# Session Notes - Cortex Enablement
Date: 2025-01-04

## Session Summary
Worked on enabling Snowflake Cortex LLM features for the A2A-MCP project.

## Key Findings

### 1. Cortex Setup Status
- ✅ Successfully granted CORTEX_USER database role to SYSADMIN
- ✅ Verified Cortex functions exist (54 functions in CORTEX schema, 24 in ML schema)
- ❌ Functions return "remote service error 400" when called

### 2. Regional Limitation
- Account: NBTQRQH-YX22629
- Region: GCP_ME_CENTRAL2 (Middle East Central)
- **Issue**: Cortex LLM features have limited availability in this region

### 3. Available Functions Found
- SNOWFLAKE.CORTEX schema has: COMPLETE, SENTIMENT, SUMMARIZE, TRANSLATE, EXTRACT_ANSWER
- SNOWFLAKE.ML schema has: AI_COMPLETE, AI_EMBED, AI_CLASSIFY
- Functions exist but are not operational due to regional limitations

## Scripts Created
1. `enable_cortex_access.py` - Grants CORTEX_USER role and tests availability
2. `check_cortex_availability.py` - Comprehensive check of Cortex functions
3. `test_ai_complete.py` - Tests AI_COMPLETE function specifically
4. `diagnose_cortex.py` - Full diagnostics including region checks

## Next Steps When Resuming
1. **Contact Snowflake Support** to enable Cortex in GCP_ME_CENTRAL2 region
2. **Alternative Options**:
   - Use a different Snowflake account in a supported region
   - Supported regions: US_WEST_2, US_EAST_1, EU_WEST_1, EU_CENTRAL_1, AP_SOUTHEAST_1
3. Once Cortex is enabled:
   - Run `test_cortex_simple.py` to verify functionality
   - Update the Market Oracle agents to use Cortex for AI analysis
   - Implement the AI-powered market analysis features

## Environment Details
- Python 3.13.1
- uv 0.1.45
- All dependencies installed
- .env file configured with Snowflake credentials
- COMPUTE_WH warehouse available and accessible

## Code Status
- Main codebase is clean (no uncommitted changes)
- All test scripts are ready to use once Cortex is enabled
- MCP server configuration is properly set up