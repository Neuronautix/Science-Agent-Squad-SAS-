# FAIR-NAMs-Squad: Knowledge Traceability Matrix

This document provides a transparent mapping of how the multi-agent system ingested, interpreted, and deployed the source materials provided by the user into the final article draft. It acts as an audit trail for the squad's reasoning.

| Source Material (Input) | Agent Assigned | Knowledge Extracted | How it was Deployed in Output | Citation Map |
| :--- | :--- | :--- | :--- | :--- |
| `chatGPT-plan.md` | **Dr. Nexus** *(Orchestrator)* | Provided the core thesis: The bottleneck for NAM adoption is metadata standardization, bridging virtual control groups (VCGs) and digital biomarkers. | Structured the 4-phase drafting approach, narrative outline, and the core argumentative spine of the article. | N/A *(Structural)* |
| `EMA draft opinion on VCGs` *(PDF/Link)* | **BioEthos** *(Ethics/Regulatory)* | EMA opened consultation to replace concurrent controls with VCGs in rat non-GLP Dose-Range Finding studies using historical databases. | Served as the primary "regulatory hook" for the Introduction, proving that data-centric models are actively being qualified. | **[1]** |
| `fda-implementing-nams.md` & `fda-announce-to-phase-out.md` | **BioEthos** *(Ethics/Regulatory)* | FDA is explicitly encouraging and implementing a roadmap to reduce animal testing and include Alternative Methods in IND applications. | Anchored the argument that regulatory readiness is already here (Box 1). | **[2]** |
| `NIH-prizes-NAMs.md` | **BioEthos** *(Ethics/Regulatory)* | NIH created a $7M "Reduction to Practice Challenge" specifically to scale NAMs. | Highlighted the massive funding shift driving the field, featured in Box 1. | **[3]** |
| `EU-roadmap-phase-out.md` | **BioEthos** *(Ethics/Regulatory)* | EC planning a directive by Q1 2026 to phase out animal testing for chemical safety. | Reinforced the transatlantic convergence of regulatory pressure. | **[4]** |
| *Live Web Search: VICT3R Consortium* | **Dr. Nexus** *(Orchestrator)* | The VICT3R project is the leading public-private partnership attempting to validate VCGs by utilizing legacy massive toxicity datasets. | Used to ground the concept of VCGs in a real-world, active consortium, while highlighting the difficulty of dataset matching. | **[5]** |
| *(Agent Internal Knowledge Base)*: `FDA SEND Format` | **DataForge** *(Infrastructure)* | The Standard for Exchange of Nonclinical Data (SEND) is structurally tabular and episodic. | DataForge identified SEND as the primary implementation friction point: it is completely antagonistic to continuous longitudinal digital biomarker data. | **[6]** |
| *"Too big to lose - a FAIR repository..."* *(Literature)* | **Semantica** *(Metadata/FAIR)* | Home-cage monitoring digital biomarkers require federated repository architectures that are FAIR-compliant. | Used to argue why centralized pooling won't work due to IP, and why federated MMS architectures are required. | **[7]** |
| `Data welfare is animal welfare- Building a WellFAIR research ecosystem.pdf` | **Semantica & BioEthos** | Making data FAIR is an ethical mandate, because un-reusable data violates the 3Rs (Reduction & Replacement). | Inserted into the "Core Thesis" section to perfectly bridge the gap between animal ethics (BioEthos) and data structure (Semantica). | **[8]** |

## AI Reasoning Process & Epistemic Constraints
To ensure the article maintained scientific rigor and avoided "hallucinations," the squad operated under strict epistemic tags during the drafting phase:
* **[FACT]:** Directly tied to one of the extracted inputs above.
* **[INFERENCE]:** A logical bridge formulated by the agents to connect two distinct facts (e.g., connecting the episodic nature of SEND [6] to the failure of pooling HCM data [7]).
* **[SPECULATION]:** A forward-looking prediction (e.g., VCGs will not immediately replace definitive GLP tox studies), heavily governed by **Reviewer-2's** adversarial safety prompts.
