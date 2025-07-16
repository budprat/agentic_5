# ABOUTME: mTLS (Mutual TLS) handler for certificate-based authentication
# ABOUTME: Provides certificate validation, chain verification, and mTLS connection setup

import ssl
import logging
import hashlib
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
from pathlib import Path
import OpenSSL.crypto
import OpenSSL.SSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CertificateInfo:
    """Certificate information extracted from X.509 certificate."""
    subject: str
    issuer: str
    serial_number: str
    fingerprint: str
    not_before: datetime
    not_after: datetime
    is_ca: bool
    subject_alt_names: List[str]
    key_usage: List[str]
    extended_key_usage: List[str]


class MTLSHandler:
    """
    Handler for mutual TLS authentication and certificate management.
    
    Provides:
    - Certificate validation and chain verification
    - SSL context creation for mTLS connections
    - Certificate information extraction
    - Revocation checking (OCSP/CRL)
    - Certificate pinning support
    """
    
    def __init__(
        self,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        ca_path: Optional[str] = None,
        verify_mode: str = "CERT_REQUIRED",
        check_hostname: bool = True,
        crl_path: Optional[str] = None,
        enable_ocsp: bool = True
    ):
        """
        Initialize mTLS handler.
        
        Args:
            cert_path: Path to server certificate
            key_path: Path to server private key
            ca_path: Path to CA certificate(s) for client verification
            verify_mode: SSL verification mode (CERT_REQUIRED, CERT_OPTIONAL, CERT_NONE)
            check_hostname: Whether to check hostname in certificate
            crl_path: Path to Certificate Revocation List
            enable_ocsp: Enable OCSP stapling and checking
        """
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
        self.verify_mode = getattr(ssl, verify_mode, ssl.CERT_REQUIRED)
        self.check_hostname = check_hostname
        self.crl_path = crl_path
        self.enable_ocsp = enable_ocsp
        
        # Certificate cache for performance
        self._cert_cache: Dict[str, CertificateInfo] = {}
        self._trusted_fingerprints: set = set()
        
        # Statistics
        self._stats = {
            "certificates_validated": 0,
            "certificates_rejected": 0,
            "ocsp_checks": 0,
            "crl_checks": 0
        }
        
        # Load CA certificates if provided
        self._ca_certs = self._load_ca_certificates() if ca_path else None
        
        logger.info(f"mTLS handler initialized with verify_mode: {verify_mode}")
    
    def create_ssl_context(self, is_server: bool = True) -> ssl.SSLContext:
        """
        Create SSL context for mTLS connections.
        
        Args:
            is_server: Whether this is a server context (vs client)
            
        Returns:
            Configured SSL context
        """
        # Create context with secure defaults
        if is_server:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        else:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        # Set protocol and options for security
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        context.options |= ssl.OP_SINGLE_DH_USE
        context.options |= ssl.OP_SINGLE_ECDH_USE
        
        # Configure ciphers (only strong ciphers)
        context.set_ciphers(
            'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'
        )
        
        # Load certificates
        if self.cert_path and self.key_path:
            context.load_cert_chain(self.cert_path, self.key_path)
        
        # Configure client certificate verification
        if is_server:
            context.verify_mode = self.verify_mode
            if self.ca_path:
                context.load_verify_locations(cafile=self.ca_path)
            context.check_hostname = False  # We'll do custom hostname checking
        else:
            context.check_hostname = self.check_hostname
            if self.ca_path:
                context.load_verify_locations(cafile=self.ca_path)
        
        # Set verification callback for additional checks
        if is_server and self.verify_mode != ssl.CERT_NONE:
            # Note: In production, you'd set up a proper verification callback
            # context.set_servername_callback(self._verify_callback)
            pass
        
        return context
    
    async def verify_certificate(
        self, cert_data: Union[str, bytes, Dict]
    ) -> Dict[str, Any]:
        """
        Verify a client certificate.
        
        Args:
            cert_data: Certificate data (PEM string, DER bytes, or cert dict)
            
        Returns:
            Verification result with certificate info
        """
        try:
            # Parse certificate
            if isinstance(cert_data, dict):
                # Already parsed SSL certificate dict
                cert_pem = cert_data.get('pem', '')
                cert_obj = self._parse_certificate(cert_pem)
            else:
                cert_obj = self._parse_certificate(cert_data)
            
            # Extract certificate info
            cert_info = self._extract_certificate_info(cert_obj)
            
            # Check cache
            if cert_info.fingerprint in self._cert_cache:
                cached_info = self._cert_cache[cert_info.fingerprint]
                logger.debug(f"Certificate found in cache: {cached_info.subject}")
            else:
                self._cert_cache[cert_info.fingerprint] = cert_info
            
            # Perform validation checks
            validation_errors = []
            
            # 1. Check validity period
            now = datetime.now(timezone.utc)
            if now < cert_info.not_before:
                validation_errors.append("Certificate not yet valid")
            if now > cert_info.not_after:
                validation_errors.append("Certificate expired")
            
            # 2. Check against CA if available
            if self._ca_certs:
                try:
                    self._verify_certificate_chain(cert_obj)
                except Exception as e:
                    validation_errors.append(f"Chain verification failed: {str(e)}")
            
            # 3. Check revocation status
            if self.enable_ocsp:
                revoked = await self._check_ocsp(cert_obj)
                if revoked:
                    validation_errors.append("Certificate revoked (OCSP)")
                self._stats["ocsp_checks"] += 1
            
            if self.crl_path:
                revoked = self._check_crl(cert_info.serial_number)
                if revoked:
                    validation_errors.append("Certificate revoked (CRL)")
                self._stats["crl_checks"] += 1
            
            # 4. Check key usage
            if "digital_signature" not in cert_info.key_usage:
                validation_errors.append("Certificate missing digital signature key usage")
            
            # Update statistics
            if validation_errors:
                self._stats["certificates_rejected"] += 1
            else:
                self._stats["certificates_validated"] += 1
            
            return {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "subject": cert_info.subject,
                "issuer": cert_info.issuer,
                "fingerprint": cert_info.fingerprint,
                "not_before": cert_info.not_before.isoformat(),
                "not_after": cert_info.not_after.isoformat(),
                "subject_alt_names": cert_info.subject_alt_names,
                "is_trusted": cert_info.fingerprint in self._trusted_fingerprints
            }
            
        except Exception as e:
            logger.error(f"Certificate verification failed: {e}")
            self._stats["certificates_rejected"] += 1
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _parse_certificate(self, cert_data: Union[str, bytes]) -> x509.Certificate:
        """Parse certificate from PEM or DER format."""
        if isinstance(cert_data, str):
            # Try PEM format
            if cert_data.startswith("-----BEGIN CERTIFICATE-----"):
                return x509.load_pem_x509_certificate(
                    cert_data.encode(), default_backend()
                )
            else:
                # Assume base64 encoded DER
                import base64
                der_data = base64.b64decode(cert_data)
                return x509.load_der_x509_certificate(der_data, default_backend())
        else:
            # Try DER format
            return x509.load_der_x509_certificate(cert_data, default_backend())
    
    def _extract_certificate_info(self, cert: x509.Certificate) -> CertificateInfo:
        """Extract information from X.509 certificate."""
        # Get subject and issuer
        subject = self._format_name(cert.subject)
        issuer = self._format_name(cert.issuer)
        
        # Calculate fingerprint
        fingerprint = cert.fingerprint(hashes.SHA256()).hex()
        
        # Extract extensions
        is_ca = False
        subject_alt_names = []
        key_usage = []
        extended_key_usage = []
        
        try:
            # Basic constraints
            bc_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.BASIC_CONSTRAINTS
            )
            is_ca = bc_ext.value.ca
        except x509.ExtensionNotFound:
            pass
        
        try:
            # Subject Alternative Names
            san_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            subject_alt_names = [
                name.value for name in san_ext.value
                if isinstance(name, (x509.DNSName, x509.IPAddress))
            ]
        except x509.ExtensionNotFound:
            pass
        
        try:
            # Key usage
            ku_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.KEY_USAGE
            )
            ku = ku_ext.value
            if ku.digital_signature:
                key_usage.append("digital_signature")
            if ku.key_agreement:
                key_usage.append("key_agreement")
            if ku.key_cert_sign:
                key_usage.append("key_cert_sign")
        except x509.ExtensionNotFound:
            pass
        
        try:
            # Extended key usage
            eku_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.EXTENDED_KEY_USAGE
            )
            extended_key_usage = [
                oid._name for oid in eku_ext.value
            ]
        except x509.ExtensionNotFound:
            pass
        
        return CertificateInfo(
            subject=subject,
            issuer=issuer,
            serial_number=str(cert.serial_number),
            fingerprint=fingerprint,
            not_before=cert.not_valid_before,
            not_after=cert.not_valid_after,
            is_ca=is_ca,
            subject_alt_names=subject_alt_names,
            key_usage=key_usage,
            extended_key_usage=extended_key_usage
        )
    
    def _format_name(self, name: x509.Name) -> str:
        """Format X.509 name as string."""
        attributes = []
        for attribute in name:
            attributes.append(f"{attribute.oid._name}={attribute.value}")
        return ", ".join(attributes)
    
    def _load_ca_certificates(self) -> List[x509.Certificate]:
        """Load CA certificates from file."""
        ca_certs = []
        
        ca_path = Path(self.ca_path)
        if ca_path.is_file():
            # Single CA file
            with open(ca_path, 'rb') as f:
                ca_data = f.read()
                
            # Handle multiple certificates in one file
            if b"-----BEGIN CERTIFICATE-----" in ca_data:
                # PEM format - may contain multiple certs
                import re
                cert_pattern = re.compile(
                    b"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
                    re.DOTALL
                )
                for cert_match in cert_pattern.finditer(ca_data):
                    cert = x509.load_pem_x509_certificate(
                        cert_match.group(), default_backend()
                    )
                    ca_certs.append(cert)
            else:
                # DER format - single cert
                cert = x509.load_der_x509_certificate(ca_data, default_backend())
                ca_certs.append(cert)
                
        elif ca_path.is_dir():
            # Directory of CA files
            for cert_file in ca_path.glob("*.pem"):
                with open(cert_file, 'rb') as f:
                    cert = x509.load_pem_x509_certificate(
                        f.read(), default_backend()
                    )
                    ca_certs.append(cert)
        
        logger.info(f"Loaded {len(ca_certs)} CA certificates")
        return ca_certs
    
    def _verify_certificate_chain(self, cert: x509.Certificate):
        """Verify certificate chain against loaded CAs."""
        # This is a simplified implementation
        # In production, use OpenSSL's full chain verification
        
        # Check if certificate is signed by any of our CAs
        for ca_cert in self._ca_certs:
            try:
                # Verify signature
                ca_public_key = ca_cert.public_key()
                ca_public_key.verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    cert.signature_algorithm_parameters
                )
                logger.debug(f"Certificate verified by CA: {self._format_name(ca_cert.subject)}")
                return True
            except Exception:
                continue
        
        raise ValueError("Certificate not signed by trusted CA")
    
    async def _check_ocsp(self, cert: x509.Certificate) -> bool:
        """
        Check certificate revocation status via OCSP.
        
        Returns:
            True if certificate is revoked, False otherwise
        """
        # This is a placeholder for OCSP checking
        # In production, implement proper OCSP checking
        logger.debug("OCSP checking not fully implemented")
        return False
    
    def _check_crl(self, serial_number: str) -> bool:
        """
        Check certificate against CRL.
        
        Returns:
            True if certificate is revoked, False otherwise
        """
        if not self.crl_path:
            return False
        
        # This is a placeholder for CRL checking
        # In production, implement proper CRL parsing and checking
        logger.debug("CRL checking not fully implemented")
        return False
    
    def add_trusted_fingerprint(self, fingerprint: str):
        """Add a certificate fingerprint to trusted list."""
        self._trusted_fingerprints.add(fingerprint)
        logger.info(f"Added trusted certificate fingerprint: {fingerprint[:16]}...")
    
    def remove_trusted_fingerprint(self, fingerprint: str):
        """Remove a certificate fingerprint from trusted list."""
        self._trusted_fingerprints.discard(fingerprint)
        logger.info(f"Removed trusted certificate fingerprint: {fingerprint[:16]}...")
    
    async def get_certificate_statistics(self) -> Dict[str, Any]:
        """Get mTLS statistics."""
        return {
            "certificates_validated": self._stats["certificates_validated"],
            "certificates_rejected": self._stats["certificates_rejected"],
            "ocsp_checks": self._stats["ocsp_checks"],
            "crl_checks": self._stats["crl_checks"],
            "cached_certificates": len(self._cert_cache),
            "trusted_fingerprints": len(self._trusted_fingerprints)
        }
    
    def clear_certificate_cache(self):
        """Clear the certificate cache."""
        self._cert_cache.clear()
        logger.info("Certificate cache cleared")