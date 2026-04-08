"""MAPPPP proposal-only export support for downstream packaging."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

_CITATION_RE = re.compile(r"\[(\d+)\]")
_SECTION_RE = re.compile(r"^\s{0,3}(?:##|#)\s+([A-I])\.\s+(.+?)\s*$", re.MULTILINE)
_KNOWN_EPISTEMIC_TAGS = [
    "[FACT]",
    "[INFERENCE]",
    "[SPECULATION]",
    "[MISSING]",
    "[MISSING SOURCE]",
    "[PLATFORM-SPECIFIC]",
    "[CONTESTED]",
]
_TRACEABILITY_HEADERS = [
    "claim_id",
    "claim",
    "epistemic_tag",
    "source",
    "agent",
    "mnms_category",
    "notes",
    "status",
]

HCM_METADATA_PERSONA = "Metadata Architect"
HCM_RISK_PERSONA = "Reproducibility and Bias Auditor"


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _extract_citations(text: str) -> list[str]:
    return _unique([f"[{match}]" for match in _CITATION_RE.findall(text or "")])


def _extract_epistemic_tags(text: str) -> list[str]:
    return [tag for tag in _KNOWN_EPISTEMIC_TAGS if tag in (text or "")]


def _normalise_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")


def _parse_markdown_table(lines: list[str]) -> list[dict[str, str]]:
    if len(lines) < 2:
        return []

    headers = [cell.strip() for cell in lines[0].strip().strip("|").split("|")]
    if not headers or all(not header for header in headers):
        return []

    rows: list[dict[str, str]] = []
    for raw_line in lines[2:]:
        if not raw_line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in raw_line.strip().strip("|").split("|")]
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        row = {
            _normalise_header(header): cells[index]
            for index, header in enumerate(headers)
        }
        if any(value for value in row.values()):
            rows.append(row)
    return rows


def _extract_markdown_tables(text: str) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    block: list[str] = []

    for line in (text or "").splitlines():
        if line.strip().startswith("|"):
            block.append(line)
            continue
        if block:
            parsed = _parse_markdown_table(block)
            if parsed:
                tables.append(parsed)
            block = []

    if block:
        parsed = _parse_markdown_table(block)
        if parsed:
            tables.append(parsed)

    return tables


def _extract_bullets(text: str) -> list[str]:
    bullets: list[str] = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def _split_sections(markdown_text: str) -> dict[str, str]:
    matches = list(_SECTION_RE.finditer(markdown_text or ""))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        sections[match.group(1)] = markdown_text[start:end].strip()
    return sections


def _parse_references(section_text: str) -> dict[str, str]:
    references: dict[str, str] = {}
    for line in (section_text or "").splitlines():
        stripped = line.strip()
        bracket_match = re.match(r"^(\[\d+\])\s+(.*)$", stripped)
        if bracket_match:
            references[bracket_match.group(1)] = bracket_match.group(2).strip()
            continue
        numbered_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered_match:
            references[f"[{numbered_match.group(1)}]"] = numbered_match.group(2).strip()
    return references


class ProposalRecord(BaseModel):
    proposal_level: str = "proposal"
    accepted: bool = False
    curator_confirmed: bool = False


class SourceAnchor(BaseModel):
    source_id: str
    citation_markers: list[str] = Field(default_factory=list)
    reference_text: str | None = None


class PackageMetadata(ProposalRecord):
    exported_at: str
    exporter: str
    swarm_name: str
    swarm_description: str | None = None
    swarm_output_dir: str | None = None


class SourcePackageMetadata(ProposalRecord):
    config_path: str
    config_name: str
    draft_path: str
    traceability_matrix_path: str
    review_notes_path: str | None = None
    references: dict[str, str] = Field(default_factory=dict)


class StudyContext(ProposalRecord):
    domain: str | None = None
    species: str | None = None
    standards: list[str] = Field(default_factory=list)
    output_sections: list[str] = Field(default_factory=list)
    inferred_from: list[str] = Field(default_factory=list)


class Assertion(ProposalRecord):
    assertion_id: str
    statement: str
    assertion_type: str
    persona: str | None = None
    epistemic_tags: list[str] = Field(default_factory=list)
    source_anchors: list[SourceAnchor] = Field(default_factory=list)
    in_text_citations: list[str] = Field(default_factory=list)
    notes: str | None = None


class MNMSMappingCandidate(ProposalRecord):
    mapping_id: str
    metadata_field: str
    value_or_status: str | None = None
    mnms_category: str | None = None
    classification: str | None = None
    source_anchors: list[SourceAnchor] = Field(default_factory=list)
    in_text_citations: list[str] = Field(default_factory=list)
    notes: str | None = None


class GraphAssertionCandidate(ProposalRecord):
    assertion_id: str
    subject: str
    predicate: str
    object: str
    evidence_level: str | None = None
    confidence: str | None = None
    source_anchors: list[SourceAnchor] = Field(default_factory=list)
    in_text_citations: list[str] = Field(default_factory=list)
    notes: str | None = None


class ReviewNote(ProposalRecord):
    note_id: str
    persona: str
    note: str
    note_type: str = "persona_review"
    source_anchors: list[SourceAnchor] = Field(default_factory=list)
    in_text_citations: list[str] = Field(default_factory=list)


class MAPPPPBundle(ProposalRecord):
    schema_name: str = "mapppp-bundle"
    schema_version: str = "0.1.0"
    package_metadata: PackageMetadata
    source_package_metadata: SourcePackageMetadata
    study_context: StudyContext | None = None
    metadata_assertions: list[Assertion] = Field(default_factory=list)
    evidence_assertions: list[Assertion] = Field(default_factory=list)
    candidate_mnms_mappings: list[MNMSMappingCandidate] = Field(default_factory=list)
    candidate_graph_assertions: list[GraphAssertionCandidate] = Field(default_factory=list)
    review_notes: list[ReviewNote] = Field(default_factory=list)


def _build_source_anchors(
    source_id: str | None,
    citations: list[str],
    references: dict[str, str],
) -> list[SourceAnchor]:
    anchors: list[SourceAnchor] = []
    if source_id:
        anchors.append(
            SourceAnchor(
                source_id=source_id.strip(),
                citation_markers=citations,
                reference_text=" ".join(
                    reference for citation, reference in references.items() if citation in citations
                ) or None,
            )
        )
        return anchors

    for citation in citations:
        anchors.append(
            SourceAnchor(
                source_id=citation,
                citation_markers=[citation],
                reference_text=references.get(citation),
            )
        )
    return anchors


def _infer_study_context(config: dict[str, Any], draft_text: str) -> StudyContext:
    swarm = config.get("swarm", {})
    text_blob = " ".join(
        [
            swarm.get("name", ""),
            swarm.get("description", ""),
            draft_text or "",
            json.dumps(config.get("personas", [])),
        ]
    ).lower()

    domain = None
    if "home cage monitoring" in text_blob:
        domain = "preclinical home cage monitoring"

    species = None
    if re.search(r"\b(mice|mouse|murine|c57bl/6)\b", text_blob):
        species = "mouse"
    elif re.search(r"\b(rats|rat)\b", text_blob):
        species = "rat"
    elif re.search(r"\brodent(s)?\b", text_blob):
        species = "rodent"

    standards = []
    if "mnms" in text_blob:
        standards.append("MNMS")

    return StudyContext(
        domain=domain,
        species=species,
        standards=standards,
        output_sections=list(config.get("output_sections", [])),
        inferred_from=["swarm config", "journalist draft"],
    )


def _load_traceability_rows(traceability_matrix_path: Path) -> list[dict[str, str]]:
    text = traceability_matrix_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    expected_headers = _TRACEABILITY_HEADERS
    for index, line in enumerate(lines):
        normalised_headers = [
            _normalise_header(cell)
            for cell in line.strip().strip("|").split("|")
        ]
        if not set(expected_headers).issubset(normalised_headers):
            continue
        headers = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows: list[dict[str, str]] = []
        for raw_line in lines[index + 2:]:
            stripped = raw_line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) != len(headers):
                continue
            if all(set(cell) <= {"-"} for cell in cells):
                continue
            rows.append(
                {
                    _normalise_header(header): cells[cell_index]
                    for cell_index, header in enumerate(headers)
                }
            )
        if rows:
            return rows

    # Fallback for traceability files that still keep rows inside a contiguous
    # Markdown table block instead of appending them after the template footer.
    tables = _extract_markdown_tables(text)
    for table in tables:
        headers = set(table[0].keys()) if table else set()
        if {"claim_id", "claim", "epistemic_tag", "source", "agent"}.issubset(headers):
            return table
    return []


def _load_review_note_payload(review_notes_path: Path | None) -> list[dict[str, Any]]:
    if review_notes_path is None:
        return []
    if not review_notes_path.exists():
        raise FileNotFoundError(f"Review notes file not found: {review_notes_path}")
    with open(review_notes_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, list) else []


def export_hcm_mapppp_bundle(
    config_path: str | Path,
    draft_path: str | Path,
    traceability_matrix_path: str | Path,
    review_notes_path: str | Path | None = None,
    exported_at: datetime | None = None,
) -> MAPPPPBundle:
    """Build a proposal-only MAPPPP bundle from existing HCM swarm artifacts.

    If provided, exported_at should be a timezone-aware datetime.
    """
    config_path = Path(config_path)
    draft_path = Path(draft_path)
    traceability_matrix_path = Path(traceability_matrix_path)
    review_notes_path = Path(review_notes_path) if review_notes_path else None

    with open(config_path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    draft_text = draft_path.read_text(encoding="utf-8")
    sections = _split_sections(draft_text)
    references = _parse_references(sections.get("I", ""))
    traceability_rows = _load_traceability_rows(traceability_matrix_path)

    metadata_assertions: list[Assertion] = []
    evidence_assertions: list[Assertion] = []
    candidate_mnms_mappings: list[MNMSMappingCandidate] = []
    candidate_graph_assertions: list[GraphAssertionCandidate] = []
    review_notes: list[ReviewNote] = []

    for index, row in enumerate(traceability_rows, start=1):
        if row.get("status", "").lower() == "superseded":
            continue
        statement = row.get("claim", "").strip()
        if not statement or statement.lower().startswith("matrix initialized"):
            continue
        citations = _extract_citations(statement + " " + row.get("notes", ""))
        anchors = _build_source_anchors(row.get("source"), citations, references)
        evidence_assertions.append(
            Assertion(
                assertion_id=f"traceability-evidence-{index}",
                statement=statement,
                assertion_type="traceability_claim",
                persona=row.get("agent") or None,
                epistemic_tags=_unique([row.get("epistemic_tag", "").strip()]),
                source_anchors=anchors,
                in_text_citations=citations,
                notes=row.get("notes") or None,
            )
        )
        if row.get("mnms_category"):
            metadata_assertions.append(
                Assertion(
                    assertion_id=f"traceability-metadata-{index}",
                    statement=statement,
                    assertion_type="metadata_candidate",
                    persona=row.get("agent") or None,
                    epistemic_tags=_unique([row.get("epistemic_tag", "").strip()]),
                    source_anchors=anchors,
                    in_text_citations=citations,
                    notes=row.get("mnms_category"),
                )
            )

    for index, table in enumerate(_extract_markdown_tables(sections.get("C", "")), start=1):
        for row_index, row in enumerate(table, start=1):
            statement = row.get("claim") or row.get("assertion") or row.get("evidence") or ""
            if not statement:
                continue
            notes = row.get("notes") or row.get("method") or None
            citations = _extract_citations(" ".join([statement, notes or ""]))
            source_id = row.get("source_anchor") or row.get("source") or row.get("doi")
            evidence_assertions.append(
                Assertion(
                    assertion_id=f"evidence-table-{index}-{row_index}",
                    statement=statement,
                    assertion_type=row.get("evidence_type") or "evidence_table_row",
                    epistemic_tags=_extract_epistemic_tags(statement + " " + (notes or "")),
                    source_anchors=_build_source_anchors(source_id, citations, references),
                    in_text_citations=citations,
                    notes=notes,
                )
            )

    for index, table in enumerate(_extract_markdown_tables(sections.get("D", "")), start=1):
        for row_index, row in enumerate(table, start=1):
            notes = row.get("notes") or None
            citations = _extract_citations(" ".join(filter(None, [notes or "", row.get("source", "")])))
            candidate_mnms_mappings.append(
                MNMSMappingCandidate(
                    mapping_id=f"mnms-mapping-{index}-{row_index}",
                    metadata_field=row.get("metadata_field", ""),
                    value_or_status=row.get("value_or_status"),
                    mnms_category=row.get("mnms_category"),
                    classification=row.get("classification"),
                    source_anchors=_build_source_anchors(row.get("source"), citations, references),
                    in_text_citations=citations,
                    notes=notes,
                )
            )

    for index, bullet in enumerate(_extract_bullets(sections.get("E", "")), start=1):
        citations = _extract_citations(bullet)
        metadata_assertions.append(
            Assertion(
                assertion_id=f"metadata-gap-{index}",
                statement=bullet,
                assertion_type="metadata_gap",
                persona=HCM_METADATA_PERSONA,
                epistemic_tags=_extract_epistemic_tags(bullet),
                source_anchors=_build_source_anchors(None, citations, references),
                in_text_citations=citations,
            )
        )

    for index, table in enumerate(_extract_markdown_tables(sections.get("F", "")), start=1):
        for row_index, row in enumerate(table, start=1):
            if not {"subject", "predicate", "object"}.issubset(row.keys()):
                continue
            notes = row.get("notes") or None
            citations = _extract_citations(" ".join(filter(None, [notes or "", row.get("source_id", "")])))
            candidate_graph_assertions.append(
                GraphAssertionCandidate(
                    assertion_id=f"graph-assertion-{index}-{row_index}",
                    subject=row["subject"],
                    predicate=row["predicate"],
                    object=row["object"],
                    evidence_level=row.get("evidence_level"),
                    confidence=row.get("confidence"),
                    source_anchors=_build_source_anchors(row.get("source_id"), citations, references),
                    in_text_citations=citations,
                    notes=notes,
                )
            )

    for index, table in enumerate(_extract_markdown_tables(sections.get("G", "")), start=1):
        for row_index, row in enumerate(table, start=1):
            note = row.get("description") or row.get("note") or ""
            if not note:
                continue
            citations = _extract_citations(note)
            review_notes.append(
                ReviewNote(
                    note_id=f"risk-note-{index}-{row_index}",
                    persona=HCM_RISK_PERSONA,
                    note=note,
                    note_type="risk_audit",
                    source_anchors=_build_source_anchors(
                        source_id=None,
                        citations=citations,
                        references=references,
                    ),
                    in_text_citations=citations,
                )
            )

    for index, payload in enumerate(_load_review_note_payload(review_notes_path), start=1):
        note = str(payload.get("note", "")).strip()
        if not note:
            continue
        citations = _unique(
            [str(citation) for citation in payload.get("citations", []) if citation]
            + _extract_citations(note)
        )
        review_notes.append(
            ReviewNote(
                note_id=f"external-review-note-{index}",
                persona=str(payload.get("persona", "Reviewer-2")),
                note=note,
                note_type=str(payload.get("note_type", "persona_review")),
                source_anchors=_build_source_anchors(payload.get("source_anchor"), citations, references),
                in_text_citations=citations,
            )
        )

    swarm = config.get("swarm", {})
    return MAPPPPBundle(
        package_metadata=PackageMetadata(
            exported_at=(exported_at or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
            exporter="automation.exporters.mapppp.export_hcm_mapppp_bundle",
            swarm_name=swarm.get("name", "Unknown swarm"),
            swarm_description=swarm.get("description"),
            swarm_output_dir=swarm.get("output_dir"),
        ),
        source_package_metadata=SourcePackageMetadata(
            config_path=str(config_path.resolve()),
            config_name=config_path.name,
            draft_path=str(draft_path.resolve()),
            traceability_matrix_path=str(traceability_matrix_path.resolve()),
            review_notes_path=str(review_notes_path.resolve()) if review_notes_path else None,
            references=references,
        ),
        study_context=_infer_study_context(config, draft_text),
        metadata_assertions=metadata_assertions,
        evidence_assertions=evidence_assertions,
        candidate_mnms_mappings=candidate_mnms_mappings,
        candidate_graph_assertions=candidate_graph_assertions,
        review_notes=review_notes,
    )
