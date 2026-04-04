# PIU Psych Swarm

A configurable multi-agent framework for psychiatric research on problematic internet use.

> The repository is preconfigured for psychiatric and behavioral-science work on problematic internet use, while remaining configurable for other research domains.

## Focus

PIU Psych Swarm is a LangGraph-based multi-agent system that researches, debates, and documents psychiatric questions about problematic internet use, including internet gaming disorder where relevant.

The repository is currently optimized for:

- clinically cautious synthesis that separates high engagement from impairment
- literature-backed summaries with in-text citations and references
- reusable local knowledge bases for subagent-specific expertise
- structured drafting workflows for reviews, evidence briefs, and study notes

## Quickstart

```bash
git clone https://github.com/dhuzard/piu-psych-swarm.git
cd piu-psych-swarm
make setup
make ingest
make run PROMPT="Review the psychiatric literature on problematic internet use in adolescents, including prevalence, comorbidity, mechanisms, and interventions."
```

## Persona Squad

| Agent | Icon | Role | Technical Focus |
| :--- | :--- | :--- | :--- |
| Dr. Nexus | 👑 | Orchestrator | Coordination, synthesis, and reference management |
| ClinicalPsych | 🧠 | Clinical specialist | Diagnosis, impairment, and comorbidity |
| EpiScope | 📊 | Epidemiology specialist | Prevalence, psychometrics, risk and protective factors |
| NeuroCogs | 🧪 | Mechanisms specialist | Reward, executive control, neurocognition, imaging |
| CarePath | 🛟 | Intervention specialist | Prevention, treatment, and care pathways |
| Journalist | ✍️ | Scribe | Neutral, professional documentation and reporting |

## Typical Workflow

```bash
make ingest
make info
make run PROMPT="Create a scoping review outline for problematic internet use in university students."
```

Useful working files:

- Drafts/piu_prompt_set.md
- Drafts/piu_study_workflow_template.md
- Article_Draft.md
- Knowledge_Traceability_Matrix.md

## Core Tooling

| Tool | Purpose |
| :--- | :--- |
| search_pubmed | Search peer-reviewed biomedical and psychiatric literature |
| search_you_engine | Search the live web |
| search_knowledge_base | Search local PIU literature packets in agents/*/KB/ |
| scrape_webpage | Pull full-text content from URLs |
| append_traceability_matrix | Log evidence and epistemic status |
| write_manuscript_section | Write markdown outputs into Drafts/ |

## Repository Layout

- swarm_config.yml: Active swarm definition
- agents/: Personas and local knowledge bases
- automation/: Runtime, tools, ingestion, and graph logic
- Drafts/: Prompt packs, workflow templates, and generated outputs
- Knowledge_Traceability_Matrix.md: Running audit trail for evidence use

## Notes

- The active team is controlled by swarm_config.yml.
- KB ingestion and KB search now follow the configured personas rather than every folder under agents/.
- The repository is currently curated for PIU-focused psychiatric research workflows.
