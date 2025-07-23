# Orchestrator Migration Guide

## Overview

We've consolidated the A2A-MCP orchestrator implementations into a single, comprehensive orchestrator that includes all features from both previous versions.

## What Changed

### Before (Two Separate Files)
```python
# Previously needed two files
from research_assistant_agent.a2a_research_orchestrator import A2AResearchOrchestrator
from research_assistant_agent.enhanced_orchestrator_with_reference import ReferenceEnhancedOrchestrator

# Had to use inheritance
orchestrator = ReferenceEnhancedOrchestrator()  # This extended A2AResearchOrchestrator
```

### After (Single Combined File)
```python
# Now just one import
from research_assistant_agent import create_enhanced_orchestrator

# Get everything in one orchestrator
orchestrator = create_enhanced_orchestrator()
```

## File Changes

1. **New File**: `a2a_enhanced_orchestrator.py` - Contains all functionality
2. **Can Remove** (if desired):
   - `a2a_research_orchestrator.py` - Functionality moved to new file
   - `enhanced_orchestrator_with_reference.py` - Functionality moved to new file

## Feature Mapping

All features are preserved in the new `A2AEnhancedOrchestrator`:

### From `a2a_research_orchestrator.py`:
- ✅ Quality validation with 7 academic metrics
- ✅ Observability with OpenTelemetry
- ✅ A2A protocol communication
- ✅ Research metrics collection
- ✅ Streaming with artifacts
- ✅ ADK agent wrapping

### From `enhanced_orchestrator_with_reference.py`:
- ✅ Reference Intelligence Service
- ✅ Multi-source aggregation
- ✅ Intelligent deduplication
- ✅ Cross-source validation
- ✅ Quality-based ranking
- ✅ Filter-based searching

### New Enhanced Features:
- ✅ Advanced pattern extraction (code, JSON, equations)
- ✅ `extract_structured_content()` method in Literature Review Agent
- ✅ Citation network analysis with H-index calculation
- ✅ Seminal work identification
- ✅ ResponseFormatter integration with pattern matching
- ✅ Enhanced metadata enrichment

## Migration Steps

1. **Update Imports**:
   ```python
   # Old
   from research_assistant_agent.enhanced_orchestrator_with_reference import ReferenceEnhancedOrchestrator
   
   # New
   from research_assistant_agent import A2AEnhancedOrchestrator, create_enhanced_orchestrator
   ```

2. **Update Instantiation**:
   ```python
   # Old
   orchestrator = ReferenceEnhancedOrchestrator()
   
   # New (recommended)
   orchestrator = create_enhanced_orchestrator()
   
   # Or
   orchestrator = A2AEnhancedOrchestrator()
   ```

3. **No API Changes**: All methods remain the same:
   - `coordinate_research()`
   - `research_with_multi_source()`
   - `search_with_filters()`
   - `stream_research_with_artifacts()`

## Benefits

1. **Simpler Architecture**: One class instead of inheritance chain
2. **Easier to Understand**: All features in one place
3. **Better Performance**: Reduced object initialization overhead
4. **Maintained Compatibility**: All existing code continues to work
5. **Future-Proof**: Easier to add new features

## Example Usage

```python
import asyncio
from research_assistant_agent import create_enhanced_orchestrator

async def main():
    # Create orchestrator with all features
    orchestrator = create_enhanced_orchestrator()
    
    # Use any feature from either original class
    result = await orchestrator.coordinate_research(
        query="machine learning interpretability",
        config={
            "aggregate_sources": True,     # From Reference Intelligence
            "quality_validation": True      # From A2A core
        }
    )
    
    # Multi-source aggregation
    multi_result = await orchestrator.research_with_multi_source(
        query="quantum computing",
        sources=["arxiv", "semantic_scholar"],
        aggregate_strategy="quality_weighted"
    )
    
    # Filtered search
    filtered = await orchestrator.search_with_filters(
        query="deep learning",
        filters={"min_year": 2022, "min_citations": 50}
    )

asyncio.run(main())
```

## Backward Compatibility

The original files still exist and work, so there's no immediate need to migrate. However, we recommend using the new combined orchestrator for:
- New projects
- When refactoring existing code
- To simplify your codebase

## Questions?

The combined orchestrator includes comprehensive docstrings and all functionality is preserved exactly as before. Check `a2a_enhanced_orchestrator.py` for detailed documentation.