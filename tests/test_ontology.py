"""The ontology parses, the example conforms, and the shapes catch bad data."""

import pytest
from rdflib import Graph

from kso.graph import (
    EXAMPLES_DIR,
    ONTOLOGY_DIR,
    SHAPES_DIR,
    VOCABULARY_DIR,
    load,
    load_examples,
    load_schema,
    load_shapes,
    turtle_files,
)
from kso.validation import validate

ALL_TURTLE = turtle_files(ONTOLOGY_DIR, VOCABULARY_DIR, SHAPES_DIR, EXAMPLES_DIR)

PREFIXES = """
@prefix kso:  <https://w3id.org/kso/ontology#> .
@prefix ksov: <https://w3id.org/kso/vocab#> .
@prefix ksoj: <https://w3id.org/kso/jurisdiction/> .
@prefix ex:   <https://w3id.org/kso/example/> .
"""


@pytest.fixture(scope="module")
def schema() -> Graph:
    return load_schema()


@pytest.fixture(scope="module")
def shapes() -> Graph:
    return load_shapes()


def check(turtle: str, schema: Graph, shapes: Graph):
    """Parse a small inline dataset and validate it."""
    data = Graph().parse(data=PREFIXES + turtle, format="turtle")
    return validate(data, schema=schema, shapes=shapes)


@pytest.mark.parametrize("path", ALL_TURTLE, ids=lambda p: p.name)
def test_every_turtle_file_parses(path):
    assert len(load(path)) > 0


def test_bundled_example_conforms(schema, shapes):
    result = validate(load_examples(), schema=schema, shapes=shapes)
    assert result.conforms, result.report


def test_checker_cannot_be_maker(schema, shapes):
    result = check("""
        ex:P a kso:NaturalPerson ; kso:legalName "Same Person" .
        ex:C a kso:Case ; kso:isLocked true .
        ex:E a kso:Escalation ;
             kso:escalatedCase ex:C ;
             kso:escalationTrigger ksov:SuspectedTrueMatch ;
             kso:maker ex:P ; kso:checker ex:P .
    """, schema, shapes)
    assert not result.conforms
    assert "Four-eyes" in result.report


def test_escalated_case_must_be_locked(schema, shapes):
    result = check("""
        ex:A a kso:NaturalPerson ; kso:legalName "Maker" .
        ex:B a kso:NaturalPerson ; kso:legalName "Checker" .
        ex:C a kso:Case .
        ex:E a kso:Escalation ;
             kso:escalatedCase ex:C ;
             kso:escalationTrigger ksov:UnmitigatedHighRisk ;
             kso:maker ex:A ; kso:checker ex:B .
    """, schema, shapes)
    assert not result.conforms
    assert "must lock its case" in result.report


def test_stakes_cannot_exceed_one_hundred_percent(schema, shapes):
    result = check("""
        ex:Co a kso:LegalEntity ; kso:legalName "Overowned Ltd" ; kso:incorporatedIn ksoj:GB .
        ex:X a kso:NaturalPerson ; kso:legalName "X" .
        ex:Y a kso:NaturalPerson ; kso:legalName "Y" .
        ex:S1 a kso:OwnershipStake ; kso:holder ex:X ; kso:heldIn ex:Co ; kso:percentage 70.0 .
        ex:S2 a kso:OwnershipStake ; kso:holder ex:Y ; kso:heldIn ex:Co ; kso:percentage 40.0 .
    """, schema, shapes)
    assert not result.conforms
    assert "exceeds 100%" in result.report
    assert "110.0%" in result.report


def test_foreign_extension_needs_a_master(schema, shapes):
    result = check("""
        ex:Co a kso:LegalEntity ; kso:legalName "Orphan Ltd" ; kso:incorporatedIn ksoj:GB .
        ex:Ext a kso:ForeignExtension ; kso:profileOf ex:Co ; kso:bookedIn ksoj:SG .
    """, schema, shapes)
    assert not result.conforms
    assert "Master Anchor Mandate" in result.report
