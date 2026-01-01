# Computer Science Course Exercise Generation based on Retrieval-Augmented Generation

## Overview
This capstone project implements a **GraphRAG (Graph-based Retrieval-Augmented Generation)** system for automatically generating high-quality Computer Science exam questions. The system leverages knowledge graph structures to create multi-hop reasoning questions that require synthesizing information from multiple sources.

## Key Features

### 1. **Knowledge Graph Construction**
- Builds semantic knowledge graphs from multiple CS textbooks
- Extracts topics and creates bidirectional edges between related concepts
- Supports 20+ textbooks with automated node and edge creation

### 2. **Comparative Retrieval Systems**
- **Baseline Retriever**: Standard keyword-based matching (flat RAG)
- **Graph Retriever**: Traverses knowledge graph using seed nodes and multi-hop expansion

### 3. **Question Generation**
- Uses DeepSeek LLM API for generating multiple-choice questions
- Baseline: Single-chunk context questions
- GraphRAG: Multi-hop questions requiring concept synthesis

### 4. **Automated Evaluation**
Evaluates generated questions on 4 metrics:
- **Relevance**: Topic alignment
- **Faithfulness**: Answer support from context
- **Integration**: Multi-hop reasoning requirement (GraphRAG focus)
- **Complexity**: Depth of reasoning required

### 5. **Logging & Artifacts**
- Detailed experiment logs with timestamped results
- JSON artifacts for each generated question (baseline + GraphRAG)
- Summary statistics comparing baseline vs GraphRAG performance

## Project Structure

```
capstone_project/
├── graphrag_mvp.py                      # Main pipeline implementation
├── GraphRAG-Bench/                      # Dataset of CS textbooks
│   ├── textbooks/                       # 20 structured JSON textbooks
│   │   ├── textbook1/
│   │   ├── textbook2/
│   │   └── ... (textbook3-20)
│   └── questions/                       # Question templates (FB, MC, MS, OE, TF)
├── experiment_logs_v4/                  # Latest experiment results
│   ├── experiment_log.txt               # Detailed execution log
│   └── generated_questions/             # JSON artifacts per topic
│       ├── recursion_baseline.json
│       ├── recursion_graphrag.json
│       └── ... (other topics)
└── README.md                            # This file
```

## Installation

