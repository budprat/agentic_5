# Framework Component Architecture Diagram

## Research Orchestrator System Component Integration

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Interactive Chat Demo]
        CLI[CLI Interface]
    end

    subgraph "Orchestration Layer"
        RO[Research Orchestrator<br/>StandardizedAgentBase]
        AE[Agent Executor]
        AR[Agent Runner]
        PW[Parallel Workflow]
    end

    subgraph "Agent Layer"
        LRA[Literature Review Agent<br/>StandardizedAgentBase]
        FUA[Future Agents<br/>Patent/Grant/etc]
    end

    subgraph "A2A-MCP Framework Components"
        A2AP[A2A Protocol]
        ACP[A2A Connection Pool]
        QF[Quality Framework]
        RF[Response Formatter]
        OB[Observability]
        MC[Metrics Collector]
    end

    subgraph "Intelligence Services"
        CT[Citation Tracker]
        RI[Reference Intelligence]
        MCP[MCP Tools]
    end

    subgraph "Google ADK Components"
        ADK[LlmAgent]
        MCPT[MCPToolset]
        RUN[Runner]
        SES[Sessions]
    end

    subgraph "External Services"
        ARX[ArXiv API]
        SS[Semantic Scholar]
        BG[Brightdata]
    end

    %% User interactions
    UI --> RO
    CLI --> RO

    %% Orchestrator connections
    RO --> AE
    RO --> AR
    RO --> PW
    RO --> A2AP
    RO --> QF
    RO --> RF
    RO --> OB
    RO --> MC

    %% Agent connections
    RO --> LRA
    RO --> FUA
    LRA --> CT
    LRA --> RI
    LRA --> MCP

    %% Framework integrations
    A2AP --> ACP
    AE --> A2AP
    AR --> OB
    PW --> MC

    %% ADK integrations
    RO -.-> ADK
    LRA -.-> ADK
    ADK --> MCPT
    ADK --> RUN
    ADK --> SES

    %% External connections
    RI --> ARX
    RI --> SS
    MCP --> BG

    %% Styling
    classDef a2a fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef adk fill:#2196F3,stroke:#1565C0,color:#fff
    classDef agent fill:#FF9800,stroke:#E65100,color:#fff
    classDef service fill:#9C27B0,stroke:#6A1B9A,color:#fff
    classDef external fill:#F44336,stroke:#C62828,color:#fff

    class RO,LRA,FUA agent
    class A2AP,ACP,QF,RF,OB,MC,CT,RI a2a
    class ADK,MCPT,RUN,SES adk
    class MCP,AE,AR,PW service
    class ARX,SS,BG external
```

## Component Communication Flow

### 1. **Request Flow**
```
User → Research Orchestrator → Quality Validation → Agent Executor → Literature Review Agent
```

### 2. **Response Flow**
```
Literature Review Agent → Citation Tracker → Response Formatter → Quality Check → User
```

### 3. **Parallel Execution Flow**
```
Orchestrator → Parallel Workflow → [Multiple Agents] → Result Aggregation → Response
```

### 4. **Intelligence Flow**
```
Reference Intelligence → [ArXiv, Semantic Scholar] → Deduplication → Quality Filter → Results
```

## Key Integration Points

### 1. **StandardizedAgentBase**
- Bridge between A2A-MCP and Google ADK
- Inherits from both frameworks
- Provides unified interface

### 2. **Quality Framework**
- Validates all agent outputs
- Academic domain metrics
- Real-time scoring

### 3. **A2A Protocol**
- Inter-agent communication
- Async message passing
- Connection pooling

### 4. **Observability**
- OpenTelemetry tracing
- Performance metrics
- Error tracking

### 5. **Reference Intelligence**
- Multi-source aggregation
- Parallel searching
- Quality filtering

## Data Flow Examples

### Example 1: Literature Search
```
1. User Query → Research Orchestrator
2. Orchestrator → A2A Protocol → Literature Review Agent
3. Literature Agent → Reference Intelligence → ArXiv API
4. ArXiv Results → Citation Tracker → Quality Validation
5. Validated Results → Response Formatter → User
```

### Example 2: Quality Validation
```
1. Agent Response → Quality Framework
2. Calculate Scores (confidence, evidence, rigor)
3. Compare Against Thresholds
4. Approve/Reject → Add Metadata
5. Return Enhanced Response
```

### Example 3: Parallel Research
```
1. Complex Query → Orchestrator
2. Task Decomposition → Parallel Workflow
3. Concurrent Execution:
   - Literature Review → ArXiv
   - Patent Search → USPTO (future)
   - Grant Search → NSF (future)
4. Result Aggregation → Quality Check
5. Unified Response → User
```