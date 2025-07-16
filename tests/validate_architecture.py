# ABOUTME: Architecture validation test to ensure correct framework usage
# ABOUTME: Validates that VideoOrchestratorV2 uses Enhanced Master Orchestrator Template

"""
Architecture Validation Test

This test validates the critical architecture requirement:
- VideoOrchestratorV2 MUST use EnhancedMasterOrchestratorTemplate
- Domain specialists MUST use StandardizedAgentBase
"""

import sys
import os
import inspect

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def validate_video_orchestrator_v2():
    """Validate VideoOrchestratorV2 uses correct base class."""
    print("\n=== Validating VideoOrchestratorV2 Architecture ===")
    
    try:
        # Read the file directly
        orchestrator_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'src/video_generator/agents/video_orchestrator_v2.py'
        )
        
        with open(orchestrator_path, 'r') as f:
            content = f.read()
        
        # Check class definition
        if 'class VideoOrchestratorV2(EnhancedMasterOrchestratorTemplate):' in content:
            print("✅ VideoOrchestratorV2 correctly inherits from EnhancedMasterOrchestratorTemplate")
            
            # Check imports
            if 'from src.a2a_mcp.common.enhanced_master_orchestrator_template import EnhancedMasterOrchestratorTemplate' in content:
                print("✅ Correct import of EnhancedMasterOrchestratorTemplate")
            else:
                print("❌ Missing import of EnhancedMasterOrchestratorTemplate")
                return False
                
            # Check it's NOT using StandardizedAgentBase
            if 'StandardizedAgentBase' not in content:
                print("✅ Not using StandardizedAgentBase (correct)")
            else:
                print("❌ Found reference to StandardizedAgentBase (incorrect)")
                return False
                
            # Check for 7 enhancement phases
            if 'enable_phase_7_streaming' in content:
                print("✅ Supports PHASE 7 streaming")
            else:
                print("⚠️  No explicit PHASE 7 streaming support found")
                
            return True
        else:
            print("❌ VideoOrchestratorV2 does NOT inherit from EnhancedMasterOrchestratorTemplate")
            return False
            
    except Exception as e:
        print(f"❌ Error validating VideoOrchestratorV2: {e}")
        return False


def validate_domain_specialists():
    """Validate domain specialists use correct base class."""
    print("\n=== Validating Domain Specialists Architecture ===")
    
    specialists = [
        ('ScriptWriter', 'src/video_generator/agents/script_writer.py'),
        ('SceneDesigner', 'src/video_generator/agents/scene_designer.py'),
        ('TimingCoordinator', 'src/video_generator/agents/timing_coordinator.py')
    ]
    
    all_valid = True
    
    for class_name, relative_path in specialists:
        try:
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                relative_path
            )
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check class definition
            if f'class {class_name}(StandardizedAgentBase):' in content:
                print(f"✅ {class_name} correctly inherits from StandardizedAgentBase")
            else:
                print(f"❌ {class_name} does NOT inherit from StandardizedAgentBase")
                all_valid = False
                
        except Exception as e:
            print(f"❌ Error validating {class_name}: {e}")
            all_valid = False
            
    return all_valid


def validate_workflow_integration():
    """Validate workflow uses VideoOrchestratorV2."""
    print("\n=== Validating Workflow Integration ===")
    
    try:
        workflow_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'src/video_generator/workflow/video_generation_workflow.py'
        )
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check import
        if 'from src.video_generator.agents.video_orchestrator_v2 import VideoOrchestratorV2' in content:
            print("✅ Workflow imports VideoOrchestratorV2")
        else:
            print("❌ Workflow does NOT import VideoOrchestratorV2")
            return False
            
        # Check usage
        if 'VideoOrchestratorV2(' in content:
            print("✅ Workflow uses VideoOrchestratorV2")
        else:
            print("❌ Workflow does NOT use VideoOrchestratorV2")
            return False
            
        # Check it's not using old orchestrator
        if 'video_orchestrator.py' not in content or 'video_orchestrator_v2' in content:
            print("✅ Not using old VideoOrchestrator")
        else:
            print("❌ Still referencing old VideoOrchestrator")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error validating workflow: {e}")
        return False


def main():
    """Run all architecture validations."""
    print("Video Generation System - Architecture Validation Test")
    print("=" * 60)
    
    results = []
    
    # Run validations
    results.append(('VideoOrchestratorV2', validate_video_orchestrator_v2()))
    results.append(('Domain Specialists', validate_domain_specialists()))
    results.append(('Workflow Integration', validate_workflow_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("ARCHITECTURE VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nOverall: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 ARCHITECTURE IS CORRECT! VideoOrchestratorV2 properly uses EnhancedMasterOrchestratorTemplate")
        return 0
    else:
        print("\n❌ ARCHITECTURE ISSUES FOUND! Please fix the failing validations.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)