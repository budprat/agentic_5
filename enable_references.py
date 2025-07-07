#!/usr/bin/env python3
"""Enable/disable reference integration for Nexus Oracle."""

import json
import os
import sys

def enable_references():
    """Enable external reference integration."""
    config_path = "oracle_config.json"
    
    config = {
        "reference_integration": {
            "enabled": True,
            "sources": {
                "arxiv": True,
                "semantic_scholar": True,
                "mcp_scholarly": False,  # Requires Docker setup
                "web_search": False     # Rate limited
            },
            "limits": {
                "max_papers_per_source": 10,
                "max_total_papers": 25,
                "request_timeout": 30
            },
            "quality_thresholds": {
                "min_citations": 2,
                "peer_review_required": False,
                "max_age_years": 10,
                "min_quality_score": 0.3
            }
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Reference integration enabled in {config_path}")
    print("📋 Configuration:")
    print(json.dumps(config, indent=2))
    
    # Set environment variables for API keys (if needed)
    print("\n🔑 API Configuration:")
    print("- ArXiv: No API key required")
    print("- Semantic Scholar: No API key required (rate limited)")
    print("- For higher limits, set SEMANTIC_SCHOLAR_API_KEY environment variable")
    print("\n📚 MCP Scholarly Setup:")
    print("- Currently disabled (requires Docker)")
    print("- To enable: Install Docker and run setup instructions")

def disable_references():
    """Disable external reference integration."""
    config_path = "oracle_config.json"
    
    config = {
        "reference_integration": {
            "enabled": False
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"❌ Reference integration disabled in {config_path}")

def show_status():
    """Show current reference integration status."""
    config_path = "oracle_config.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        enabled = config.get("reference_integration", {}).get("enabled", False)
        print(f"📊 Reference Integration Status: {'✅ ENABLED' if enabled else '❌ DISABLED'}")
        
        if enabled:
            sources = config.get("reference_integration", {}).get("sources", {})
            print(f"📚 Active Sources:")
            for source, active in sources.items():
                status = "✅" if active else "❌"
                print(f"   {status} {source}")
            
            limits = config.get("reference_integration", {}).get("limits", {})
            print(f"⚙️  Limits:")
            print(f"   Max papers per source: {limits.get('max_papers_per_source', 'N/A')}")
            print(f"   Max total papers: {limits.get('max_total_papers', 'N/A')}")
            print(f"   Request timeout: {limits.get('request_timeout', 'N/A')}s")
    else:
        print(f"📊 Reference Integration Status: ❌ NOT CONFIGURED")
        print(f"   Run 'python enable_references.py' to enable")

def show_help():
    """Show help information."""
    print("🔧 Oracle Reference Integration Manager")
    print("=" * 40)
    print("Commands:")
    print("  python enable_references.py        - Enable reference integration")
    print("  python enable_references.py disable - Disable reference integration")
    print("  python enable_references.py status  - Show current status")
    print("  python enable_references.py help    - Show this help")
    print("\nSource Configuration:")
    print("  arxiv: ArXiv academic papers (computer science, physics, math)")
    print("  semantic_scholar: Cross-disciplinary academic database")
    print("  mcp_scholarly: Docker-based scholarly search (advanced setup)")
    print("  web_search: Real-time web search (rate limited)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "disable":
            disable_references()
        elif command == "status":
            show_status()
        elif command == "help":
            show_help()
        else:
            print(f"Unknown command: {command}")
            show_help()
    else:
        enable_references()