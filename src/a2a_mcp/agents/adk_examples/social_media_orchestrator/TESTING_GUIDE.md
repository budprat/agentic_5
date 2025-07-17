# Social Media Orchestrator - Agent Testing Guide

## ✅ Quick Test Results

**All 8 sub-agents are properly configured and ready for testing:**

1. ✅ **social_media_content_agent** - Multi-platform content generation
2. ✅ **blog_post_generator_agent** - SEO-optimized blog posts  
3. ✅ **email_agent** - Professional email generation
4. ✅ **lead_qualification_agent** - BANT lead qualification
5. ✅ **linkedin_carousel_agent** - LinkedIn carousel creation
6. ✅ **competitor_analysis_agent** - Competitive analysis
7. ✅ **trend_analysis_agent** - Industry trend analysis
8. ✅ **news_analyst** - Real-time news analysis

## 🧪 Manual Testing Protocol

### Step 1: Start the Orchestrator
```bash
cd /Users/mac/Agents/agentic_5/src/a2a_mcp/agents/adk_examples/social_media_orchestrator
/opt/anaconda3/envs/a2a-mcp/bin/python main.py
```

### Step 2: Test Each Agent Systematically

Copy and paste each query below, one at a time:

#### **Test 1: Social Media Content Agent**
```
Create a LinkedIn post about AI trends in healthcare
```
**Expected Output:**
- `Event ID: xxx, Author: social_media_content_agent`
- Multi-platform content (LinkedIn, X/Twitter, Instagram)
- Visual content requirements
- Engagement tactics

#### **Test 2: Blog Post Generator Agent**
```
Write a comprehensive blog post about quantum computing developments
```
**Expected Output:**
- `Event ID: xxx, Author: blog_post_generator_agent`
- SEO-optimized blog structure
- Meta descriptions and tags

#### **Test 3: Email Agent**
```
Draft a professional email to investors about our Q4 financial results
```
**Expected Output:**
- `Event ID: xxx, Author: email_agent` (displays as `advanced_email_agent`)
- Professional email format
- Subject line and call-to-action

#### **Test 4: Lead Qualification Agent**
```
Qualify this lead: Sarah Johnson, VP Marketing at TechCorp, budget $100k, needs marketing automation solution by Q2
```
**Expected Output:**
- `Event ID: xxx, Author: lead_qualification_agent`
- BANT qualification analysis
- Lead scoring and recommendations

#### **Test 5: LinkedIn Carousel Agent**
```
Create a LinkedIn carousel about the top 5 machine learning frameworks for developers
```
**Expected Output:**
- `Event ID: xxx, Author: linkedin_carousel_agent`
- Slide-by-slide content
- Visual design guidelines

#### **Test 6: Competitor Analysis Agent**
```
Analyze competitor Microsoft and their latest AI product offerings compared to our capabilities
```
**Expected Output:**
- `Event ID: xxx, Author: competitor_analysis_agent`
- SWOT analysis
- Competitive positioning insights

#### **Test 7: Trend Analysis Agent**
```
What are the emerging trends in sustainable technology and green energy for 2024?
```
**Expected Output:**
- `Event ID: xxx, Author: trend_analysis_agent`
- Trend momentum scoring
- Market opportunity analysis

#### **Test 8: News Analyst Agent**
```
What's the latest news about ChatGPT and OpenAI developments this week?
```
**Expected Output:**
- `Event ID: xxx, Author: news_analyst`
- Recent news analysis
- Real-time insights

## 📊 What to Look For

### ✅ **Success Indicators:**
- Correct agent routing (check `Author:` in logs)
- Structured JSON responses
- No schema validation errors
- Response length > 500 characters
- All requested features present (hashtags, engagement tactics, etc.)

### ❌ **Failure Indicators:**
- Wrong agent triggered
- Empty or very short responses
- Schema validation errors
- Missing required fields
- Error messages in logs

## 🔍 Advanced Verification

### **Check Session State Management**
After each test, verify:
- `interaction_history` is being updated
- Previous context is maintained
- Session state shows proper agent responses

### **Verify All Restored Features**
Look for these in social media content responses:
- ✅ `repurposing_opportunities`
- ✅ `trending_elements`
- ✅ `adaptation_strategy`
- ✅ `style_guidelines`
- ✅ `text_overlay`
- ✅ `mentions`
- ✅ `engagement_tactics`
- ✅ `call_to_action`

### **Performance Benchmarks**
- Response time: < 30 seconds per query
- No memory leaks between tests
- Clean exit with `quit` command

## 🚨 Common Issues & Solutions

### **Issue: Wrong Agent Triggered**
**Solution:** Check query phrasing - be more specific about the task type

### **Issue: Schema Validation Errors**
**Solution:** Our recent fixes should prevent this, but if it occurs, check field lengths

### **Issue: Empty Responses**
**Solution:** Verify API keys and model configuration

### **Issue: Config Warnings**
**Solution:** Should be resolved with our transfer configuration fixes

## 📈 Expected Success Rate

- **Agent Routing Accuracy:** 100% (8/8 agents should route correctly)
- **Response Generation:** 100% (all agents should produce valid responses)
- **Schema Validation:** 100% (no validation errors expected)
- **Feature Completeness:** 100% (all restored features working)

## 🎯 Quick Verification Commands

```bash
# Run configuration test
python quick_agent_test.py

# Check for any remaining issues
grep -r "ERROR\|WARNING" *.py

# Verify all agents have transfer config
grep -r "disallow_transfer" social_media_agent/sub_agents/*/agent.py
```

## 📝 Test Results Template

Use this to track your manual testing:

```
Agent Test Results:
[ ] social_media_content_agent - Multi-platform content
[ ] blog_post_generator_agent - Blog post creation  
[ ] email_agent - Professional emails
[ ] lead_qualification_agent - BANT qualification
[ ] linkedin_carousel_agent - Carousel content
[ ] competitor_analysis_agent - Competitive analysis
[ ] trend_analysis_agent - Trend insights
[ ] news_analyst - Real-time news

Overall Status: ___/8 agents working correctly
```

## 🎉 Success Criteria

**The orchestrator is working perfectly when:**
- All 8 agents route correctly to their specific queries
- No config warnings appear (clean startup)
- All responses contain expected structured data
- Session management works across multiple queries
- No errors or timeouts occur

You should achieve 100% success rate with the current configuration!