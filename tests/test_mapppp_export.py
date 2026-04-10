import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from automation.exporters.mapppp import HCM_METADATA_PERSONA, export_hcm_mapppp_bundle


def _collect_keys(value):
    keys = set()
    if isinstance(value, dict):
        keys.update(value.keys())
        for item in value.values():
            keys.update(_collect_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_collect_keys(item))
    return keys


def _write_hcm_fixture_files(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    config_text = """
swarm:
  name: "HCMSAS"
  description: >
    Home Cage Monitoring Scientific Agent Squad.
    Investigates preclinical home cage monitoring research with emphasis on MNMS.
  output_dir: "./Drafts/HCMSAS"
  traceability_matrix: "./Knowledge_Traceability_Matrix_HCMSAS.md"

personas:
  - name: "Metadata Architect"
    role: "MNMS extraction and metadata structure mapping"
  - name: "Reproducibility and Bias Auditor"
    role: "Comparability and confounder review"

output_sections:
  - "A. Research scope"
  - "B. Key evidence summary"
  - "C. Evidence table with in-text citations"
  - "D. HCM MNMS mapping table"
  - "E. Missing metadata and ambiguity report"
  - "F. Knowledge graph schema proposal"
  - "G. Reproducibility and comparability risks"
  - "H. Conservative conclusions"
  - "I. References"
"""
    config_path = tmp_path / "swarm_config_hcmsas.yml"
    config_path.write_text(config_text.strip() + "\n", encoding="utf-8")

    matrix_text = """# HCMSAS Knowledge Traceability Matrix

## Traceability Log

| claim_id | claim | epistemic_tag | source | agent | mnms_category | notes | status |
|---|---|---|---|---|---|---|---|
| HCM-000 | Matrix initialized for HCMSAS swarm | [FACT] | internal | HCMSAS_DrNexus | provenance_and_versioning | Baseline entry | active |

---

*Append new entries below this line.*
| HCM-001 | Continuous cage-side HCM can capture circadian locomotor activity in mice [1] | [FACT] | DOI:10.1000/hcm.methods.2024 | Metadata Architect | temporal_structure | Anchored to the methods paper. | active |
| HCM-002 | Cross-platform comparisons require explicit sensor equivalence [2] | [INFERENCE] | DOI:10.1000/hcm.review.2025 | Reproducibility and Bias Auditor | acquisition_system | Comparability risk noted in the review. | active |
"""
    matrix_path = tmp_path / "Knowledge_Traceability_Matrix_HCMSAS.md"
    matrix_path.write_text(matrix_text, encoding="utf-8")

    draft_text = """## A. Research scope
This HCMSAS report focuses on preclinical home cage monitoring in mice [1].

## B. Key evidence summary
- [FACT] Automated HCM systems differ by sensor modality and classifier stack [1].

## C. Evidence table with in-text citations
| claim | evidence_type | source_anchor | notes |
|---|---|---|---|
| [FACT] Continuous cage-side recording can capture circadian locomotor activity in mice [1] | methods_paper | DOI:10.1000/hcm.methods.2024 | Preserves the raw measurement versus interpretation distinction. |
| [INFERENCE] Cross-platform comparisons require explicit sensor equivalence [2] | review | DOI:10.1000/hcm.review.2025 | Sensor modality and classifier equivalence must be reported. |

## D. HCM MNMS mapping table
| metadata_field | value_or_status | MNMS_category | classification | source | notes |
|---|---|---|---|---|---|
| species | mouse | animal_characteristics | MNMS_core | DOI:10.1000/hcm.methods.2024 | Reported as C57BL/6J mice [1]. |
| classifier_version | missing | software_and_classifier | missing_in_source | DOI:10.1000/hcm.review.2025 | Review flags missing version disclosure [2]. |

## E. Missing metadata and ambiguity report
- [MISSING] Light cycle transition timing was not reported [1].
- [CONTESTED] Software classifier version disclosure remains inconsistent across HCM platforms [2].

## F. Knowledge graph schema proposal
| subject | predicate | object | evidence_level | confidence | source_id | notes |
|---|---|---|---|---|---|---|
| Study_001 | uses_system | HCM_System_DVC | [FACT] | medium | DOI:10.1000/hcm.methods.2024 | System provenance retained [1]. |
| HCM_System_DVC | confounded_by | Classifier_Version_Gap | [INFERENCE] | low | DOI:10.1000/hcm.review.2025 | Missing classifier version weakens comparability [2]. |

## G. Reproducibility and comparability risks
| risk_id | category | severity | description | affected_studies | recommended_action |
|---|---|---|---|---|---|
| R1 | software_and_classifier | Major | Classifier versions were omitted, limiting reproducibility [2]. | Study_001 | Require explicit software version reporting. |

## H. Conservative conclusions
[INFERENCE] HCM exports should remain proposal-level until curator review [1][2].

## I. References
[1] Example Methods Consortium. Continuous HCM methods paper. 2024.
[2] Example Review Group. HCM comparability review. 2025.
"""
    draft_path = tmp_path / "hcm_report.md"
    draft_path.write_text(draft_text, encoding="utf-8")

    review_notes = [
        {
            "persona": HCM_METADATA_PERSONA,
            "note": "Keep MNMS mappings proposal-level because several core fields remain missing [1].",
            "note_type": "mnms_review",
            "source_anchor": "DOI:10.1000/hcm.methods.2024",
            "citations": ["[1]"],
        },
        {
            "persona": "Reviewer-2",
            "note": "Do not mark classifier-version mappings as accepted or curator-confirmed [2].",
            "note_type": "reviewer_feedback",
            "source_anchor": "DOI:10.1000/hcm.review.2025",
            "citations": ["[2]"],
        },
    ]
    notes_path = tmp_path / "review_notes.json"
    notes_path.write_text(json.dumps(review_notes, indent=2), encoding="utf-8")

    return config_path, matrix_path, draft_path, notes_path


def test_export_hcm_mapppp_bundle_emits_canonical_shape(tmp_path: Path):
    config_path, matrix_path, draft_path, notes_path = _write_hcm_fixture_files(tmp_path)

    bundle = export_hcm_mapppp_bundle(
        config_path=config_path,
        draft_path=draft_path,
        traceability_matrix_path=matrix_path,
        review_notes_path=notes_path,
    )

    assert bundle.package_metadata.swarm_name == "HCMSAS"
    assert bundle.study_context is not None
    assert bundle.study_context.domain == "preclinical home cage monitoring"
    assert bundle.study_context.species == "mouse"
    assert bundle.study_context.standards == ["MNMS"]

    assert bundle.metadata_assertions
    assert bundle.evidence_assertions
    assert bundle.mapping_assertions
    assert bundle.graph_assertions
    assert bundle.review_notes

    for collection in (
        bundle.metadata_assertions,
        bundle.evidence_assertions,
        bundle.mapping_assertions,
        bundle.graph_assertions,
        bundle.review_notes,
    ):
        assert all(item.status == "proposed" for item in collection)

    assert any(
        anchor.source_id == "DOI:10.1000/hcm.methods.2024"
        and "[1]" in anchor.citation_markers
        for assertion in bundle.evidence_assertions
        for anchor in assertion.source_anchors
    )
    assert any(
        assertion.assertion_id.startswith("traceability-evidence-")
        for assertion in bundle.evidence_assertions
    )
    assert any(mapping.classification == "MNMS_core" for mapping in bundle.mapping_assertions)
    assert any(
        graph.subject == "Study_001" and graph.predicate == "uses_system"
        for graph in bundle.graph_assertions
    )
    assert any(assertion.epistemic_label == "fact" for assertion in bundle.evidence_assertions)
    assert any(assertion.epistemic_label == "missing" for assertion in bundle.metadata_assertions)
    risk_note = next(note for note in bundle.review_notes if note.note_id == "risk-note-1-1")
    assert risk_note.source_anchors
    assert risk_note.source_anchors[0].source_id == "[2]"
    assert risk_note.disposition == "flag"
    assert all(anchor.source_id != "Study_001" for anchor in risk_note.source_anchors)
    assert any(note.persona == "Reviewer-2" for note in bundle.review_notes)
    assert any(note.disposition == "request_changes" for note in bundle.review_notes)

    payload = bundle.model_dump(mode="json")
    top_level_keys = set(payload)
    assert "mapping_assertions" in top_level_keys
    assert "graph_assertions" in top_level_keys
    assert "candidate_mnms_mappings" not in top_level_keys
    assert "candidate_graph_assertions" not in top_level_keys

    legacy_keys = _collect_keys(payload)
    assert "proposal_level" not in legacy_keys
    assert "accepted" not in legacy_keys
    assert "curator_confirmed" not in legacy_keys
    assert "note_type" not in legacy_keys

    json.dumps(payload)


def test_export_hcm_mapppp_bundle_raises_for_missing_explicit_review_notes_path(tmp_path: Path):
    config_path, matrix_path, draft_path, _ = _write_hcm_fixture_files(tmp_path)

    missing_notes_path = tmp_path / "missing-review-notes.json"

    try:
        export_hcm_mapppp_bundle(
            config_path=config_path,
            draft_path=draft_path,
            traceability_matrix_path=matrix_path,
            review_notes_path=missing_notes_path,
        )
    except FileNotFoundError as exc:
        assert str(missing_notes_path) in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError for missing explicit review notes path")


def test_export_mapppp_hcm_cli_writes_bundle_json(tmp_path: Path):
    pytest.importorskip("langgraph")
    from automation.main import app

    config_path, matrix_path, draft_path, notes_path = _write_hcm_fixture_files(tmp_path)
    output_path = tmp_path / "mapppp_bundle.json"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "export",
            "mapppp-hcm",
            "--config-path",
            str(config_path),
            "--draft-path",
            str(draft_path),
            "--traceability-matrix",
            str(matrix_path),
            "--review-notes-path",
            str(notes_path),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["package_metadata"]["swarm_name"] == "HCMSAS"
    assert payload["graph_assertions"][0]["status"] == "proposed"
    assert payload["review_notes"][-1]["persona"] == "Reviewer-2"
    assert payload["review_notes"][-1]["disposition"] == "request_changes"
