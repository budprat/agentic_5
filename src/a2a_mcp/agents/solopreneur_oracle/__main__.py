"""ABOUTME: Main entry point for solopreneur oracle system with AWIE integration.
ABOUTME: This launches the complete 76-agent ecosystem including the revolutionary AWIE domain oracle."""

# type: ignore

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from solopreneur_oracle_agent_adk import SolopreneurOracleAgent
from autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
from agent_registry import SOLOPRENEUR_AGENTS, get_agent_count

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def initialize_awie_system():
    """Initialize the complete AWIE-enhanced solopreneur system."""
    print("🧠 AUTONOMOUS WORKFLOW INTELLIGENCE ENGINE")
    print("🚀 INITIALIZING REVOLUTIONARY PRODUCTIVITY SYSTEM")
    print("=" * 60)
    
    try:
        # Initialize main solopreneur oracle
        print("1. Initializing Solopreneur Oracle Master...")
        master_oracle = SolopreneurOracleAgent()
        
        # Initialize AWIE Oracle
        print("2. Initializing AWIE Oracle (AI Chief of Staff)...")
        awie_oracle = AutonomousWorkflowIntelligenceOracle()
        
        # Get agent statistics
        agent_stats = get_agent_count()
        print(f"3. System Ready - {agent_stats['total']} agents available:")
        print(f"   • Tier 1 (Master): {agent_stats.get('tier_1', 0)} agents")
        print(f"   • Tier 2 (Domain Specialists): {agent_stats.get('tier_2', 0)} agents") 
        print(f"   • Tier 3 (Intelligence Modules): {agent_stats.get('tier_3', 0)} agents")
        
        print("\n✅ AWIE SYSTEM ACTIVE")
        print("🎯 Ready for revolutionary productivity experience")
        
        return {
            "master_oracle": master_oracle,
            "awie_oracle": awie_oracle,
            "status": "ready",
            "agent_count": agent_stats['total']
        }
        
    except Exception as e:
        logger.error(f"AWIE system initialization failed: {e}")
        print(f"❌ Initialization failed: {e}")
        return {"status": "failed", "error": str(e)}

async def test_awie_capabilities():
    """Test AWIE capabilities with real scenarios."""
    print("\n🔬 TESTING AWIE CAPABILITIES")
    print("-" * 40)
    
    # Initialize system
    system = await initialize_awie_system()
    if system["status"] != "ready":
        print("❌ Cannot test - system not ready")
        return
    
    awie_oracle = system["awie_oracle"]
    
    # Test scenarios
    test_scenarios = [
        "research RAG techniques for my current project",
        "create content about my AI experiments", 
        "organize my learning materials and plan next steps"
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Test {i}: '{scenario}'")
        print("Processing with AWIE...")
        
        try:
            response = await awie_oracle._execute_agent_logic(
                scenario, f"test_context_{i}", f"task_{i}"
            )
            
            content = response.get("content", "Error in processing")
            # Show abbreviated response for console
            if len(content) > 200:
                abbreviated = content[:200] + "...\n[Full enhanced workflow generated]"
            else:
                abbreviated = content
                
            print(f"✨ AWIE Enhanced: {abbreviated}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 AWIE TESTING COMPLETE")
    print("✅ Revolutionary workflow intelligence active")

async def start_interactive_awie():
    """Start interactive AWIE session."""
    print("\n💬 INTERACTIVE AWIE SESSION")
    print("Type your tasks and watch AWIE transform them!")
    print("(Type 'quit' to exit)")
    print("-" * 50)
    
    # Initialize system
    system = await initialize_awie_system()
    if system["status"] != "ready":
        print("❌ Cannot start interactive mode - system not ready")
        return
    
    awie_oracle = system["awie_oracle"]
    
    while True:
        try:
            user_input = input("\n🎯 NU: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 AWIE session ended")
                break
            
            if not user_input:
                continue
            
            print("🧠 AWIE processing...")
            
            response = await awie_oracle._execute_agent_logic(
                user_input, "interactive_session", f"task_{hash(user_input)}"
            )
            
            content = response.get("content", "Error in processing")
            print(f"\n✨ AWIE: {content}")
            
        except KeyboardInterrupt:
            print("\n👋 AWIE session ended")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main entry point for AWIE system."""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "test":
            await test_awie_capabilities()
        elif mode == "interactive":
            await start_interactive_awie()
        elif mode == "init":
            await initialize_awie_system()
        else:
            print("Usage: python __main__.py [test|interactive|init]")
    else:
        # Default: run interactive mode
        await start_interactive_awie()

if __name__ == "__main__":
    asyncio.run(main())