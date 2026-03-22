# Getting Started

## Activate Environment

```bash
python3 -m venv env
source env/bin/activate
```

## Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Run the App

```bash
python3 main.py
```

# Files and Folders

- `/knowledge-base` - Folder containing the MD files
- `ingest.py` - Ingests documents into the vector database
- `state.py` - State class
- `rag.py` - RAG implementation
- `nodes.py` - Node definitions
- `validators.py` - Validation functions
- `helpers.py` - Helper functions
- `main.py` - Entry point of the application
- `Insurance RAG Chatbot Flowchart.png` - Lucidchart flowchart that served as guide
- `graph.png` - Graph generated from code in `main.py`. Also a guide
