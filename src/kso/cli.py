"""Command-line entry point.

    kso validate [FILE ...]      SHACL-validate data (defaults to examples/)
    kso query cq03 [FILE ...]    run a competency query by id or path
    kso ubo ENTITY_IRI [FILE ...] look-through UBO report for one entity
"""

import argparse
import sys
from pathlib import Path

from rdflib import Graph, URIRef

from kso.graph import EXAMPLES_DIR, QUERIES_DIR, load, load_knowledge_graph, turtle_files
from kso.ownership import reportable_owners, ubo_threshold
from kso.validation import validate


def resolve_query(name: str) -> Path:
    """Accept 'cq03', 'cq03-local-document-gaps', or a path to a .rq file."""
    candidate = Path(name)
    if candidate.suffix == ".rq" and candidate.exists():
        return candidate
    matches = sorted(QUERIES_DIR.glob(f"{name}*.rq"))
    if not matches:
        raise SystemExit(f"No query matching '{name}' in {QUERIES_DIR}")
    return matches[0]


def cmd_validate(args: argparse.Namespace) -> int:
    data = load(*(args.files or turtle_files(EXAMPLES_DIR)))
    result = validate(data)
    print(result.report)
    return 0 if result.conforms else 1


def cmd_query(args: argparse.Namespace) -> int:
    graph = load_knowledge_graph(*args.files)
    results = graph.query(resolve_query(args.query).read_text())
    header = [str(var) for var in results.vars]
    print(" | ".join(header))
    print("-+-".join("-" * len(column) for column in header))
    for row in results:
        print(" | ".join("" if value is None else str(value) for value in row))
    return 0


def to_iri(graph: Graph, text: str) -> URIRef:
    """Turn 'ex:Harbourline' or a full https:// IRI into a URIRef."""
    if text.startswith(("http://", "https://")):
        return URIRef(text)
    return graph.namespace_manager.expand_curie(text)


def cmd_ubo(args: argparse.Namespace) -> int:
    graph = load_knowledge_graph(*args.files)
    entity = to_iri(graph, args.entity)
    threshold = ubo_threshold(graph, entity)
    print(f"Threshold applied: {threshold}%")
    for owner in reportable_owners(graph, entity):
        print(f"  {owner.effective_percent:>6.2f}%  {owner.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kso", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    validate_cmd = commands.add_parser("validate", help="SHACL-validate data files")
    validate_cmd.add_argument("files", nargs="*", type=Path)
    validate_cmd.set_defaults(handler=cmd_validate)

    query_cmd = commands.add_parser("query", help="run a competency query")
    query_cmd.add_argument("query")
    query_cmd.add_argument("files", nargs="*", type=Path)
    query_cmd.set_defaults(handler=cmd_query)

    ubo_cmd = commands.add_parser("ubo", help="look-through UBO report")
    ubo_cmd.add_argument("entity", help="IRI or CURIE, e.g. ex:Harbourline")
    ubo_cmd.add_argument("files", nargs="*", type=Path)
    ubo_cmd.set_defaults(handler=cmd_ubo)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
