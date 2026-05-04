# Fixtures

## User profiles (`fixtures/users/*.json`)

Five synthetic profiles for edge cases: aggressive trader, concentrated holder, empty portfolio, multi-currency global, dividend retiree.

## Conversations (`fixtures/conversations/*.json`)

Multi-turn transcripts for follow-up resolution and topic switches. Tests load these to verify coreference handling when the classifier receives prior turns.

## Test queries

### `test_queries/intent_classification.json`

Each row includes:

- `id`, `query`
- `expected_agent` — must match classifier routing exactly
- `expected_entities` — subset match after normalization (see below)

### `test_queries/safety_pairs.json`

- `query`, `class` (`harmful` | `educational`), `expect_block` (boolean)

## Entity normalization (subset tests)

- **tickers**: Unicode case-fold; strip common exchange suffixes (`.US`, `.AS`, `.L`, `.PA`, `.DE`, `.TO`); compare base symbol.
- **topics**, **sectors**: case-fold; trim whitespace.
- **amount**, **rate**, **period_years**: classifier output must match expected within **±5%** when expected is non-null.
