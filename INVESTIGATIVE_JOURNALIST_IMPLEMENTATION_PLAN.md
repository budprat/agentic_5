# "Investigative Journalist AI" A2A-MCP Implementation Plan

## Overview
Transform the Investigative-Creator GPT into a sophisticated multi-agent system using A2A-MCP framework patterns, specialized for Indian investigative journalism with corporate network analysis, OSINT verification, and secure content generation.

## Core Agent Architecture (7 Specialized Agents)

### 1. Investigative Orchestrator Agent (Port 10301)
**Persona**: "InvestiGenie" - AI investigative journalist assistant
**Security Model**: Air-gapped with selective MCP integration
**Core Functions**: Tip ingestion, workflow coordination, ethical oversight, export management

### 2. Entity Extraction Agent (Port 10302) 
**Specialization**: spaCy-HI, regex heuristics, Indian entity recognition
**Domain**: Companies (CIN), Politicians, NGOs, Financial instruments
**Integration**: Context7 MCP for legal entity databases

### 3. Corporate Maze-Breaker Agent (Port 10303)
**Specialization**: MCA-21 filings, SEBI data, ownership graph construction
**Tech Stack**: Neo4j integration, NetworkX analysis, shell company detection
**MCP Integration**: Supabase for graph storage, BrightData for corporate scraping

### 4. OSINT Verification Agent (Port 10304)
**Specialization**: Multi-source verification, satellite imagery analysis, social media cross-reference
**Tools**: Sentinel-2 analysis, reverse image search, indic-BERT sentiment
**MCP Integration**: Puppeteer for automated verification, Brave Search for cross-referencing

### 5. Legal Risk Assessment Agent (Port 10305)
**Specialization**: Indian legal framework, defamation risk, UAPA compliance
**Knowledge Base**: Supreme Court/High Court precedents, media law
**Integration**: Local LLM with legal corpus, risk scoring algorithms

### 6. Content Strategy Agent (Port 10306)
**Specialization**: Investigative storytelling, narrative structure, audience engagement
**Outputs**: 12-minute YouTube scripts, thumbnail suggestions, SEO optimization
**MCP Integration**: Firecrawl for competitive analysis, NotionAI for content management

### 7. Technical Export Agent (Port 10307)
**Specialization**: Multi-format export (Premiere Pro XML, DaVinci Resolve DRT)
**Security**: Encrypted evidence bundles, SHA-256 hashing, audit trails
**Integration**: ffmpeg-python, secure file handling

## Operational Modes & Workflows

### Investigation Modes:
- **Corporate Exposure Mode**: Shell company analysis, ownership tracing
- **Political Investigation Mode**: Enhanced legal safeguards, multi-source verification
- **Financial Fraud Mode**: Transaction pattern analysis, regulatory compliance
- **Social Impact Mode**: NGO/CSR tracking, impact verification

### Security-First Workflow:
1. **Secure Ingestion**: Encrypted tip processing with source protection
2. **Evidence Chain**: Cryptographic hashing at each verification step
3. **Legal Clearance**: Mandatory risk assessment before publication
4. **Controlled Export**: Human-in-the-loop approval for external sharing

## Enhanced Database Schema

```sql
-- Core investigative entities
CREATE TABLE investigations (
    id INTEGER PRIMARY KEY,
    case_title TEXT NOT NULL,
    risk_score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Entity network mapping
CREATE TABLE entities (
    id INTEGER PRIMARY KEY,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- company, person, politician, ngo
    cin_number TEXT,
    verification_status TEXT DEFAULT 'pending',
    risk_flags TEXT
);

-- Evidence tracking with cryptographic integrity
CREATE TABLE evidence_items (
    id INTEGER PRIMARY KEY,
    investigation_id INTEGER,
    source_type TEXT NOT NULL, -- document, image, satellite, social
    content_hash TEXT NOT NULL, -- SHA-256
    verification_score INTEGER,
    legal_clearance BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (investigation_id) REFERENCES investigations (id)
);

-- Legal risk assessments
CREATE TABLE legal_assessments (
    id INTEGER PRIMARY KEY,
    investigation_id INTEGER,
    risk_category TEXT NOT NULL, -- defamation, uapa, contempt
    risk_score INTEGER,
    mitigation_steps TEXT,
    cleared_by TEXT,
    FOREIGN KEY (investigation_id) REFERENCES investigations (id)
);
```

