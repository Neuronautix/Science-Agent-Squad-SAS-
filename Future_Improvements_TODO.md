# 🚀 FAIR-NAMs-Squad: Future Development Roadmap

This document outlines the critical next steps to evolve the `FAIR-NAMs-Squad` from a static retrieval-augmented context environment into a fully functional, autonomous Multi-Agent framework with verifiable technical outputs.

## Phase 1: Moving from "Show" to "Implementation"
- [x] **Create the `schemas/` directory in the repository.**
- [x] **Draft the Reference Implementation (`mms_schema_v1.jsonld`).**
  - Translate the tabular "Box 2" MMS from the article draft into a machine-readable JSON-LD schema.
  - Implement PROV-O ontology headers for provenance tracking (for items like Preprocessing Logs).
  - Test validation with standard JSON-LD parsing libraries to prove interoperability.
- [x] **Update Article Draft:** Embed the final GitHub repository URL referencing the new `schemas/` directory to prove to peer-reviewers that the concept is technically grounded.

## Phase 2: Agent Framework Upgrade (LangGraph / CrewAI)
- [x] **Sunset standard LangChain basic pipeline.** Move from `automation/ingest.py` simple vector lookup to an event-driven framework (e.g., LangGraph or CrewAI).
- [x] **Implement Active Tool Calling for Agents.**
  - **Dr. Nexus Tool:** PubMed API or EuropePMC API integration for live programmatic retrieval of peer-reviewed validation pathways.
  - **Semantica Tool:** API hooks to validate generated schemas against `schema.org`.
  - **Scribe Tool:** File I/O capabilities so the agent can write directly to disk iteratively.

## Phase 3: Automated Lineage & Epistemic Tracking
- [x] **Enforce JSON-structured Retriever Outputs.** Modify the system prompt for retrieval chains so the LLM must output knowledge facts in strict JSON: `{"fact": "...", "source": "...", "epistemic_tag": "[FACT]"}`.
- [x] **Automate the Traceability Matrix.** Write a python script or independent agent that hooks into the LangGraph state to automatically compile the `Knowledge_Traceability_Matrix.md` post-execution, entirely removing manual intervention.

## Phase 4: State-Machine Manuscript Assembly
- [x] **Implement a JSON State Object for Drafting.** Switch the drafting pipeline from a single massive prompt to a resilient state machine: `{"abstract": "", "intro": "", "methods": ""}`.
- [x] **Build Section-by-Section Adversarial Checkpoints.** Program the `Reviewer-2` agent to automatically block state progression until specific negative constraints (e.g., "no hyping digital biomarkers") are passed on a per-section basis, resolving context-window bloat when writing larger research papers.
