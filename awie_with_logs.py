#!/usr/bin/env python3
"""ABOUTME: AWIE demonstration with detailed logging - shows complete execution flow and SERP integration.
ABOUTME: This script enables comprehensive logging to see how AWIE processes requests step by step."""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('awie_execution.log', mode='w')
    ]
)

# Enable logging for all AWIE components
loggers_to_enable = [
    'a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle',
    'a2a_mcp.agents.tier3.awie_scheduler_agent',
    'a2a_mcp.common.standardized_agent_base',
    '__main__'
]

for logger_name in loggers_to_enable:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

# Main logger
logger = logging.getLogger(__name__)

async def demonstrate_awie_with_logs(request: str):
    """Demonstrate AWIE with full logging enabled"""
    
    logger.info("="*70)
    logger.info("🧠 AWIE EXECUTION DEMONSTRATION WITH FULL LOGGING")
    logger.info("="*70)
    logger.info(f"📝 Processing request: {request}")
    logger.info("-"*50)
    
    try:
        # Import and initialize AWIE Oracle
        logger.info("🚀 Step 1: Importing AWIE Oracle...")
        from a2a_mcp.agents.solopreneur_oracle.autonomous_workflow_intelligence_oracle import AutonomousWorkflowIntelligenceOracle
        
        logger.info("🚀 Step 2: Initializing AWIE Oracle...")
        oracle = AutonomousWorkflowIntelligenceOracle()
        logger.info("✅ AWIE Oracle initialized successfully")
        
        # Generate request IDs
        import hashlib
        request_hash = hashlib.md5(request.encode()).hexdigest()[:8]
        context_id = f"demo_{request_hash}"
        task_id = f"task_{request_hash}"
        
        logger.info(f"🚀 Step 3: Processing request through Oracle...")
        logger.info(f"   Context ID: {context_id}")
        logger.info(f"   Task ID: {task_id}")
        
        # Process request through AWIE Oracle
        result = await oracle._process_manual_task_request(request, context_id, task_id)
        
        logger.info("🚀 Step 4: Processing complete, analyzing results...")
        
        if result and "content" in result:
            logger.info("✅ AWIE Oracle generated response successfully")
            logger.info(f"📊 Response length: {len(result['content'])} characters")
            
            # Log metadata if available
            if "metadata" in result:
                metadata = result["metadata"]
                logger.info("📊 Workflow Metadata:")
                logger.info(f"   Workflow ID: {metadata.get('workflow_id', 'N/A')}")
                logger.info(f"   Total Tasks: {metadata.get('total_tasks', 'N/A')}")
                logger.info(f"   SERP Optimized: {metadata.get('serp_optimized', 'N/A')}")
            
            print("\n" + "="*70)
            print("🎯 FINAL AWIE OUTPUT:")
            print("="*70)
            print(result["content"])
            print("="*70)
            
        else:
            logger.error("❌ No response generated from AWIE Oracle")
            
    except Exception as e:
        logger.error(f"❌ Error during AWIE execution: {e}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")

async def main():
    """Main function with example requests"""
    
    # Example requests to demonstrate
    test_requests = [
        "research AI automation trends and create content strategy",
        "organize my development workflow with market intelligence",
        "schedule content creation about RAG implementation"
    ]
    
    print("🧠 AWIE Logging Demonstration")
    print("🎯 This will show complete execution flow with detailed logs")
    print("📝 Logs are saved to 'awie_execution.log' file")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Command line request
        request = " ".join(sys.argv[1:])
        await demonstrate_awie_with_logs(request)
    else:
        # Interactive selection
        print("Choose a request to demonstrate:")
        for i, req in enumerate(test_requests, 1):
            print(f"{i}. {req}")
        print("4. Custom request")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice in ["1", "2", "3"]:
                selected_request = test_requests[int(choice) - 1]
                await demonstrate_awie_with_logs(selected_request)
            elif choice == "4":
                custom = input("Enter your request: ").strip()
                if custom:
                    await demonstrate_awie_with_logs(custom)
                else:
                    print("⚠️ No request entered")
            else:
                print("⚠️ Invalid choice")
                
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Demonstration ended")
    
    print(f"\n📝 Complete execution log saved to: awie_execution.log")
    print("🔍 You can review the detailed execution flow in the log file")

if __name__ == "__main__":
    asyncio.run(main())