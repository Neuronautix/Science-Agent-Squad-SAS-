# Quickstart: Run the PIU Psych Swarm

This guide takes you from clone to first run for a psychiatric literature workflow focused on problematic internet use.

## Prerequisites

- Python 3.10+
- An OpenAI API key, or another supported provider key if you retarget the model config
- Optional: a You.com API key for live web search

## Step 1: Clone and Setup

```bash
git clone https://github.com/dhuzard/piu-psych-swarm.git
cd piu-psych-swarm
make setup
```

## Step 2: Add API Keys

Set the required keys in .env.

```env
OPENAI_API_KEY=sk-your-key
YOU_API_KEY=your-you-key
```

## Step 3: Build the Local Knowledge Base

```bash
make ingest
```

This vectorizes the active personas' KB folders so local literature notes are searchable.

## Step 4: Verify the Active Team

```bash
make info
```

You should see the PIU team: Dr. Nexus, ClinicalPsych, EpiScope, NeuroCogs, CarePath, and Journalist.

## Step 5: Run a First PIU Task

```bash
make run PROMPT="Review the psychiatric literature on problematic internet use in adolescents, including prevalence, comorbidity, mechanisms, and interventions."
```

## Ready-to-Use Prompt Ideas

```bash
make run PROMPT="Compare problematic internet use and internet gaming disorder as psychiatric constructs, including diagnostic cautions."
make run PROMPT="Draft a neutral evidence brief on problematic internet use and sleep disturbance in adolescents."
make run PROMPT="Create a literature map of problematic internet use among university students, including prevalence, depression, anxiety, and interventions."
```

## Key Working Files

- Drafts/piu_prompt_set.md
- Drafts/piu_study_workflow_template.md
- Article_Draft.md
- Knowledge_Traceability_Matrix.md

## Troubleshooting

| Problem | Solution |
| :--- | :--- |
| CONFIG ERROR | Ensure swarm_config.yml exists and is valid |
| ENV ERROR | Add required API keys to .env |
| No Knowledge Base found | Run make ingest |
| Tool import failures | Run make setup again or install missing dependencies into .venv |
