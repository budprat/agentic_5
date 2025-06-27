#!/usr/bin/env python3
"""Generate .mcp.json configuration from environment variables."""

import os
import json
from dotenv import load_dotenv

def generate_mcp_config():
    """Generate .mcp.json from environment variables."""
    load_dotenv()
    
    config = {
        "mcpServers": {
            "supabase": {
                "type": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "@supabase/mcp-server-supabase@latest",
                    "--access-token",
                    os.getenv('SUPABASE_MCP_ACCESS_TOKEN', 'YOUR_SUPABASE_MCP_ACCESS_TOKEN'),
                    "--project-ref",
                    os.getenv('SUPABASE_MCP_PROJECT_REF', 'YOUR_SUPABASE_MCP_PROJECT_REF')
                ],
                "env": {}
            },
            "snowflake": {
                "command": "python",
                "args": [
                    "/home/coder/project/a2a-mcp/snowflake_mcp.py"
                ]
            },
            "brightdata": {
                "type": "stdio",
                "command": "npx",
                "args": [
                    "@brightdata/mcp"
                ],
                "env": {
                    "API_TOKEN": os.getenv('BRIGHTDATA_API_TOKEN', 'YOUR_BRIGHTDATA_API_TOKEN'),
                    "WEB_UNLOCKER_ZONE": os.getenv('BRIGHTDATA_ZONE', 'mcp_unlocker')
                }
            },
            "brave": {
                "type": "stdio",
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-brave-search"
                ],
                "env": {
                    "BRAVE_API_KEY": os.getenv('BRAVE_API_KEY', 'YOUR_BRAVE_API_KEY')
                }
            },
            "puppeteer": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
            },
            "context7": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@upstash/context7-mcp"]
            },
            "upstash": {
                "type": "stdio",
                "command": "npx",
                "args": [
                    "-y", 
                    "@upstash/mcp-server", 
                    "run", 
                    os.getenv('UPSTASH_EMAIL', 'YOUR_UPSTASH_EMAIL'), 
                    os.getenv('UPSTASH_PROJECT_ID', 'YOUR_UPSTASH_PROJECT_ID')
                ]
            },
            "firecrawl": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "firecrawl-mcp"],
                "env": {
                    "FIRECRAWL_API_KEY": os.getenv('FIRECRAWL_API_KEY', 'YOUR_FIRECRAWL_API_KEY'),
                    "FIRECRAWL_RETRY_MAX_ATTEMPTS": "5",
                    "FIRECRAWL_RETRY_INITIAL_DELAY": "2000",
                    "FIRECRAWL_RETRY_MAX_DELAY": "30000",
                    "FIRECRAWL_RETRY_BACKOFF_FACTOR": "3",
                    "FIRECRAWL_CREDIT_WARNING_THRESHOLD": "2000",
                    "FIRECRAWL_CREDIT_CRITICAL_THRESHOLD": "500"
                }
            },
            "notionAI": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@notionhq/notion-mcp-server"],
                "env": {
                    "OPENAPI_MCP_HEADERS": json.dumps({
                        "Authorization": f"Bearer {os.getenv('NOTION_MCP_TOKEN', 'YOUR_NOTION_MCP_TOKEN')}",
                        "Notion-Version": "2022-06-28"
                    })
                }
            }
        }
    }
    
    # Write the configuration
    with open('.mcp.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Generated .mcp.json from environment variables")
    print("⚠️  Make sure all required environment variables are set in .env")
    print("📋 Required variables:")
    required_vars = [
        'SUPABASE_MCP_ACCESS_TOKEN',
        'SUPABASE_MCP_PROJECT_REF',
        'BRIGHTDATA_API_TOKEN',
        'BRAVE_API_KEY',
        'UPSTASH_EMAIL',
        'UPSTASH_PROJECT_ID',
        'FIRECRAWL_API_KEY',
        'NOTION_MCP_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
    else:
        print("\n✅ All required environment variables are set!")

if __name__ == "__main__":
    generate_mcp_config()