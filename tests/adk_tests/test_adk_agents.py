# ABOUTME: Test script for Google ADK agent implementations
# ABOUTME: Validates all tiers of agents and orchestration patterns

import asyncio
import logging
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get API key from environment
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    sys.exit(1)

# Set up environment
os.environ['GOOGLE_API_KEY'] = google_api_key

async def test_tier1_orchestrator():
    """Test Tier 1: ContentCreationOrchestrator"""
    logger.info("\n=== Testing Tier 1: ContentCreationOrchestrator ===")
    
    try:
        from a2a_mcp.agents.adk_examples.tier1_sequential_orchestrator import ContentCreationOrchestrator
        
        # Create orchestrator
        orchestrator = ContentCreationOrchestrator()
        await orchestrator.init_agent()
        
        # Test workflow
        request = {
            'topic': 'AI Agents and Multi-Agent Systems',
            'content_type': 'technical_blog_post',
            'target_audience': 'software developers',
            'requirements': {
                'length': 'medium',
                'style': 'technical but accessible',
                'include_examples': True
            }
        }
        
        logger.info(f"Executing content creation workflow for: {request['topic']}")
        result = await orchestrator.execute_workflow(request)
        
        logger.info(f"Workflow completed successfully!")
        logger.info(f"Result keys: {list(result.keys())}")
        logger.info(f"Execution summary: {result.get('execution_summary', 'N/A')}")
        
        return True, result
        
    except Exception as e:
        logger.error(f"Tier 1 test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)

async def test_tier2_specialists():
    """Test Tier 2: Domain Specialists"""
    logger.info("\n=== Testing Tier 2: Domain Specialists ===")
    
    results = {}
    
    # Test Financial Domain Specialist
    try:
        from a2a_mcp.agents.adk_examples.tier2_domain_specialist import FinancialDomainSpecialist
        
        specialist = FinancialDomainSpecialist()
        await specialist.init_agent()
        
        market_data = {
            'indices': {
                'SP500': 4500,
                'NASDAQ': 14200,
                'DOW': 35000
            },
            'volatility': 'moderate',
            'economic_indicators': {
                'inflation': 3.2,
                'gdp_growth': 2.8,
                'unemployment': 3.7
            },
            'sector_performance': {
                'technology': '+2.5%',
                'healthcare': '+1.2%',
                'finance': '-0.5%'
            }
        }
        
        logger.info("Testing Financial Domain Specialist")
        analysis = await specialist.analyze_market(market_data)
        
        logger.info(f"Financial analysis completed!")
        logger.info(f"Market trend: {analysis.get('market_trend', 'N/A')}")
        results['financial'] = (True, analysis)
        
    except Exception as e:
        logger.error(f"Financial specialist test failed: {str(e)}")
        results['financial'] = (False, str(e))
    
    # Test Technical Domain Specialist
    try:
        from a2a_mcp.agents.adk_examples.tier2_domain_specialist import TechnicalDomainSpecialist
        
        specialist = TechnicalDomainSpecialist()
        await specialist.init_agent()
        
        code_snippet = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Usage
for i in range(10):
    print(f"F({i}) = {calculate_fibonacci(i)}")
"""
        
        logger.info("Testing Technical Domain Specialist")
        review = await specialist.review_code(code_snippet)
        
        logger.info(f"Code review completed!")
        logger.info(f"Overall quality: {review.get('overall_quality', 'N/A')}")
        results['technical'] = (True, review)
        
    except Exception as e:
        logger.error(f"Technical specialist test failed: {str(e)}")
        results['technical'] = (False, str(e))
    
    return results

async def test_tier3_services():
    """Test Tier 3: Service Agents"""
    logger.info("\n=== Testing Tier 3: Service Agents ===")
    
    results = {}
    
    # Test Data Processing Service
    try:
        from a2a_mcp.agents.adk_examples.tier3_service_agent import DataProcessingServiceAgent
        
        service = DataProcessingServiceAgent()
        await service.init_agent()
        
        # Test data transformation
        test_data = {
            'users': [
                {'id': 1, 'name': 'Alice', 'age': 30},
                {'id': 2, 'name': 'Bob', 'age': 25},
                {'id': 3, 'name': 'Charlie', 'age': 35}
            ],
            'transactions': [
                {'user_id': 1, 'amount': 100, 'date': '2024-01-01'},
                {'user_id': 2, 'amount': 200, 'date': '2024-01-02'},
                {'user_id': 1, 'amount': 150, 'date': '2024-01-03'}
            ]
        }
        
        request = {
            'type': 'aggregate',
            'data': test_data,
            'requirements': 'Calculate total transaction amount per user'
        }
        
        logger.info("Testing Data Processing Service Agent")
        result = await service.process_data(request)
        
        logger.info(f"Data processing completed!")
        logger.info(f"Result type: {type(result)}")
        results['data_processing'] = (True, result)
        
    except Exception as e:
        logger.error(f"Data processing service test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        results['data_processing'] = (False, str(e))
    
    # Test Computation Service
    try:
        from a2a_mcp.agents.adk_examples.tier3_service_agent import ComputationServiceAgent
        
        service = ComputationServiceAgent()
        await service.init_agent()
        
        # Test financial calculation
        request = {
            'type': 'financial_calculation',
            'operation': 'compound_interest',
            'parameters': {
                'principal': 10000,
                'rate': 0.05,
                'time': 10,
                'compound_frequency': 12
            }
        }
        
        logger.info("Testing Computation Service Agent")
        result = await service.calculate(request)
        
        logger.info(f"Calculation completed!")
        logger.info(f"Result: {result}")
        results['computation'] = (True, result)
        
    except Exception as e:
        logger.error(f"Computation service test failed: {str(e)}")
        results['computation'] = (False, str(e))
    
    return results

async def test_advanced_patterns():
    """Test Advanced Orchestration Patterns"""
    logger.info("\n=== Testing Advanced Orchestration Patterns ===")
    
    try:
        from a2a_mcp.agents.adk_examples.advanced_orchestration_patterns import HybridOrchestrationPattern
        
        # Create hybrid orchestrator
        orchestrator = HybridOrchestrationPattern()
        await orchestrator.initialize()
        
        # Test complex request
        request = {
            'query': 'Analyze the impact of AI on software development',
            'requirements': {
                'research_depth': 'comprehensive',
                'include_examples': True,
                'future_predictions': True
            }
        }
        
        logger.info("Testing Hybrid Orchestration Pattern")
        result = await orchestrator.execute(request)
        
        logger.info(f"Hybrid orchestration completed!")
        logger.info(f"Execution phases: {len(result.get('execution_log', []))}")
        
        return True, result
        
    except Exception as e:
        logger.error(f"Advanced patterns test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)

async def test_complete_system():
    """Test Complete Investment Analysis System"""
    logger.info("\n=== Testing Complete Investment Analysis System ===")
    
    try:
        from a2a_mcp.agents.adk_examples.complete_system_example import InvestmentAnalysisSystem
        
        # Initialize system
        system = InvestmentAnalysisSystem()
        await system.initialize()
        
        # Test single stock analysis
        logger.info("Testing single stock analysis")
        result = await system.analyze_investment(
            ticker="AAPL",
            context={
                'portfolio_size': 100000,
                'risk_tolerance': 'moderate',
                'investment_horizon': '12 months'
            }
        )
        
        if result['success']:
            logger.info(f"Investment analysis completed for {result['ticker']}")
            logger.info(f"Analysis timestamp: {result['timestamp']}")
        else:
            logger.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
        
        return result['success'], result
        
    except Exception as e:
        logger.error(f"Complete system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)

async def main():
    """Run all tests"""
    logger.info("Starting ADK Agent Tests")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check for API key
    if not os.environ.get('GOOGLE_API_KEY'):
        logger.warning("GOOGLE_API_KEY not set. Some tests may fail.")
    
    # Summary of results
    summary = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Run Tier 1 tests
    success, result = await test_tier1_orchestrator()
    summary['tests']['tier1_orchestrator'] = {
        'success': success,
        'message': 'Passed' if success else result
    }
    
    # Run Tier 2 tests
    tier2_results = await test_tier2_specialists()
    summary['tests']['tier2_specialists'] = tier2_results
    
    # Run Tier 3 tests
    tier3_results = await test_tier3_services()
    summary['tests']['tier3_services'] = tier3_results
    
    # Run Advanced Pattern tests
    success, result = await test_advanced_patterns()
    summary['tests']['advanced_patterns'] = {
        'success': success,
        'message': 'Passed' if success else result
    }
    
    # Run Complete System test
    success, result = await test_complete_system()
    summary['tests']['complete_system'] = {
        'success': success,
        'message': 'Passed' if success else result
    }
    
    # Print summary
    logger.info("\n=== TEST SUMMARY ===")
    logger.info(json.dumps(summary, indent=2))
    
    # Count successes
    total_tests = 0
    passed_tests = 0
    
    for test_category, results in summary['tests'].items():
        if isinstance(results, dict) and 'success' in results:
            total_tests += 1
            if results['success']:
                passed_tests += 1
        elif isinstance(results, dict):
            # Handle nested results (tier2, tier3)
            for sub_test, sub_result in results.items():
                total_tests += 1
                if sub_result[0]:  # First element is success boolean
                    passed_tests += 1
    
    logger.info(f"\nTotal Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())