### Prerequisites
- Python 3.7+
- DeepSeek API key ([Get one here](https://platform.deepseek.com/api_keys))

### Dependencies
```bash
pip install openai
```

### Optional (for enhanced baseline)
```bash
pip install sentence-transformers numpy
```

### 🔐 API Key Configuration

**Important:** For security reasons, API keys should be stored as environment variables, not hardcoded in source files.

**Method 1: Environment Variable (Recommended)**
```bash
export DEEPSEEK_API_KEY='your-api-key-here'
python graphrag_mvp.py
```

**Method 2: Create a local .env file (Advanced)**
```bash
# Create .env file (this file is gitignored and won't be committed)
echo "DEEPSEEK_API_KEY='your-api-key-here'" > .env

# Load environment variables before running
source .env
python graphrag_mvp.py
```

> ⚠️ **Security Note**: Never commit API keys to version control. The `.gitignore` file is configured to exclude `.env` files and other sensitive data.

## Usage

### Quick Start

1. **Set your API key:**
   ```bash
   export DEEPSEEK_API_KEY='your-api-key-here'
   ```

2. **Run the experiment:**
   ```bash
   python graphrag_mvp.py
   ```

3. **View results:**
   - Console output shows real-time progress and scores
   - Detailed logs: `experiment_logs_v4/experiment_log.txt`
   - Generated questions: `experiment_logs_v4/generated_questions/`

### Basic Execution
```bash
python graphrag_mvp.py
```

### Configuration
The main pipeline automatically loads the API key from the `DEEPSEEK_API_KEY` environment variable. 

**Topics can be customized** by editing the `main()` function in `graphrag_mvp.py`:

```python
topics = [
    "recursion", 
    "sorting algorithm", 
    "graph traversal",
    "dynamic programming", 
    "hash table"
]

# Output directory for experiment results
output_dir = "./experiment_logs_v4"
```

## Experiment Results

### Sample Output
```
============================================================
Starting Experiment
============================================================

>>> Topic 1/5: recursion
   [Baseline] Retrieving 'recursion': Found 8 nodes.
   [GraphRAG] Found 3 seed nodes for 'recursion'.
   
   [BASELINE] Score: 0.45 (Rel: 0.9, Faith: 0.8, Integ: 0.1, Comp: 0.3)
   Q: What is the primary characteristic of a recursive function?
   
   [GRAPHRAG] Score: 0.78 (Rel: 0.9, Faith: 0.9, Integ: 0.8, Comp: 0.7)
   Q: How does memoization in dynamic programming relate to recursion optimization?

============================================================
Final Summary
============================================================
Baseline Avg: 0.423
GraphRAG Avg: 0.701
Improvement:  +0.278
```

## Key Components

### 1. `SimpleKnowledgeGraph`
- **Nodes**: Textbook chunks with metadata
- **Edges**: Sequential (follows) + Semantic (shares_topic)
- **Topic Index**: Fast lookup for concept-related nodes

### 2. `GraphRetriever`
- Seed node identification via topic matching
- Multi-hop BFS traversal (default: 2 hops)
- Neighbor sampling to prevent explosion

### 3. `AutomatedEvaluator`
- LLM-as-Judge evaluation framework
- Weighted scoring emphasizing Integration (40%) and Complexity (30%)
- JSON-formatted output for analysis

## Evaluation Metrics

| Metric       | Weight | Description                                    |
|--------------|--------|------------------------------------------------|
| Relevance    | 10%    | Does the question address the target topic?    |
| Faithfulness | 20%    | Is the answer supported by retrieved context?  |
| Integration  | 40%    | Requires synthesizing multiple sources?        |
| Complexity   | 30%    | Demands deep reasoning vs. simple recall?      |

**Overall Score** = Weighted sum of all metrics

## Research Hypothesis

**H1**: GraphRAG generates questions with **higher Integration scores** than baseline (multi-hop reasoning).

**H2**: GraphRAG produces **more complex questions** requiring concept synthesis.

**H3**: GraphRAG maintains **comparable Faithfulness** to baseline (factual accuracy).

## Dataset

### GraphRAG-Bench
The project uses the **GraphRAG-Bench** dataset, which contains:
- **20 Computer Science textbooks** covering topics like algorithms, data structures, complexity theory
- **Structured JSON format** with metadata (chapter, section, content)
- **Question templates** in 5 formats:
  - **MC** (Multiple Choice)
  - **TF** (True/False)
  - **FB** (Fill in the Blank)
  - **MS** (Multiple Selection)
  - **OE** (Open Ended)

All textbook data is included in the `GraphRAG-Bench/textbooks/` directory.

## Future Enhancements

1. **Advanced Graph Construction**
   - Entity extraction and coreference resolution
   - Typed edges (prerequisite, contrast, example)

2. **Retrieval Optimization**
   - Hybrid retrieval (vector + graph)
   - Personalized PageRank for node ranking

3. **Question Diversity**
   - Support for True/False, Fill-in-the-Blank
   - Difficulty level control

4. **Human Evaluation**
   - Expert annotation for ground truth
   - Inter-rater agreement analysis

## Author
- **Name**: CZYZCC
- **Email**: 22102947d@connect.polyu.hk
- **Institution**: The Hong Kong Polytechnic University
- **Project Type**: Capstone Project (Computer Science)

## Repository
- **GitHub**: [Capstone Project - GraphRAG Question Generation](https://github.com/CZYZCC/Captone-Project-Computer-Science-Course-Exercise-Generation-based-on-Retrieval-Augmented-Generation)
- **Latest Update**: January 2, 2026

## License
This project is for academic purposes only.

## Acknowledgments
- **GraphRAG-Bench** dataset for CS textbooks
- **DeepSeek** for LLM API access
- Research on Graph-based Retrieval-Augmented Generation methodologies

## Security & Best Practices

### API Key Management
- ✅ API keys are loaded from environment variables
- ✅ `.gitignore` configured to exclude sensitive files
- ✅ No hardcoded credentials in source code

### Recommended Tools
- **GitGuardian**: Monitor repository for exposed secrets ([Setup Guide](https://dashboard.gitguardian.com/))
- **Pre-commit hooks**: Prevent accidental credential commits

---

*Last Updated: January 2, 2026*
