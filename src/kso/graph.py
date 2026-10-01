"""Find the repository's Turtle files and load them into rdflib graphs.

Three kinds of graph, kept separate on purpose:

    schema  — ontology/ + vocabularies/   (what things mean)
    shapes  — shapes/                     (what valid data must look like)
    data    — examples/ or your own files (the facts being checked)
"""

from pathlib import Path

from rdflib import Graph, Namespace

REPO_ROOT = Path(__file__).resolve().parents[2]

ONTOLOGY_DIR = REPO_ROOT / "ontology"
VOCABULARY_DIR = REPO_ROOT / "vocabularies"
SHAPES_DIR = REPO_ROOT / "shapes"
EXAMPLES_DIR = REPO_ROOT / "examples"
QUERIES_DIR = REPO_ROOT / "queries"

KSO = Namespace("https://w3id.org/kso/ontology#")
KSOV = Namespace("https://w3id.org/kso/vocab#")
KSOJ = Namespace("https://w3id.org/kso/jurisdiction/")
EX = Namespace("https://w3id.org/kso/example/")


def turtle_files(*directories: Path) -> list[Path]:
    """Every .ttl file under the given directories, in a stable order."""
    return sorted(path for directory in directories for path in directory.rglob("*.ttl"))


def load(*paths: Path) -> Graph:
    """Parse Turtle files into one graph, with the project prefixes bound."""
    graph = Graph()
    for prefix, namespace in {"kso": KSO, "ksov": KSOV, "ksoj": KSOJ, "ex": EX}.items():
        graph.bind(prefix, namespace)
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def load_schema() -> Graph:
    return load(*turtle_files(ONTOLOGY_DIR, VOCABULARY_DIR))


def load_shapes() -> Graph:
    return load(*turtle_files(SHAPES_DIR))


def load_examples() -> Graph:
    return load(*turtle_files(EXAMPLES_DIR))


def load_knowledge_graph(*data_paths: Path) -> Graph:
    """Schema + data in one graph — what you query against.

    With no paths given, the bundled examples are used.
    """
    paths = data_paths or tuple(turtle_files(EXAMPLES_DIR))
    return load(*turtle_files(ONTOLOGY_DIR, VOCABULARY_DIR), *paths)
