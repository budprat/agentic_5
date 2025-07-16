# SuperClaude Comprehensive Usage Guide

This guide covers what to use with Claude Code (SuperClaude framework), when to use it, and where it applies.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Commands Reference](#commands-reference)
3. [Flags Reference](#flags-reference)
4. [MCP Servers](#mcp-servers)
5. [Personas](#personas)
6. [Decision Trees](#decision-trees)
7. [Auto-Activation Rules](#auto-activation-rules)
8. [Common Scenarios](#common-scenarios)
9. [Best Practices](#best-practices)

## Quick Start

### Basic Command Structure
```
/command [arguments] --flags
```

### Most Common Commands
- `/build` - Build projects with framework detection
- `/implement` - Implement features and code
- `/analyze` - Analyze code and systems
- `/improve` - Enhance code quality
- `/test` - Run tests
- `/document` - Generate documentation
- `/git` - Git operations

### Essential Flags
- `--think` - Enable deep analysis (4K tokens)
- `--uc` - Ultra-compressed mode (30-50% token reduction)
- `--persona-[name]` - Activate specific persona
- `--c7` - Enable Context7 for documentation
- `--seq` - Enable Sequential for complex analysis
- `--wave-mode` - Multi-stage orchestration

## Commands Reference

### Development Commands

#### `/build [target] [flags]`
**Purpose**: Build projects with automatic framework detection
**Auto-Activates**: Frontend/Backend/Architect personas, Magic (UI), Context7 (patterns)
**Best For**: Creating new features, components, or systems
**Example**: `/build navbar --type component --framework react`

#### `/implement [feature] [flags]`
**Purpose**: Implement specific features with intelligent persona activation
**Auto-Activates**: Domain-specific personas, Magic (UI), Context7 (patterns), Sequential (complex logic)
**Best For**: Adding new functionality, implementing APIs, creating UI components
**Examples**:
- `/implement user authentication --type api`
- `/implement dashboard component --framework vue`
- `/implement payment integration --type service`

### Analysis Commands

#### `/analyze [target] [flags]`
**Purpose**: Multi-dimensional code and system analysis
**Auto-Activates**: Analyzer/Architect/Security personas, Sequential (primary), Context7 (patterns)
**Best For**: Understanding codebases, finding issues, architectural reviews
**Examples**:
- `/analyze --focus performance`
- `/analyze authentication.js --focus security`
- `/analyze @src/ --scope project`

#### `/troubleshoot [symptoms] [flags]`
**Purpose**: Debug and investigate problems
**Auto-Activates**: Analyzer/QA personas, Sequential, Playwright
**Best For**: Finding root causes, debugging issues
**Example**: `/troubleshoot "API returns 500 errors"`

#### `/explain [topic] [flags]`
**Purpose**: Educational explanations
**Auto-Activates**: Mentor/Scribe personas, Context7, Sequential
**Best For**: Learning, documentation, understanding concepts
**Example**: `/explain React hooks --detailed`

### Quality Commands

#### `/improve [target] [flags]`
**Purpose**: Evidence-based code enhancement
**Auto-Activates**: Refactorer/Performance/Architect/QA personas, Sequential, Context7
**Best For**: Refactoring, optimization, code quality improvements
**Examples**:
- `/improve --focus performance`
- `/improve auth.js --quality`
- `/improve @components/ --loop` (iterative improvement)

#### `/cleanup [target] [flags]`
**Purpose**: Technical debt reduction
**Auto-Activates**: Refactorer persona, Sequential
**Best For**: Removing dead code, simplifying complex code
**Example**: `/cleanup @src/ --focus unused-code`

### Additional Commands

#### `/test [type] [flags]`
**Purpose**: Testing workflows
**Auto-Activates**: QA persona, Playwright, Sequential
**Examples**:
- `/test unit`
- `/test e2e --browser chrome`
- `/test integration @api/`

#### `/document [target] [flags]`
**Purpose**: Generate documentation
**Auto-Activates**: Scribe/Mentor personas, Context7, Sequential
**Examples**:
- `/document @api/ --type swagger`
- `/document README.md --persona-scribe=es` (Spanish)

#### `/git [operation] [flags]`
**Purpose**: Git workflow assistance
**Auto-Activates**: DevOps/Scribe/QA personas, Sequential
**Examples**:
- `/git commit --message "feat: add auth"`
- `/git pr --title "Add authentication"`

## Flags Reference

### Thinking & Analysis Flags

#### `--think`
- **When**: Complex problems requiring multi-file analysis
- **Tokens**: ~4K
- **Auto-enables**: `--seq`, suggests `--persona-analyzer`
- **Use for**: Import chains, cross-module analysis

#### `--think-hard`
- **When**: System-wide analysis, architectural decisions
- **Tokens**: ~10K
- **Auto-enables**: `--seq --c7`, suggests `--persona-architect`
- **Use for**: Major refactoring, security audits

#### `--ultrathink`
- **When**: Critical system redesign, legacy modernization
- **Tokens**: ~32K
- **Auto-enables**: `--seq --c7 --all-mcp`
- **Use for**: Complete system overhauls

### Efficiency Flags

#### `--uc` / `--ultracompressed`
- **When**: Context usage >75%, large operations
- **Effect**: 30-50% token reduction
- **Auto-activates**: When resources constrained
- **Maintains**: Technical accuracy with symbols

#### `--validate`
- **When**: Risky operations, production changes
- **Auto-activates**: Risk score >0.7
- **Includes**: Pre-operation validation, risk assessment

#### `--safe-mode`
- **When**: Production environment, critical operations
- **Auto-activates**: Resource usage >85%
- **Effect**: Maximum validation, conservative execution

### MCP Server Flags

#### `--c7` / `--context7`
- **When**: Need official documentation, framework patterns
- **Auto-activates**: Library imports detected
- **Use for**: React, Vue, Angular, Node.js docs

#### `--seq` / `--sequential`
- **When**: Complex debugging, multi-step analysis
- **Auto-activates**: With any `--think` flag
- **Use for**: Root cause analysis, system design

#### `--magic`
- **When**: Creating UI components
- **Auto-activates**: Component/UI keywords
- **Use for**: Modern component generation

#### `--play` / `--playwright`
- **When**: E2E testing, browser automation
- **Use for**: Cross-browser testing, visual regression

### Orchestration Flags

#### `--wave-mode [auto|force|off]`
- **When**: Complex multi-stage operations
- **Auto**: complexity >0.8 AND files >20 AND operation_types >2
- **Effect**: 30-50% better results through compound intelligence

#### `--delegate [files|folders|auto]`
- **When**: Large-scale analysis needed
- **Auto-activates**: >7 directories or >50 files
- **Effect**: 40-70% time savings

#### `--loop`
- **When**: Iterative improvements needed
- **Auto-activates**: Keywords like "polish", "refine", "enhance"
- **Default**: 3 iterations

### Persona Flags

#### `--persona-architect`
- **When**: System design, architecture decisions
- **Focus**: Long-term maintainability, scalability
- **Prefers**: Sequential, Context7

#### `--persona-frontend`
- **When**: UI/UX work
- **Focus**: User experience, accessibility, performance
- **Prefers**: Magic, Playwright

#### `--persona-backend`
- **When**: Server-side, API development
- **Focus**: Reliability, security, data integrity
- **Prefers**: Context7, Sequential

#### `--persona-security`
- **When**: Security audits, threat modeling
- **Focus**: Vulnerabilities, compliance
- **Prefers**: Sequential, Context7

#### `--persona-performance`
- **When**: Optimization needed
- **Focus**: Bottlenecks, metrics
- **Prefers**: Playwright, Sequential

## Decision Trees

### "What Command Should I Use?"

```
Need to create something new?
├── UI Component → /build or /implement + --magic
├── API/Backend → /implement --type api
└── Full Feature → /implement + appropriate flags

Need to understand/fix code?
├── Debug Issue → /troubleshoot or /analyze
├── Performance → /analyze --focus performance
└── Security → /analyze --focus security

Need to improve code?
├── Quality → /improve --quality
├── Performance → /improve --perf
└── Cleanup → /cleanup

Need documentation/testing?
├── Tests → /test [type]
├── Docs → /document
└── Git → /git [operation]
```

### "What Flags Should I Add?"

```
Is it complex?
├── Yes → Add --think (or --think-hard for very complex)
├── Involves UI? → Add --magic
├── Need docs? → Add --c7
└── Multiple steps? → Add --seq

Running low on tokens?
├── Add --uc for compression
└── Critical operation? → Add --safe-mode

Large codebase?
├── >50 files → Auto-activates --delegate
├── >20 files + complex → Consider --wave-mode
└── Need speed? → Use --delegate folders

Want specific expertise?
├── Architecture → --persona-architect
├── Frontend → --persona-frontend
├── Security → --persona-security
└── Performance → --persona-performance
```

## Auto-Activation Rules

### Commands Auto-Activate Based On:

1. **Keywords in your request**
   - "component", "UI" → Frontend persona + Magic
   - "API", "endpoint" → Backend persona + Context7
   - "vulnerability", "security" → Security persona + Sequential
   - "performance", "optimize" → Performance persona

2. **Complexity Detection**
   - Simple (1 file, <3 steps) → Minimal activation
   - Moderate (multi-file, 3-10 steps) → Appropriate personas + MCP
   - Complex (system-wide, >10 steps) → Multiple personas + all relevant MCP

3. **File Patterns**
   - `*.jsx`, `*.tsx` → Frontend tools
   - `controllers/*`, `models/*` → Backend tools
   - `*.test.js` → QA tools

### Flags Auto-Activate When:

1. **Resource Constraints**
   - Context >75% → `--uc`
   - Risk >0.7 → `--validate`
   - Production detected → `--safe-mode`

2. **Scale Thresholds**
   - >7 directories → `--delegate`
   - >50 files → `--delegate files`
   - Complexity >0.8 + files >20 → `--wave-mode`

3. **Keywords**
   - "polish", "refine" → `--loop`
   - Import statements → `--c7`
   - "debug", "trace" → `--seq`

## Common Scenarios

### Scenario 1: Building a New React Component
```bash
/build user-profile --type component --framework react

# Auto-activates:
# - Frontend persona
# - Magic (UI generation)
# - Context7 (React patterns)
```

### Scenario 2: Debugging API Issues
```bash
/troubleshoot "API returns 500 on user login"

# Auto-activates:
# - Analyzer persona
# - Sequential (root cause analysis)
# - Backend persona (if API-related)
```

### Scenario 3: Large Codebase Analysis
```bash
/analyze @src/ --comprehensive

# Auto-activates:
# - --delegate (due to scale)
# - Multiple personas
# - --uc (if needed)
```

### Scenario 4: Security Audit
```bash
/analyze --focus security --scope project

# Auto-activates:
# - Security persona
# - --think-hard or --ultrathink
# - Sequential for threat modeling
```

### Scenario 5: Performance Optimization
```bash
/improve @api/ --focus performance

# Auto-activates:
# - Performance persona
# - Playwright (for metrics)
# - --think for analysis
```

### Scenario 6: Iterative Code Improvement
```bash
/improve @components/ --loop --iterations 5

# Runs 5 improvement cycles
# Each validated before next
# Progressive enhancement
```

## Best Practices

### 1. Let Auto-Activation Work
- Don't manually specify flags that auto-activate
- Trust the detection engine
- Override only when needed

### 2. Use Wave Mode for Complex Operations
- Automatic for very complex tasks
- Better results through multi-stage approach
- Worth the extra time

### 3. Leverage Personas
- Each has specialized knowledge
- Auto-activate based on context
- Can manually override with `--persona-[name]`

### 4. Token Management
- `--uc` auto-activates when needed
- Maintains quality while saving tokens
- Use symbol reference if unclear

### 5. MCP Server Usage
- Context7: Official docs and patterns
- Sequential: Complex reasoning
- Magic: UI components
- Playwright: Testing and metrics

### 6. Task Management
- TodoWrite automatically creates tasks for 3+ steps
- One task in_progress at a time
- Use `/task` for multi-session projects

### 7. Quality Gates
- All operations go through 8-step validation
- Automatic quality checks
- Evidence-based completion

### 8. Iterative Improvement
- Use `--loop` for refinement
- Auto-activates on quality keywords
- Default 3 iterations

## Advanced Tips

### Combining Flags Effectively
```bash
# Maximum analysis power
/analyze --ultrathink --all-mcp --scope system

# Efficient large-scale improvement
/improve @src/ --wave-mode --uc --focus quality

# Comprehensive testing
/test e2e --play --validate --persona-qa
```

### Understanding Wave Strategies
- **Progressive**: Step-by-step enhancement
- **Systematic**: Methodical comprehensive analysis
- **Adaptive**: Adjusts to varying complexity
- **Enterprise**: For massive codebases

### Performance Optimization
- Batch operations when possible
- Use delegation for large scopes
- Enable caching with MCP servers
- Leverage --uc when appropriate

### Emergency Protocols
- Resource zones: Green (0-60%) → Critical (95%+)
- Graceful degradation at each level
- Automatic optimization activation
- Safety overrides optimization