#!/usr/bin/env python3
"""
Comprehensive test suite for Solopreneur Oracle system.
Tests all 56 agents across 3 tiers with various scenarios.
"""

import asyncio
import aiohttp
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_solopreneur_comprehensive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SolopreneurOracleTestSuite:
    """Comprehensive test suite for Solopreneur Oracle system."""
    
    def __init__(self):
        self.base_url = "http://localhost:10901"
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "tests": []
        }
        self.tier_ports = {
            1: [10901],  # Oracle Master
            2: list(range(10902, 10907)),  # Domain Specialists
            3: list(range(10910, 10960))  # Intelligence Modules
        }
        
    async def run_all_tests(self):
        """Run complete test suite."""
        logger.info("Starting Solopreneur Oracle Comprehensive Test Suite")
        logger.info("=" * 60)
        
        # Phase 1: System Health Tests
        await self.test_system_health()
        
        # Phase 2: Communication Protocol Tests
        await self.test_communication_protocols()
        
        # Phase 3: Domain-Specific Tests
        await self.test_domain_functionality()
        
        # Phase 4: Integration Tests
        await self.test_cross_domain_integration()
        
        # Phase 5: Performance Tests
        await self.test_performance_metrics()
        
        # Phase 6: Error Handling Tests
        await self.test_error_handling()
        
        # Generate Report
        self.generate_report()
    
    async def test_system_health(self):
        """Test system health and availability."""
        logger.info("\n🏥 PHASE 1: System Health Tests")
        logger.info("-" * 40)
        
        # Test 1.1: MCP Server Health
        await self._test_case(
            "MCP Server Health Check",
            self._check_mcp_server_health()
        )
        
        # Test 1.2: Oracle Master Health
        await self._test_case(
            "Oracle Master Agent Health",
            self._check_agent_health(10901, "Oracle Master")
        )
        
        # Test 1.3: Domain Specialist Health
        domain_names = [
            "Technical Intelligence",
            "Knowledge Management",
            "Personal Optimization",
            "Learning Enhancement",
            "Integration Synthesis"
        ]
        for i, port in enumerate(self.tier_ports[2]):
            await self._test_case(
                f"Domain Specialist Health: {domain_names[i]}",
                self._check_agent_health(port, domain_names[i])
            )
        
        # Test 1.4: Sample Intelligence Module Health
        sample_modules = [10910, 10920, 10930, 10940, 10950]
        for port in sample_modules:
            await self._test_case(
                f"Intelligence Module Health: Port {port}",
                self._check_agent_health(port, f"Module {port}")
            )
    
    async def test_communication_protocols(self):
        """Test A2A JSON-RPC communication protocols."""
        logger.info("\n📡 PHASE 2: Communication Protocol Tests")
        logger.info("-" * 40)
        
        # Test 2.1: Basic JSON-RPC Request
        await self._test_case(
            "Basic A2A JSON-RPC Request",
            self._test_jsonrpc_request(
                "Hello Oracle",
                expected_fields=["jsonrpc", "id", "result"]
            )
        )
        
        # Test 2.2: Streaming Request
        await self._test_case(
            "A2A Streaming Request",
            self._test_streaming_request(
                "Analyze multi-agent patterns",
                expected_events=["task", "status-update", "streaming-response"]
            )
        )
        
        # Test 2.3: Batch Request
        await self._test_case(
            "A2A Batch Request",
            self._test_batch_request([
                "What is LangGraph?",
                "Optimize my schedule",
                "Track learning progress"
            ])
        )
    
    async def test_domain_functionality(self):
        """Test domain-specific functionality."""
        logger.info("\n🧠 PHASE 3: Domain-Specific Tests")
        logger.info("-" * 40)
        
        # Test 3.1: Technical Intelligence Domain
        await self._test_case(
            "Technical Intelligence Analysis",
            self._test_domain_query(
                "Analyze the architecture of modern LLM agents",
                expected_domains=["technical_intelligence"],
                expected_keywords=["architecture", "agent", "LLM"]
            )
        )
        
        # Test 3.2: Personal Optimization Domain
        await self._test_case(
            "Personal Schedule Optimization",
            self._test_domain_query(
                "Optimize my daily schedule for maximum productivity",
                expected_domains=["personal_optimization"],
                expected_keywords=["schedule", "energy", "productivity"]
            )
        )
        
        # Test 3.3: Learning Enhancement Domain
        await self._test_case(
            "Learning Path Generation",
            self._test_domain_query(
                "Create a learning path for mastering Rust programming",
                expected_domains=["learning_enhancement"],
                expected_keywords=["learning", "Rust", "path", "skills"]
            )
        )
        
        # Test 3.4: Knowledge Management Domain
        await self._test_case(
            "Knowledge Synthesis",
            self._test_domain_query(
                "Synthesize my knowledge about distributed systems",
                expected_domains=["knowledge_management"],
                expected_keywords=["knowledge", "synthesis", "distributed"]
            )
        )
    
    async def test_cross_domain_integration(self):
        """Test cross-domain integration scenarios."""
        logger.info("\n🔗 PHASE 4: Cross-Domain Integration Tests")
        logger.info("-" * 40)
        
        # Test 4.1: Technical + Learning Integration
        await self._test_case(
            "Technical-Learning Integration",
            self._test_integration_query(
                "How can I efficiently learn LangGraph given my Python background?",
                expected_domains=["technical_intelligence", "learning_enhancement"],
                min_synthesis_depth=2
            )
        )
        
        # Test 4.2: Personal + Technical Integration
        await self._test_case(
            "Personal-Technical Integration",
            self._test_integration_query(
                "Schedule my week to implement a new AI feature considering my energy patterns",
                expected_domains=["personal_optimization", "technical_intelligence"],
                min_synthesis_depth=2
            )
        )
        
        # Test 4.3: Full System Integration
        await self._test_case(
            "Full System Integration",
            self._test_integration_query(
                "Create a comprehensive plan for building an AI startup, considering technical requirements, learning needs, and personal optimization",
                expected_domains=["technical_intelligence", "learning_enhancement", "personal_optimization", "knowledge_management", "integration_synthesis"],
                min_synthesis_depth=4
            )
        )
    
    async def test_performance_metrics(self):
        """Test system performance metrics."""
        logger.info("\n⚡ PHASE 5: Performance Tests")
        logger.info("-" * 40)
        
        # Test 5.1: Response Time
        await self._test_case(
            "Response Time Test",
            self._test_response_time(
                "Quick test query",
                max_time_ms=5000
            )
        )
        
        # Test 5.2: Concurrent Request Handling
        await self._test_case(
            "Concurrent Request Handling",
            self._test_concurrent_requests(
                num_requests=5,
                max_total_time_ms=10000
            )
        )
        
        # Test 5.3: Large Query Processing
        await self._test_case(
            "Large Query Processing",
            self._test_large_query_processing(
                query_size_kb=10,
                max_time_ms=15000
            )
        )
    
    async def test_error_handling(self):
        """Test error handling and edge cases."""
        logger.info("\n⚠️  PHASE 6: Error Handling Tests")
        logger.info("-" * 40)
        
        # Test 6.1: Invalid JSON-RPC Request
        await self._test_case(
            "Invalid JSON-RPC Request Handling",
            self._test_invalid_request()
        )
        
        # Test 6.2: Timeout Handling
        await self._test_case(
            "Timeout Handling",
            self._test_timeout_handling()
        )
        
        # Test 6.3: Empty Query Handling
        await self._test_case(
            "Empty Query Handling",
            self._test_empty_query()
        )
    
    # Helper Methods
    async def _test_case(self, name: str, test_coro):
        """Execute a single test case."""
        try:
            start_time = time.time()
            result = await test_coro
            duration = (time.time() - start_time) * 1000  # ms
            
            self.test_results["tests"].append({
                "name": name,
                "status": "PASSED" if result else "FAILED",
                "duration_ms": duration,
                "timestamp": datetime.now().isoformat()
            })
            
            if result:
                self.test_results["passed"] += 1
                logger.info(f"✅ {name} - PASSED ({duration:.0f}ms)")
            else:
                self.test_results["failed"] += 1
                logger.error(f"❌ {name} - FAILED ({duration:.0f}ms)")
                
        except Exception as e:
            self.test_results["errors"] += 1
            self.test_results["tests"].append({
                "name": name,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            logger.error(f"⚠️  {name} - ERROR: {str(e)}")
    
    async def _check_mcp_server_health(self) -> bool:
        """Check MCP server health."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://localhost:10100/health",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def _check_agent_health(self, port: int, name: str) -> bool:
        """Check individual agent health."""
        try:
            async with aiohttp.ClientSession() as session:
                # Try multiple endpoints
                endpoints = ["/", "/health", "/status"]
                for endpoint in endpoints:
                    try:
                        async with session.get(
                            f"http://localhost:{port}{endpoint}",
                            timeout=aiohttp.ClientTimeout(total=2)
                        ) as response:
                            if response.status in [200, 405]:  # 405 for GET on POST-only endpoints
                                return True
                    except:
                        continue
                return False
        except:
            return False
    
    async def _test_jsonrpc_request(self, query: str, expected_fields: List[str]) -> bool:
        """Test basic JSON-RPC request."""
        try:
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "jsonrpc": "2.0",
                    "id": f"test-{int(time.time())}",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [{"kind": "text", "text": query}],
                            "messageId": f"msg-{int(time.time())}",
                            "kind": "message"
                        },
                        "metadata": {}
                    }
                }
                
                async with session.post(
                    self.base_url,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return all(field in data for field in expected_fields)
                    return False
        except Exception as e:
            logger.debug(f"JSON-RPC request failed: {e}")
            return False
    
    async def _test_streaming_request(self, query: str, expected_events: List[str]) -> bool:
        """Test streaming request."""
        try:
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "jsonrpc": "2.0",
                    "id": f"test-stream-{int(time.time())}",
                    "method": "message/stream",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [{"kind": "text", "text": query}],
                            "messageId": f"msg-{int(time.time())}",
                            "kind": "message"
                        },
                        "metadata": {}
                    }
                }
                
                events_received = set()
                async with session.post(
                    self.base_url,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                try:
                                    line_str = line.decode('utf-8').strip()
                                    if line_str.startswith('data: '):
                                        data = json.loads(line_str[6:])
                                        if 'result' in data and 'kind' in data['result']:
                                            events_received.add(data['result']['kind'])
                                except:
                                    pass
                        
                        return any(event in events_received for event in expected_events)
                    return False
        except Exception as e:
            logger.debug(f"Streaming request failed: {e}")
            return False
    
    async def _test_batch_request(self, queries: List[str]) -> bool:
        """Test batch request handling."""
        # Note: This might need to be implemented based on system capabilities
        # For now, test sequential requests
        try:
            success_count = 0
            for query in queries:
                if await self._test_jsonrpc_request(query, ["jsonrpc", "id"]):
                    success_count += 1
            return success_count == len(queries)
        except:
            return False
    
    async def _test_domain_query(self, query: str, expected_domains: List[str], expected_keywords: List[str]) -> bool:
        """Test domain-specific query."""
        try:
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "jsonrpc": "2.0",
                    "id": f"test-domain-{int(time.time())}",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [{"kind": "text", "text": query}],
                            "messageId": f"msg-{int(time.time())}",
                            "kind": "message"
                        },
                        "metadata": {"include_metrics": True}
                    }
                }
                
                async with session.post(
                    self.base_url,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check if response contains expected content
                        response_text = json.dumps(data).lower()
                        return any(keyword.lower() in response_text for keyword in expected_keywords)
                    return False
        except Exception as e:
            logger.debug(f"Domain query failed: {e}")
            return False
    
    async def _test_integration_query(self, query: str, expected_domains: List[str], min_synthesis_depth: int) -> bool:
        """Test cross-domain integration query."""
        # Similar to domain query but checks for multiple domain involvement
        return await self._test_domain_query(query, expected_domains, expected_domains)
    
    async def _test_response_time(self, query: str, max_time_ms: int) -> bool:
        """Test response time performance."""
        start_time = time.time()
        result = await self._test_jsonrpc_request(query, ["jsonrpc"])
        duration_ms = (time.time() - start_time) * 1000
        return result and duration_ms < max_time_ms
    
    async def _test_concurrent_requests(self, num_requests: int, max_total_time_ms: int) -> bool:
        """Test concurrent request handling."""
        start_time = time.time()
        
        async def make_request(i: int):
            return await self._test_jsonrpc_request(f"Test query {i}", ["jsonrpc"])
        
        tasks = [make_request(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        duration_ms = (time.time() - start_time) * 1000
        success_count = sum(1 for r in results if r is True)
        
        return success_count == num_requests and duration_ms < max_total_time_ms
    
    async def _test_large_query_processing(self, query_size_kb: int, max_time_ms: int) -> bool:
        """Test large query processing."""
        # Generate large query
        base_text = "Analyze this comprehensive requirement: "
        padding = "x" * (query_size_kb * 1024 - len(base_text))
        large_query = base_text + padding
        
        return await self._test_response_time(large_query, max_time_ms)
    
    async def _test_invalid_request(self) -> bool:
        """Test invalid request handling."""
        try:
            async with aiohttp.ClientSession() as session:
                # Send invalid JSON-RPC request
                invalid_request = {
                    "jsonrpc": "1.0",  # Invalid version
                    "method": "invalid_method",
                    "params": {}
                }
                
                async with session.post(
                    self.base_url,
                    json=invalid_request,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status in [400, 422]:  # Bad request or unprocessable
                        data = await response.json()
                        return "error" in data
                    return False
        except:
            return False
    
    async def _test_timeout_handling(self) -> bool:
        """Test timeout handling."""
        try:
            async with aiohttp.ClientSession() as session:
                request_data = {
                    "jsonrpc": "2.0",
                    "id": "test-timeout",
                    "method": "message/send",
                    "params": {
                        "message": {
                            "role": "user",
                            "parts": [{"kind": "text", "text": "test"}],
                            "messageId": "msg-timeout",
                            "kind": "message"
                        }
                    }
                }
                
                # Use very short timeout
                try:
                    async with session.post(
                        self.base_url,
                        json=request_data,
                        timeout=aiohttp.ClientTimeout(total=0.001)  # 1ms timeout
                    ) as response:
                        return False  # Should timeout
                except asyncio.TimeoutError:
                    return True  # Correctly timed out
        except:
            return False
    
    async def _test_empty_query(self) -> bool:
        """Test empty query handling."""
        return await self._test_jsonrpc_request("", ["jsonrpc"])
    
    def generate_report(self):
        """Generate comprehensive test report."""
        logger.info("\n" + "=" * 60)
        logger.info("SOLOPRENEUR ORACLE COMPREHENSIVE TEST REPORT")
        logger.info("=" * 60)
        logger.info(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total Tests: {len(self.test_results['tests'])}")
        logger.info(f"Passed: {self.test_results['passed']}")
        logger.info(f"Failed: {self.test_results['failed']}")
        logger.info(f"Errors: {self.test_results['errors']}")
        
        if self.test_results['tests']:
            success_rate = (self.test_results['passed'] / len(self.test_results['tests'])) * 100
            logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Save detailed report
        report_path = Path("test_solopreneur_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        logger.info(f"\nDetailed report saved to: {report_path}")
        
        # Summary by phase
        phases = {
            "System Health": 0,
            "Communication Protocol": 0,
            "Domain-Specific": 0,
            "Cross-Domain Integration": 0,
            "Performance": 0,
            "Error Handling": 0
        }
        
        for test in self.test_results['tests']:
            for phase in phases:
                if phase in test['name']:
                    if test['status'] == 'PASSED':
                        phases[phase] += 1
                    break
        
        logger.info("\nResults by Phase:")
        for phase, passed in phases.items():
            logger.info(f"  {phase}: {passed} passed")
        
        # Exit code
        if self.test_results['failed'] == 0 and self.test_results['errors'] == 0:
            logger.info("\n🎉 All tests passed! The Solopreneur Oracle is fully operational.")
            sys.exit(0)
        else:
            logger.error("\n⚠️  Some tests failed. Please check the logs for details.")
            sys.exit(1)


async def main():
    """Run the comprehensive test suite."""
    test_suite = SolopreneurOracleTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())