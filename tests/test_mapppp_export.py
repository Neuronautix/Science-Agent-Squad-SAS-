import json
from pathlib import Path

from typer.testing import CliRunner

from automation.exporters.mapppp import export_hcm_mapppp_bundle
from automation.main import app


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_hcm_fixture_files(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    config_path = REPO_ROOT / "swarm_config_hcmsas.yml"

    matrix_text = (REPO_ROOT / "Knowledge_Traceability_Matrix_HCMSAS.md").read_text(encoding="utf-8")
    matrix_text += (
        "| HCM-001 | [FACT] Continuous cage-side HCM can capture circadian locomotor activity in mice [1] | "
        "[FACT] | DOI:10.1000/hcm.methods.2024 | Metadata Architect | temporal_structure | "
        "Anchored to the methods paper. | active |\n"
        "| HCM-002 | [INFERENCE] Cross-platform comparisons require explicit sensor equivalence [2] | "
        "[INFERENCE] | DOI:10.1000/hcm.review.2025 | Reproducibility and Bias Auditor | acquisition_system | "
        "Comparability risk noted in the review. | active |\n"
    )
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
            "persona": "Metadata Architect",
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


def test_export_hcm_mapppp_bundle_preserves_traceability_and_proposal_status(tmp_path: Path):
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
    assert bundle.candidate_mnms_mappings
    assert bundle.candidate_graph_assertions
    assert bundle.review_notes

    for collection in (
        bundle.metadata_assertions,
        bundle.evidence_assertions,
        bundle.candidate_mnms_mappings,
        bundle.candidate_graph_assertions,
        bundle.review_notes,
    ):
        assert all(item.proposal_level == "proposal" for item in collection)
        assert all(item.accepted is False for item in collection)
        assert all(item.curator_confirmed is False for item in collection)

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
    assert any(mapping.classification == "MNMS_core" for mapping in bundle.candidate_mnms_mappings)
    assert any(
        graph.subject == "Study_001" and graph.predicate == "uses_system"
        for graph in bundle.candidate_graph_assertions
    )
    assert any(note.persona == "Reviewer-2" for note in bundle.review_notes)

    json.dumps(bundle.model_dump(mode="json"))


def test_export_mapppp_hcm_cli_writes_bundle_json(tmp_path: Path):
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
    assert payload["candidate_graph_assertions"][0]["accepted"] is False
    assert payload["review_notes"][-1]["persona"] == "Reviewer-2"
