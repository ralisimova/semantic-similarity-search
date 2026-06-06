# Semantic Similarity Search - Knowledge Graph Demo

A semantic similarity search engine built on top of a Wikidata knowledge graph, with an interactive web interface for exploring geographic entities and their relationships.

## Overview

This project leverages semantic similarity algorithms to search and explore a geographic knowledge graph derived from Wikidata. It combines multiple similarity metrics to provide intelligent entity matching and relationship discovery.

## Features

- **Semantic Search**: Find entities based on semantic similarity using WordNet and Sematch algorithms
- **Interactive Web UI**: Streamlit-based interface for exploring the knowledge graph
- **Graph Visualization**: Interactive network visualization of entity relationships
- **Knowledge Graph Construction**: Build and process Wikidata subgraphs from raw triple data
- **Multi-method Similarity**: 
  - WordNet similarity for text-based comparisons
  - Entity semantic similarity using Wikidata/DBpedia mappings
  - Label-based semantic search over graph nodes

## Installation

### Prerequisites
- Python 3.10 or higher
- pip or conda
- a downloaded dataset[https://www.kaggle.com/datasets/alexrenz/wikidata5m] in the `data/raw folder`

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ralisimova/semantic-similarity-search.git
cd semantic-similarity-search
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate.ps1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Building the Knowledge Graph

Process raw Wikidata triples to create the knowledge graph:

```bash
python build_graph.py
```

This script:
- Loads Wikidata triples from `data/raw/`
- Filters for geographic entities and relationships
- Fetches entity labels via SPARQL
- Generates the processed graph in `data/processed/geo_graph_v2.gpickle`

### Running the Web Application

Start the interactive Streamlit application:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Features in the Web UI:**
- Compare two entities by multiple similarity metrics
- Search for entities by semantic similarity
- View entity properties and relationships
- Explore the graph with interactive visualization