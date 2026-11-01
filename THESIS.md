# NEAR long-term thesis — evidence first

*Snapshot: data fetched 2026-10-30 22:32 UTC (NearBlocks day 2026-10-29). Every number below is in `data/metrics.json` and re-computed by `./run.sh`; the live scorecard is on the dashboard. If this file and the dashboard disagree, the dashboard is newer.*

## The thesis in one line
NEAR's value case has moved from "a busy L1" to "the settlement layer for cross-chain intents". The data supports the second part and clearly cuts against the first. Today it is a **bet on NEAR Intents** with weak L1 fundamentals and a rich valuation. **Current score: 4 / 10 claims bullish.**

## Scoring model (re-runnable)
Each claim has a metric, a source, a fixed threshold and a falsifier. `pipeline/build.py` marks it BULL (1) or BEAR (0); the score is the sum. Thresholds were set before looking at the result for this snapshot and are not tuned afterwards; changes go through git history.
- 0–3: thesis rejected · 4–6: speculative (Intents-only bet) · 7–10: thesis supported.

## Claims

| ID | Claim | Metric (source) | Value | Threshold | Verdict | What proves it wrong |
|---|---|---|---|---|---|---|
| C1 | Intents settles volume far larger than NEAR's own DeFi | Intents 1y volume / NEAR TVL (DefiLlama) | **$32.8B / $197M = 167x** | > 50x | BULL | 1y volume < 50x TVL |
| C1b | Intents momentum is positive | Intents 30d vs prior 30d (DefiLlama) | $3.89B vs $4.75B = **−18.1%** | > 0% | BEAR | — (already failing) |
| C2 | Daily active accounts growing YoY | 90d avg active accounts vs 1y ago (NearBlocks) | 72.7k vs 302.2k = **−76%** | > +10% | BEAR | — |
| C3 | Transactions growing YoY | 90d avg txns/day vs 1y ago (NearBlocks) | 0.74M vs 4.76M = **−84%** | > +10% | BEAR | — |
| C4 | Fees offset issuance (deflation) | 1y fees as % of net supply growth (NearBlocks) | 0.62M NEAR vs 31.7M NEAR = **2.0%** | ≥ 100% | BEAR | fees ≥ 100% of new supply |
| C5 | Stablecoin liquidity growing | Stablecoin supply vs 1y ago (DefiLlama) | $129M vs $226M = **−43%** | > +20% | BEAR | — |
| C6 | TVL growing | NEAR TVL vs 1y ago (DefiLlama) | $197M vs $162M = **+21.7%** | > 0% | BULL | TVL below 1y-ago level |
| C7 | Cheap vs peers on fees | P/F rank of 5 L1s (CoinGecko + DefiLlama) | NEAR **4,651x** vs SOL 239x, APT 479x, SUI 1,281x, AVAX 1,352x → rank 5/5 | rank ≤ 2 | BEAR | rank ≤ 2 |
| C8 | Core development stays active | nearcore commits 12w vs prior 12w (GitHub) | 386 vs 370 = **+4.3%** | > −25% | BULL | drop > 25% |
| C9 | Derivatives not crowded long | Hyperliquid NEAR funding 30d avg, annualized | **11.1%** (default ≈ 11%), OI ≈ $250M | < 15% | BULL | 30d funding > 15% |

Other context (not scored): net supply inflation **2.48%/yr** (1.278B → 1.310B NEAR); **45.3%** of supply staked across 379 validators (NEAR RPC `validators`); MC/TVL 28.8x (SOL 10.4x, SUI 8.0x, APT 13.7x, AVAX 7.2x).

## Bull case (honest)
1. **Intents is real money.** $32.8B settled in 12 months ($35.7B all time) is ~167x NEAR's own TVL and ~6x its market cap. No peer L1 here has a comparable cross-chain settlement product native to the chain.
2. **Builders did not leave.** nearcore commit rate is flat to up while usage fell — the protocol team keeps shipping.
3. **Positioning is clean.** Funding sits at the default rate; no crowded long that would unwind.
4. **TVL is up 22% YoY** even as activity collapsed — remaining capital is stickier.

## Bear case (honest)
1. **L1 activity collapsed.** Active accounts −76% and txns −84% YoY. Much of the 2025 count was bot/airdrop traffic; organic usage is what is left.
2. **Fees don't pay for security.** 1y burned fees cover ~2% of new issuance; holders are diluted ~2.5%/yr.
3. **Valuation is the most expensive of the five** on P/F (~19x Solana) and MC/TVL.
4. **Intents value capture is unproven.** Intents volume doesn't flow to NEAR fees (C4); and momentum just turned negative (C1b, C5).

## What would change my mind
- **Upgrade to "supported" (≥7):** Intents 30d momentum back above 0, stablecoins back above $226M, and active accounts above the 1y-ago 90d average — or a mechanism that routes Intents fees to NEAR holders, visible as C4 rising above 10%.
- **Reject (≤3):** Intents 1y volume below 50x TVL, or nearcore commits −25%.

## Limitations
- NearBlocks counts are not sybil-filtered. The NEAR BigQuery dataset (`bigquery-public-data.crypto_near_mainnet_us`) could give a stricter count; it is billed per query, so we left it as an optional extension (`sql/` queries in a later commit).
- DefiLlama "chain fees" and Intents volume follow DefiLlama methodology; NEAR Intents Explorer API needs a partner JWT and isn't used.
- CoinGecko free API is rate-limited; GitHub `stats` can return 202 at first call (the fetcher retries).
