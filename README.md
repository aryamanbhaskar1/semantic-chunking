# Semantic Chunking for RAG

A Python pipeline for processing and chunking conversation transcripts for retrieval-augmented generation (RAG).

Developed as part of **ImasonsGPT**, an LLM-powered application built through the NYU Business Analytics Club's Machine Learning team. The project focused on improving how expert-interview transcripts are organized and retrieved to provide more relevant context for LLM-generated responses.

## Overview

Traditional fixed-size text splitting can break apart conversations without accounting for speaker changes or contextual boundaries. This project takes a more structured approach, creating retrieval-friendly chunks while preserving important transcript metadata.

The pipeline:

- Normalizes transcript records into a consistent format
- Groups conversation segments into configurable chunks
- Uses speaker changes, timestamp gaps, and source boundaries to determine splitting points
- Preserves overlapping segments between chunks to maintain context
- Retains speaker, source, and timestamp metadata for downstream retrieval

## Chunking Approach

The pipeline uses several configurable rules to control chunk boundaries:

- **Target chunk size:** 300 words
- **Maximum chunk size:** 450 words
- **Speaker-aware splitting:** Splits at speaker changes when chunks reach the target size
- **Timestamp-aware splitting:** Detects extended gaps between conversation segments
- **Context overlap:** Carries over the final two transcript units into subsequent chunks

These settings can be adjusted in `config.py` depending on the structure of the input transcripts.

## Pipeline Architecture

The project is organized into four main components:

- `ingest.py` — Loads JSON or JSONL transcripts and normalizes text and metadata
- `chunker.py` — Implements chunking logic, boundary detection, and overlap
- `config.py` — Defines chunk sizes, splitting rules, and file paths
- `run_pipeline.py` — Runs the full pipeline and exports the resulting chunks

Each output chunk includes its text alongside metadata such as transcript ID, speakers, sources, timestamps, and word count.

## Running the Pipeline

The project uses Python's standard library and requires no additional Python packages.

1. Place a compatible transcript file in the `data/` directory.
2. Update the input and output paths in `config.py` if needed.
3. Run `python run_pipeline.py`.

By default, the pipeline reads `data/dean_rag_chunks.json` and writes the processed chunks to `output/normalized_chunks_v3.json`.

## Related Project

This pipeline was developed for ImasonsGPT, a RAG-based chatbot using Qwen, OpenAI embeddings, and Pinecone vector search.

The application's backend is available in the [chatbot-backend repository](https://github.com/aryamanbhaskar1/chatbot-backend).
