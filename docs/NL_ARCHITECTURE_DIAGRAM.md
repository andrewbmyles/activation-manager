# Natural Language Architecture - Technical Flow

## System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend - React Application"
        UI[User Interface]
        NLB[NL Audience Builder Component]
        VP[Variable Picker Component]
    end
    
    subgraph "API Gateway"
        API[Flask REST API]
    end
    
    subgraph "NL Processing Engine"
        QP[Query Processor]
        CE[Concept Extractor]
        SE[Synonym Expander]
        VS[Variable Scorer]
    end
    
    subgraph "Data Layer"
        VL[Variable Loader<br/>49,323 variables]
        PC[Parquet Cache]
        EM[Embeddings<br/>Semantic Vectors]
    end
    
    subgraph "Enhanced Features"
        CS[Complex Search]
        RF[Refine Engine]
        CAT[Category Manager]
    end
    
    UI --> NLB
    NLB --> API
    API --> QP
    QP --> CE
    CE --> SE
    SE --> VS
    VS --> VL
    VS --> EM
    API --> CS
    API --> RF
    API --> CAT
    VL --> PC
    
    style UI fill:#e3f2fd
    style API fill:#fff9c4
    style VL fill:#e8f5e9
```

## Detailed Component Flow

### 1. Natural Language Query Processing

```mermaid
sequenceDiagram
    participant User
    participant UI as React UI
    participant API as Flask API
    participant NLP as NL Processor
    participant VS as Variable Search
    participant DB as Variable Database
    
    User->>UI: Types "high income millennials"
    UI->>API: POST /api/nl/process
    API->>NLP: Parse query
    NLP->>NLP: Extract concepts:<br/>- income: high<br/>- age: millennials
    NLP->>VS: Search with expanded terms
    VS->>DB: Query 49K variables
    DB->>VS: Return matches
    VS->>VS: Score & rank results
    VS->>API: Formatted results
    API->>UI: JSON response
    UI->>User: Display variables
```

### 2. Enhanced Variable Picker Flow

```mermaid
graph LR
    subgraph "User Query"
        Q[income over 100k]
    end
    
    subgraph "Query Analysis"
        QA1[Numeric Detection: 100k]
        QA2[Concept: income]
        QA3[Modifier: over]
    end
    
    subgraph "Search Strategy"
        S1[Keyword Match:<br/>INCOME_100K_PLUS]
        S2[Semantic Match:<br/>HIGH_NET_WORTH]
        S3[Related Match:<br/>AFFLUENT_HOUSEHOLD]
    end
    
    subgraph "Results"
        R[Ranked Variables<br/>with Relevance Scores]
    end
    
    Q --> QA1
    Q --> QA2
    Q --> QA3
    QA1 --> S1
    QA2 --> S1
    QA2 --> S2
    QA3 --> S3
    S1 --> R
    S2 --> R
    S3 --> R
```

### 3. Variable Refine Process

```mermaid
stateDiagram-v2
    [*] --> InitialSelection: User selects variables
    InitialSelection --> RefineRequest: Clicks "Refine"
    RefineRequest --> AnalyzeContext: System analyzes current selection
    
    AnalyzeContext --> ExpandMode: Mode = Expand
    AnalyzeContext --> FilterMode: Mode = Filter
    AnalyzeContext --> SuggestMode: Mode = Suggest
    
    ExpandMode --> FindSimilar: Find similar variables
    FilterMode --> NarrowDown: Remove less relevant
    SuggestMode --> Recommend: AI recommendations
    
    FindSimilar --> UpdatedResults
    NarrowDown --> UpdatedResults
    Recommend --> UpdatedResults
    
    UpdatedResults --> [*]
```

## Key Components Explained

### Query Processor (`/api/nl/process`)
- **Input**: Natural language text
- **Process**: 
  - Tokenization
  - Concept extraction
  - Intent classification
- **Output**: Structured query object

### Concept Extractor
```python
Concepts Identified:
- Demographics: age, gender, location
- Financial: income, wealth, spending
- Behavioral: interests, activities, purchases
- Psychographic: attitudes, values, lifestyle
```

### Variable Scoring Algorithm
```
Score = (
    Keyword Match Weight × 0.4 +
    Concept Coverage × 0.3 +
    Semantic Similarity × 0.2 +
    Context Relevance × 0.1
)
```

### Enhanced Search Features

```mermaid
graph TD
    subgraph "Search Methods"
        KW[Keyword Search<br/>Fast, exact matches]
        SM[Semantic Search<br/>Concept understanding]
        HY[Hybrid Search<br/>Best of both]
    end
    
    subgraph "Similarity Filtering"
        SF[Remove Duplicates<br/>threshold: 85%]
        GR[Group Related<br/>max 2 per group]
    end
    
    subgraph "Results Enhancement"
        EX[Explanations<br/>Why matched]
        SC[Scores<br/>Relevance 0-1]
        GP[Grouping<br/>By category/theme]
    end
    
    KW --> HY
    SM --> HY
    HY --> SF
    SF --> GR
    GR --> EX
    EX --> SC
    SC --> GP
```

## Data Flow Architecture

```mermaid
graph TD
    subgraph "Data Sources"
        PF[Parquet File<br/>49,323 variables]
        MD[Metadata<br/>Categories, themes]
        EM[Embeddings<br/>Semantic vectors]
    end
    
    subgraph "Memory Cache"
        SC[Shared Cache<br/>30min TTL]
        DF[DataFrame<br/>In-memory]
    end
    
    subgraph "API Endpoints"
        E1[/api/variable-picker/search]
        E2[/api/variable-picker/categories]
        E3[/api/variable-picker/refine]
        E4[/api/nl/process]
    end
    
    PF --> SC
    MD --> SC
    EM --> SC
    SC --> DF
    DF --> E1
    DF --> E2
    DF --> E3
    DF --> E4
```

## Performance Optimizations

1. **Lazy Loading**: Enhanced picker only loads when needed
2. **Shared Cache**: Reduces memory usage across workers
3. **DataFrame Operations**: Fast pandas queries
4. **Pre-computed Indexes**: Lower-case columns for search

## API Response Structure

```json
{
  "results": [...],
  "query_context": {
    "original_query": "high income millennials",
    "concepts": ["income", "age"],
    "expanded_terms": ["affluent", "wealthy", "25-40"]
  },
  "search_methods": {
    "keyword": true,
    "semantic": true
  },
  "total_found": 25
}
```