#\!/usr/bin/env python3
"""ABOUTME: Clean interactive AWIE launcher - test AWIE Oracle with custom requests and see live SERP integration.
ABOUTME: Provides simple CLI interface for testing AWIE system with real market intelligence."""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def test_awie_request(request: str):
    """Test a single AWIE request"""
    print(f"🎯 Processing: {request}")
    print("-" * 50)
    
    try:
        from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
        
        oracle = AutonomousWorkflowIntelligenceOracle()
        
        # Generate unique IDs
        import hashlib
        request_hash = hashlib.md5(request.encode()).hexdigest()[:8]
        
        result = await oracle._process_manual_task_request(
            request, f"test_{request_hash}", f"task_{request_hash}"
        )
        
        if result and "content" in result:
            print(result["content"])
            
            if "metadata" in result:
                metadata = result["metadata"]
                print(f"\n📊 Workflow ID: {metadata.get('workflow_id', 'N/A')}")
                print(f"📊 Total Tasks: {metadata.get('total_tasks', 'N/A')}")
                print(f"📊 SERP Optimized: {metadata.get('serp_optimized', 'N/A')}")
        else:
            print("❌ No response generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_examples():
    """Show example requests"""
    print("💡 Example Requests:")
    print("  • research AI automation trends and create content strategy")
    print("  • organize my development workflow with market intelligence") 
    print("  • schedule social media posting strategy")
    print("  • plan content creation for next week")
    print("  • create AI research workflow")
    print("  • optimize my coding schedule")

async def main():
    """Main interactive function"""
    print("🧠 AWIE Interactive Launcher")
    print("🎯 Revolutionary AI Chief of Staff with SERP Intelligence")
    print("=" * 60)
    
    show_examples()
    print("\n" + "=" * 60)
    
    if len(sys.argv) > 1:
        # Command line mode
        request = " ".join(sys.argv[1:])
        await test_awie_request(request)
    else:
        # Interactive mode with pre-defined tests
        print("Choose a test or enter custom request:")
        print("1. Research AI trends and create content strategy")
        print("2. Organize development workflow")
        print("3. Schedule social media strategy") 
        print("4. Custom request")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                await test_awie_request("research AI automation trends and create content strategy")
            elif choice == "2":
                await test_awie_request("organize my development workflow with market intelligence")
            elif choice == "3":
                await test_awie_request("schedule social media posting strategy")
            elif choice == "4":
                custom = input("Enter your request: ").strip()
                if custom:
                    await test_awie_request(custom)
                else:
                    print("⚠️ No request entered")
            else:
                print("⚠️ Invalid choice")
                
        except KeyboardInterrupt:
            print("\n👋 AWIE session ended")
        except EOFError:
            print("\n👋 AWIE session ended")

if __name__ == "__main__":
    asyncio.run(main())
EOF < /dev/null
