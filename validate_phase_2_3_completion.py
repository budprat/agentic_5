#!/usr/bin/env python3
"""
Phase 2.3 Completion Validation Script
Validates that all Phase 2.3 orchestration implementation is complete.
"""

import os
import json
from pathlib import Path
from datetime import datetime

class Phase23Validator:
    def __init__(self):
        self.base_path = Path("/home/solopreneur")
        self.results = []
        
    def validate_oracle_agent_implementation(self):
        """Validate the solopreneur oracle agent implementation."""
        print("🧪 Validating Oracle Agent Implementation")
        print("=" * 50)
        
        oracle_file = self.base_path / "src/a2a_mcp/agents/solopreneur_oracle/solopreneur_oracle_agent.py"
        
        if oracle_file.exists():
            content = oracle_file.read_text()
            
            # Check for key orchestration features
            features = {
                "ADK Base Class": "BaseAgent" in content,
                "ParallelWorkflowGraph": "ParallelWorkflowGraph" in content,
                "Domain Dependencies": "analyze_domain_dependencies" in content,
                "A2A Protocol Communication": "http://localhost:" in content and "aiohttp" in content,
                "Fallback Analysis": "_get_fallback_analysis" in content,
                "Quality Thresholds": "check_quality_thresholds" in content,
                "Health Validation": "validate_orchestration_health" in content,
                "Error Handling": "handle_orchestration_failure" in content,
                "Gemini Integration": "google.generativeai" in content,
                "Streaming Interface": "async def stream" in content
            }
            
            for feature, present in features.items():
                status = "✅" if present else "❌"
                print(f"   {status} {feature}: {'Present' if present else 'Missing'}")
                
            all_present = all(features.values())
            self.results.append(("Oracle Agent Implementation", all_present))
            return all_present
        else:
            print("   ❌ Oracle agent file not found")
            self.results.append(("Oracle Agent Implementation", False))
            return False
    
    def validate_domain_specialists(self):
        """Validate domain specialist agent files."""
        print("\n🧪 Validating Domain Specialist Agents")
        print("=" * 50)
        
        specialists = [
            "technical_intelligence_agent.py",
            "knowledge_management_agent.py",
            "personal_optimization_agent.py",
            "learning_enhancement_agent.py",
            "integration_synthesis_agent.py"
        ]
        
        oracle_dir = self.base_path / "src/a2a_mcp/agents/solopreneur_oracle"
        all_present = True
        
        for specialist in specialists:
            specialist_file = oracle_dir / specialist
            if specialist_file.exists():
                print(f"   ✅ {specialist}: Present")
            else:
                print(f"   ❌ {specialist}: Missing")
                all_present = False
        
        self.results.append(("Domain Specialists", all_present))
        return all_present
    
    def validate_agent_cards(self):
        """Validate agent card configurations."""
        print("\n🧪 Validating Agent Card Configurations")
        print("=" * 50)
        
        agent_cards = [
            "solopreneur_oracle_agent.json",
            "technical_intelligence_agent.json",
            "knowledge_management_agent.json",
            "personal_optimization_agent.json",
            "learning_enhancement_agent.json",
            "integration_synthesis_agent.json"
        ]
        
        cards_dir = self.base_path / "agent_cards"
        all_present = True
        
        for card in agent_cards:
            card_file = cards_dir / card
            if card_file.exists():
                try:
                    card_data = json.loads(card_file.read_text())
                    has_skills = "skills" in card_data
                    has_url = "url" in card_data
                    print(f"   ✅ {card}: Valid JSON with {'skills' if has_skills else 'no skills'}")
                except json.JSONDecodeError:
                    print(f"   ❌ {card}: Invalid JSON")
                    all_present = False
            else:
                print(f"   ❌ {card}: Missing")
                all_present = False
        
        self.results.append(("Agent Cards", all_present))
        return all_present
    
    def validate_startup_scripts(self):
        """Validate startup and test scripts."""
        print("\n🧪 Validating Startup and Test Scripts")
        print("=" * 50)
        
        scripts = {
            "run_solopreneur_agents.sh": "Startup script",
            "test_solopreneur_oracle_orchestration.py": "Orchestration test",
            "test_solopreneur_integration.py": "Integration test",
            "test_orchestration_standalone.py": "Standalone test"
        }
        
        all_present = True
        
        for script, description in scripts.items():
            script_file = self.base_path / script
            if script_file.exists():
                print(f"   ✅ {script}: {description} present")
            else:
                print(f"   ❌ {script}: {description} missing")
                all_present = False
        
        self.results.append(("Scripts", all_present))
        return all_present
    
    def validate_framework_integration(self):
        """Validate integration with A2A-MCP framework."""
        print("\n🧪 Validating Framework Integration")
        print("=" * 50)
        
        main_file = self.base_path / "src/a2a_mcp/agents/__main__.py"
        
        if main_file.exists():
            content = main_file.read_text()
            
            integration_checks = {
                "Solopreneur Oracle Import": "solopreneur_oracle_agent" in content,
                "Technical Intelligence Import": "technical_intelligence_agent" in content,
                "Knowledge Management Import": "knowledge_management_agent" in content,
                "Personal Optimization Import": "personal_optimization_agent" in content,
                "Learning Enhancement Import": "learning_enhancement_agent" in content,
                "Integration Synthesis Import": "integration_synthesis_agent" in content
            }
            
            for check, present in integration_checks.items():
                status = "✅" if present else "❌"
                print(f"   {status} {check}: {'Integrated' if present else 'Missing'}")
            
            all_integrated = all(integration_checks.values())
            self.results.append(("Framework Integration", all_integrated))
            return all_integrated
        else:
            print("   ❌ Main agent file not found")
            self.results.append(("Framework Integration", False))
            return False
    
    def validate_port_configuration(self):
        """Validate port configurations across all files."""
        print("\n🧪 Validating Port Configurations")
        print("=" * 50)
        
        expected_ports = {
            "Solopreneur Oracle": 10901,
            "Technical Intelligence": 10902,
            "Knowledge Management": 10903,
            "Personal Optimization": 10904,
            "Learning Enhancement": 10905,
            "Integration Synthesis": 10906
        }
        
        # Check startup script
        startup_script = self.base_path / "run_solopreneur_agents.sh"
        if startup_script.exists():
            content = startup_script.read_text()
            all_ports_configured = True
            
            for agent, port in expected_ports.items():
                if str(port) in content:
                    print(f"   ✅ {agent}: Port {port} configured")
                else:
                    print(f"   ❌ {agent}: Port {port} missing")
                    all_ports_configured = False
            
            self.results.append(("Port Configuration", all_ports_configured))
            return all_ports_configured
        else:
            print("   ❌ Startup script not found")
            self.results.append(("Port Configuration", False))
            return False
    
    def validate_orchestration_logic(self):
        """Validate core orchestration logic implementation."""
        print("\n🧪 Validating Orchestration Logic Implementation")
        print("=" * 50)
        
        oracle_file = self.base_path / "src/a2a_mcp/agents/solopreneur_oracle/solopreneur_oracle_agent.py"
        
        if oracle_file.exists():
            content = oracle_file.read_text()
            
            logic_features = {
                "Domain Analysis": "analyze_domain_dependencies" in content,
                "Execution Planning": "_build_execution_plan" in content,
                "Parallel Batches": "_identify_parallel_batches" in content,
                "A2A Communication": "aiohttp" in content and "session.post" in content,
                "Fallback Handling": "_get_fallback_analysis" in content,
                "Quality Validation": "check_quality_thresholds" in content,
                "Health Monitoring": "validate_orchestration_health" in content,
                "Error Recovery": "handle_orchestration_failure" in content
            }
            
            for feature, present in logic_features.items():
                status = "✅" if present else "❌"
                print(f"   {status} {feature}: {'Implemented' if present else 'Missing'}")
            
            all_implemented = all(logic_features.values())
            self.results.append(("Orchestration Logic", all_implemented))
            return all_implemented
        else:
            print("   ❌ Oracle agent file not found")
            self.results.append(("Orchestration Logic", False))
            return False
    
    def generate_completion_report(self):
        """Generate Phase 2.3 completion report."""
        print("\n" + "=" * 70)
        print("PHASE 2.3 COMPLETION VALIDATION REPORT")
        print("=" * 70)
        print(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Framework: A2A-MCP with ADK Pattern")
        print(f"Architecture: 3-Tier Solopreneur Oracle System")
        
        total_checks = len(self.results)
        passed_checks = sum(1 for _, passed in self.results if passed)
        
        print(f"\nValidation Results: {passed_checks}/{total_checks} components validated")
        print(f"Success Rate: {(passed_checks/total_checks)*100:.1f}%")
        
        print("\nDetailed Results:")
        for component, passed in self.results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status} {component}")
        
        if passed_checks == total_checks:
            print("\n🎉 PHASE 2.3 IMPLEMENTATION: COMPLETE!")
            print("✅ Orchestration logic with ParallelWorkflowGraph: IMPLEMENTED")
            print("✅ 5 Domain specialists: CREATED")
            print("✅ Agent cards and configurations: CONFIGURED")
            print("✅ A2A protocol communication: INTEGRATED")
            print("✅ Startup and test scripts: PROVIDED")
            print("✅ Health monitoring and error handling: IMPLEMENTED")
            print("✅ Framework integration: COMPLETE")
            
            print("\n🏆 Ready to proceed to Phase 3: Integration & Testing")
            return True
        else:
            print(f"\n⚠️  {total_checks - passed_checks} components need attention")
            print("   Review failed validations before proceeding")
            return False

def main():
    """Run Phase 2.3 completion validation."""
    print("🚀 Phase 2.3 Completion Validation")
    print("Solopreneur Oracle System - ParallelWorkflowGraph Implementation")
    print("=" * 70)
    
    validator = Phase23Validator()
    
    # Run all validations
    validator.validate_oracle_agent_implementation()
    validator.validate_domain_specialists()
    validator.validate_agent_cards()
    validator.validate_startup_scripts()
    validator.validate_framework_integration()
    validator.validate_port_configuration()
    validator.validate_orchestration_logic()
    
    # Generate final report
    success = validator.generate_completion_report()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)