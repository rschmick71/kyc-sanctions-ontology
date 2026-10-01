# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [0.1.1] — 2026-09-30

### Fixed
- SHACL stake-total message now shows the actual sum (`?total` was never bound).
- Stake-total test asserts the reported percentage, not just the failure.
- README CI badge markup.
- Operating-model doc: LaTeX symbols, direct regulator links for Vietnam and India.

### Changed
- FATF statuses dated to the 19 June 2026 plenary; thresholds labelled as illustrative firm policy.

## [0.1.0] — 2026-09-29

### Added
- Seven ontology modules: core, ownership, risk, screening, governance,
  correspondent, trade-finance.
- SKOS reference codes and a 20-jurisdiction vocabulary generated from the
  operating-model matrix.
- SHACL shapes for data quality and 1LOD policy (four-eyes, system lock,
  US Master Anchor Mandate, stake totals).
- Fictional worked example: Harbourline Commodities Ltd.
- Five SPARQL competency questions.
- `kso` Python package and CLI: `validate`, `query`, `ubo`.
- pytest suite and GitHub Actions CI.
- ADRs 0001–0004.