## MCP Integration Strategy

**Air-Gapped Core + Selective Cloud Integration**:
- **Local Processing**: Entity extraction, legal assessment, content generation
- **Secured Cloud Access**: Corporate data scraping (BrightData), satellite imagery
- **Verification Pipeline**: Brave Search, Puppeteer for automated checks
- **Content Support**: Firecrawl for research, Context7 for legal precedents

## Technical Implementation

### Security Architecture:
- **Encrypted Vault**: AES-256 encrypted storage for sensitive documents
- **Dead-Man Switch**: Auto-purge after 72h inactivity
- **Audit Trail**: Complete investigation history with cryptographic integrity
- **Air-Gap Mode**: Disable all external MCPs for sensitive investigations

### Agent Coordination:
- **Dependency Graph**: Automated workflow progression based on evidence readiness
- **Human Checkpoints**: Legal clearance, editorial review, publication approval
- **Parallel Processing**: OSINT verification while corporate analysis runs
- **Rollback Capability**: Return to any previous investigation state

### Export Capabilities:
- **Newsroom Package**: Markdown brief with inline citations
- **Video Production**: Premiere Pro XML with B-roll suggestions
- **Evidence Bundle**: Encrypted ZIP with source verification
- **Interactive Embed**: JSON package for web integration

## Ethical & Legal Safeguards

### Built-in Protections:
- **Source Protection**: Anonymous tip handling with secure communication
- **Bias Detection**: Automated scanning for communal/hate language
- **Fact-Checking**: Multi-source corroboration requirements
- **Legal Compliance**: Real-time risk assessment with Indian media law

### Editorial Controls:
- **Peer Review**: Multi-agent verification before content generation
- **Editorial Override**: Human veto power at all decision points
- **Retraction Protocol**: Systematic correction and update procedures
- **Transparency**: Complete audit trail for accountability

## Technical File Structure

```
src/a2a_mcp/agents/
├── investigative_orchestrator.py      # Main InvestiGenie orchestrator
├── entity_extraction_agent.py        # spaCy-HI entity recognition
├── corporate_maze_breaker_agent.py   # MCA-21/SEBI analysis
├── osint_verification_agent.py       # Multi-source verification
├── legal_risk_assessment_agent.py    # Indian legal framework
├── content_strategy_agent.py         # Investigative storytelling
└── technical_export_agent.py         # Multi-format export

agent_cards/
├── investigative_orchestrator.json   # InvestiGenie configuration
├── entity_extraction_agent.json      # Entity recognition specs
├── corporate_maze_breaker_agent.json # Corporate analysis specs
├── osint_verification_agent.json     # OSINT verification specs
├── legal_risk_assessment_agent.json  # Legal risk specs
├── content_strategy_agent.json       # Content strategy specs
└── technical_export_agent.json       # Export capabilities specs

databases/
├── init_investigative_database.py    # Investigation domain setup
└── security/
    ├── encryption_manager.py         # AES-256 vault management
    ├── dead_man_switch.py            # Auto-purge mechanisms
    └── audit_trail.py                # Cryptographic integrity
```

## Deployment Configuration

### Security-First Deployment:
- **Port Range**: 10301-10307 (isolated from other systems)
- **Network**: Air-gapped by default, selective VPN for MCP access
- **Storage**: Encrypted vault with hardware TPM sealing
- **Monitoring**: Internal audit trails without external telemetry

### MCP Server Utilization:
- **BrightData**: Corporate data scraping with rate limiting
- **Brave Search**: Cross-reference verification with source validation
- **Puppeteer**: Automated verification workflows
- **Context7**: Legal precedent and entity databases
- **Firecrawl**: Competitive intelligence and research
- **Supabase**: Secure graph storage for complex investigations
- **NotionAI**: Content management and collaboration (secure workspace)

This implementation transforms investigative journalism into a systematic, secure, and ethically-guided process while maintaining the rigor and verification standards essential for credible reporting in the Indian media landscape.