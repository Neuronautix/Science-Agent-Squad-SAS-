# FAIR-NAMs-Squad 🐁🦉⚙️

**An Autonomous Multi-Agent Swarm for Regulatory Science & Alternative Methodologies**

## 🎯 Complete Overview & Objective
The `FAIR-NAMs-Squad` is an advanced Multi-Agent System (MAS) built to accelerate the replacement of animal testing in preclinical pharmacology. The primary goal of this repository is to validate **New Approach Methodologies (NAMs)** and **Virtual Control Groups (VCGs)** by focusing on their critical bottleneck: metadata homogenization. 

Instead of relying on human researchers to manually parse thousands of pages of evolving FDA/EMA guidelines, parse ontologies, and draft technical specs, this repository deploys a "Swarm" of specialized AI Agents. These agents dynamically browse the internet, query scientific databases, validate semantic data structures, and autonomously draft publication-ready regulatory documentation and code schemas.

---

## 🦾 The Squad (AI Personas)
The intelligence of the repository is divided into specialized roles. Rather than one generic AI, the system forces "experts" to debate and logically constrain each other:

| Agent | Icon | Role | Technical Focus |
| :--- | :---: | :--- | :--- |
| **Dr. Nexus** | 👑 | **Orchestrator** | Coordinates the swarm. Synthesizes inputs, resolves conflicts between architecture and ethics, and dictates the core thesis of research. |
| **BioEthos** | 🐁 | **Ethics & Regs** | Ensures all outputs strict adhere to the **3Rs** (Reduction, Replacement, Refinement), EU Directive 2010/63/EU, and current FDA/EMA qualification runways. |
| **Semantica** | 🦉 | **Ontologist** | Enforces the **FAIR Principles** (Findable, Accessible, Interoperable, Reusable). Maps scientific concepts to JSON-LD, RDF, and PROV-O ontology standards. |
| **TechLead** | ⚙️ | **Architect** | Turns Semantica's theoretical ontologies into deployable REST APIs and federated deployment structures (e.g., API Platform, Symfony). |
| **Journalist**| ✍️ | **Observer** | Neutral, professional documentation and reporting. Writes the final Markdown files strictly detailing the observed facts without bias. |

---

## 🗺️ Version 2.0 Architecture (The "Graph")
The squad is no longer just a static chatbot. It runs on a **LangGraph State Machine**, allowing it to autonomously loop its reasoning through actual python-based software tools:

*   **Live Web Intelligence:** The built-in `search_you_engine` Tool connects the agents to the live internet via **You.com's Search API**. The agents can dynamically fetch the latest FDA news or web documentation before writing.
*   **Scientific Literature:** The `search_pubmed` Tool connects the agents directly to the NCBI/PubMed database to cite real, peer-reviewed toxicology literature.
*   **Semantic Validation:** The `check_schema_org` Tool allows agents to programmatically verify if the metadata JSON schemas they are designing actually conform to global web standards.
*   **Persistent File I/O:** The `write_manuscript_section` Tool allows the AI to autonomously create files and write its research outputs natively into the local `./Drafts/` folder on your hard drive.

---

## 🛠️ Best Usage & Quickstart

To utilize the Squad optimally, you no longer just "chat" with it. You assign it programmatic execution tasks via the local CLI.

### 1. Configure the Brain & Eyes
Ensure you have the API keys required to power both the LLM's reasoning engine and the Web Search tools. Create a `.env` file in the root of the repository:
```env
OPENAI_API_KEY=sk-your-openai-key-here     # Powers the LangGraph Brain (gpt-4o)
YOU_API_KEY=your-you-dot-com-key-here      # Powers the Live Search API
```

### 2. Execute an Autonomous Task
Use the Python module exactly like a CLI tool to trigger the swarm. Pass complex, multi-step instructions as your prompt:

```bash
# Run this from the root of the repository
python -m automation.main "Have Dr. Nexus search You.com for the absolute latest updates on EMA Virtual Control Groups, ask Semantica to define a metadata mapping for it, and write the output to disk."
```

### 3. Review the Output
Once the terminal sequence finishes spinning, open the `/Drafts/` folder in the repository. The agents will have autonomously synthesized the real-world data and saved the output as a Markdown file.

---

## 📂 Repository Layout

*   `automation/main.py`: The entry-point for the LangGraph framework.
*   `automation/graph.py`: The State-Machine routing logic dictating how the LLM functions.
*   `automation/tools.py`: The Python functions granting the AI its API capabilities (You.com, PubMed, Disk Read/Write).
*   `schemas/`: Ground-truth executable `.jsonld` reference models designed by the squad.
*   `Drafts/`: The automated output directory for generated papers and summaries.

---

## 🚀 Further Development
The goal is to move beyond writing articles into developing actual microservices. For information on where the project is heading (e.g., automated execution of SHACL validation, automated lineage matrices), please check the [Future Roadmap](Future_Improvements_TODO.md).
