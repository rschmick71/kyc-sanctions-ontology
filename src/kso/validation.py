"""SHACL validation of instance data against the KSO shapes."""

from dataclasses import dataclass

from pyshacl import validate as shacl_validate
from rdflib import Graph

from kso.graph import load_schema, load_shapes


@dataclass(frozen=True)
class ValidationResult:
    conforms: bool
    report: str


def validate(data: Graph, schema: Graph | None = None, shapes: Graph | None = None) -> ValidationResult:
    """Check `data` against the shapes.

    The schema (ontology + vocabularies) is merged into the data graph because
    instance data points at reference data it doesn't contain — ex:Harbourline
    says it is incorporated in ksoj:KE, but KE's FATF status lives in
    vocabularies/. Validation has to see both to judge the whole picture.

    RDFS inference matters too: a kso:ForeignExtension is only a
    kso:CustomerProfile because of rdfs:subClassOf, so shapes targeting
    CustomerProfile would miss it without inference.
    """
    schema = schema if schema is not None else load_schema()
    conforms, _report_graph, report_text = shacl_validate(
        data + schema,
        shacl_graph=shapes if shapes is not None else load_shapes(),
        inference="rdfs",
        abort_on_first=False,
        allow_warnings=True,
    )
    return ValidationResult(conforms=bool(conforms), report=str(report_text))
