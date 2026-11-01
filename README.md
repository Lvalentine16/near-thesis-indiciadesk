# NEAR Thesis Scorecard — built at NEAR HACKATHON

**Track 02 · Investment Thesis.** A long-term investment thesis for NEAR where every claim is a falsifiable test that anyone can re-score from free public data with one command. By [IndiciaDesk](https://indiciadesk.com).

- Live dashboard: https://lvalentine16.github.io/near-thesis-indiciadesk/
- Thesis: [THESIS.md](THESIS.md) · raw scores: [data/metrics.json](data/metrics.json)

## Problem
Most token theses are conviction plus cherry-picked charts. This repo turns a NEAR thesis into 10 numeric claims with thresholds and falsifiers, scored automatically, including the claims that cut against NEAR.

## Try it (judges)
1. `git clone https://github.com/Lvalentine16/near-thesis-indiciadesk && cd near-thesis-indiciadesk`
2. `./run.sh` (Python 3.9+, standard library only, no API keys, ~10 s)
3. See: per-claim BULL/BEAR verdicts and the score printed in the terminal; `data/metrics.json` updated; open `docs/index.html` for the charts, scorecard and peer valuation table.

## How it works
- `pipeline/fetch.py` downloads raw JSON into `data/raw/` (snapshot committed for audit).
- `pipeline/build.py` computes metrics, scores claims C1–C9 (incl. C1b), writes `data/metrics.json` and `docs/index.html` (from `pipeline/template.html`, Chart.js via CDN).
- `.github/workflows/refresh.yml` re-runs the pipeline daily and publishes to GitHub Pages.

## Data sources & licensing
| Source | Used for | Terms |
|---|---|---|
| NearBlocks API `/v1/charts` | active accounts, txns, supply, fees | public free API, attribution |
| NEAR RPC `rpc.mainnet.near.org` `validators` | staked NEAR, validator count | public |
| DefiLlama (api.llama.fi, stablecoins.llama.fi) | TVL, chain fees, stablecoins, NEAR Intents volume | free open API |
| CoinGecko `/coins/markets` | price, market cap (NEAR, SOL, SUI, APT, AVAX) | free Demo API, attribution "Data by CoinGecko" |
| GitHub REST `stats/commit_activity` | nearcore dev activity | GitHub API terms |
| Hyperliquid `info` API | NEAR perp funding, open interest | public |

Code: MIT ([LICENSE](LICENSE)). Data belongs to the providers above.

## Hackathon disclosure
All code here was written for NEAR HACKATHON (window 2026-10-19 → 2026-11-14). No pre-existing code; libraries: Python stdlib, Chart.js (MIT). AI coding assistance was used. Team: 1 (IndiciaDesk). No other project submitted by this team.
