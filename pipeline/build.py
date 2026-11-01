"""Compute metrics + score falsifiable claims from data/raw, write data/metrics.json and docs/index.html."""
import warnings; warnings.filterwarnings("ignore")
import json, os, statistics as st, datetime as dt
B = os.path.join(os.path.dirname(__file__), ".."); R = os.path.join(B, "data", "raw")
L = lambda n: json.load(open(os.path.join(R, n + ".json")))
Y = 1e24
nb = L("nearblocks_charts")["charts"]; nb = [c for c in nb if c["txns"]]
def ser(key, f=float): return [(c["date"][:10], f(c[key])) for c in nb]
def avg(s, a, b): v = [x for _, x in s[a:b]]; return sum(v) / len(v)
aa, tx = ser("active_accounts"), ser("txns")
sup = ser("total_supply", lambda x: float(x) / Y)
feeN = ser("txn_fee", lambda x: float(x) / Y)
m = {"fetched_utc": L("_meta")["fetched_utc"], "last_day": nb[-1]["date"][:10]}
m["aa_90d"], m["aa_prev90d"], m["aa_365d_ago_90d"] = avg(aa, -90, None), avg(aa, -180, -90), avg(aa, -455, -365)
m["tx_90d"], m["tx_prev90d"], m["tx_365d_ago_90d"] = avg(tx, -90, None), avg(tx, -180, -90), avg(tx, -455, -365)
m["supply_now"], m["supply_1y_ago"] = sup[-1][1], sup[-366][1]
m["net_inflation_1y_pct"] = (m["supply_now"] / m["supply_1y_ago"] - 1) * 100
m["fees_near_1y"] = sum(x for _, x in feeN[-365:])
m["fees_vs_supply_change_pct"] = m["fees_near_1y"] / (m["supply_now"] - m["supply_1y_ago"]) * 100
v = L("near_rpc_validators")["result"]["current_validators"]
m["staked_near"] = sum(int(x["stake"]) for x in v) / Y; m["validators"] = len(v)
m["staked_pct"] = m["staked_near"] / m["supply_now"] * 100
tvl = L("llama_tvl_near"); m["tvl_now"], m["tvl_1y_ago"] = tvl[-1]["tvl"], tvl[-366]["tvl"]
stb = L("llama_stables_near"); sv = lambda r: r["totalCirculatingUSD"].get("peggedUSD", 0)
m["stables_now"], m["stables_1y_ago"] = sv(stb[-1]), sv(stb[-366])
it = L("llama_intents")["totalDataChart"]
m["intents_30d"], m["intents_prev30d"] = sum(x for _, x in it[-30:]), sum(x for _, x in it[-60:-30])
m["intents_1y"], m["intents_alltime"] = sum(x for _, x in it[-365:]), sum(x for _, x in it)
gh = L("github_nearcore"); m["nearcore_commits_12w"] = sum(w["total"] for w in gh[-12:]); m["nearcore_commits_prev12w"] = sum(w["total"] for w in gh[-24:-12])
hl = L("hyperliquid_ctx"); i = [a["name"] for a in hl[0]["universe"]].index("NEAR"); c = hl[1][i]
m["hl_oi_usd"] = float(c["openInterest"]) * float(c["markPx"]); m["hl_funding_ann_pct"] = float(c["funding"]) * 24 * 365 * 100
fh = L("hyperliquid_funding_near"); m["hl_funding_30d_ann_pct"] = st.mean(float(x["fundingRate"]) for x in fh) * 24 * 365 * 100
cg = {x["id"]: x for x in L("coingecko_markets")}; ch = {x["name"]: x["tvl"] for x in L("llama_chains")}
peers = {"near": ("near", "Near"), "solana": ("solana", "Solana"), "sui": ("sui", "Sui"), "aptos": ("aptos", "Aptos"), "avalanche": ("avalanche-2", "Avalanche")}
m["peers"] = {}
for k, (g, n) in peers.items():
    f = L("llama_fees_" + k); mc = cg[g]["market_cap"]
    m["peers"][k] = {"mcap": mc, "fdv": cg[g]["fully_diluted_valuation"], "price": cg[g]["current_price"], "fees_1y": f["total1y"], "tvl": ch[n],
                     "p_f": mc / f["total1y"], "mc_tvl": mc / ch[n]}
m["near_pf_rank"] = sorted(m["peers"], key=lambda k: m["peers"][k]["p_f"]).index("near") + 1
g = lambda a, b: (a / b - 1) * 100
# Claims: (id, side, statement, metric, value, threshold, pass?, falsifier)
C = [
 ("C1", "bull", "NEAR Intents settles volume far larger than NEAR's own DeFi", "Intents 1y volume / NEAR chain TVL (x)", m["intents_1y"] / m["tvl_now"], "> 50x", m["intents_1y"] > 50 * m["tvl_now"], "1y Intents volume below 50x chain TVL"),
 ("C1b", "bull", "Intents volume momentum is positive", "Intents volume, last 30d vs prior 30d (%)", g(m["intents_30d"], m["intents_prev30d"]), "> 0%", m["intents_30d"] > m["intents_prev30d"], "30d volume below prior 30d"),
 ("C2", "bull", "Usage is growing: daily active accounts up year over year", "Active accounts, 90d avg vs same window 1y ago (%)", g(m["aa_90d"], m["aa_365d_ago_90d"]), "> +10%", g(m["aa_90d"], m["aa_365d_ago_90d"]) > 10, "90d avg active accounts below the 1y-ago level"),
 ("C3", "bull", "Transactions are growing year over year", "Txns/day, 90d avg vs 1y ago (%)", g(m["tx_90d"], m["tx_365d_ago_90d"]), "> +10%", g(m["tx_90d"], m["tx_365d_ago_90d"]) > 10, "90d avg txns below 1y-ago level"),
 ("C4", "bear", "Fees do not offset issuance: NEAR is not deflationary", "Fees paid in 1y as % of net supply growth", m["fees_vs_supply_change_pct"], "bull only if >= 100%", m["fees_vs_supply_change_pct"] >= 100, "fees reach >=100% of net new supply"),
 ("C5", "bull", "Stablecoin liquidity on NEAR is growing", "Stablecoin supply vs 1y ago (%)", g(m["stables_now"], m["stables_1y_ago"]), "> +20%", g(m["stables_now"], m["stables_1y_ago"]) > 20, "stablecoin supply below 1y-ago level"),
 ("C6", "bear", "Onchain TVL is not growing", "DefiLlama NEAR TVL vs 1y ago (%)", g(m["tvl_now"], m["tvl_1y_ago"]), "bull only if > 0%", m["tvl_now"] > m["tvl_1y_ago"], "TVL above 1y-ago level"),
 ("C7", "bear", "Valuation is rich vs peers on fees", "P/F (mcap / 1y chain fees), rank among 5 L1s (1 = cheapest)", m["near_pf_rank"], "bull only if rank <= 2", m["near_pf_rank"] <= 2, "NEAR ranks in the 2 cheapest by P/F"),
 ("C8", "bull", "Core development stays active", "nearcore commits last 12w vs prior 12w (%)", g(m["nearcore_commits_12w"], m["nearcore_commits_prev12w"]), "> -25%", g(m["nearcore_commits_12w"], m["nearcore_commits_prev12w"]) > -25, "commits drop >25% vs prior 12w"),
 ("C9", "bull", "Derivatives positioning is not crowded long", "Hyperliquid NEAR funding, 30d avg annualized (%)", m["hl_funding_30d_ann_pct"], "< 15% (default ~11%)", m["hl_funding_30d_ann_pct"] < 15, "30d funding > 15% annualized (crowded longs)"),
]
m["claims"] = [dict(zip(["id", "side", "claim", "metric", "value", "threshold", "bullish", "falsifier"], x)) for x in C]
m["score"] = sum(x["bullish"] for x in m["claims"]); m["score_max"] = len(C)
json.dump(m, open(os.path.join(B, "data", "metrics.json"), "w"), indent=1, default=float)
# Dashboard
def s7(s): return [round(st.mean(x for _, x in s[max(0, k - 6):k + 1]), 1) for k in range(len(s))]
cut = -730
charts = {
 "aa": ([d for d, _ in aa[cut:]], s7(aa)[cut:], "Daily active accounts (7d avg) - NearBlocks", "Unique accounts signing txns per day."),
 "tx": ([d for d, _ in tx[cut:]], s7(tx)[cut:], "Daily transactions (7d avg) - NearBlocks", "Txns per day on NEAR mainnet."),
 "supply": ([d for d, _ in sup[cut:]], [round(x / 1e6, 2) for _, x in sup[cut:]], "Total supply, M NEAR - NearBlocks", "Issuance minus burned fees."),
 "tvl": ([dt.datetime.utcfromtimestamp(r["date"]).strftime("%Y-%m-%d") for r in tvl[cut:]], [round(r["tvl"] / 1e6, 1) for r in tvl[cut:]], "TVL, $M - DefiLlama", "Value locked in NEAR DeFi."),
 "stables": ([dt.datetime.utcfromtimestamp(int(r["date"])).strftime("%Y-%m-%d") for r in stb[cut:]], [round(sv(r) / 1e6, 1) for r in stb[cut:]], "Stablecoin supply, $M - DefiLlama", "USD stablecoins issued/bridged on NEAR."),
 "intents": ([dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d") for t, _ in it], s7([(0, x / 1e6) for _, x in it]), "NEAR Intents daily volume (7d avg), $M - DefiLlama", "Cross-chain swaps settled via NEAR Intents."),
}
rows = "".join(f"<tr class='{'ok' if c['bullish'] else 'no'}'><td>{c['id']}</td><td>{c['claim']}</td><td>{c['metric']}</td><td>{c['value']:,.1f}</td><td>{c['threshold']}</td><td>{'BULL' if c['bullish'] else 'BEAR'}</td><td>{c['falsifier']}</td></tr>" for c in m["claims"])
prow = "".join(f"<tr><td>{k.upper()}</td><td>${p['mcap']/1e9:,.2f}B</td><td>${p['fees_1y']/1e6:,.1f}M</td><td>{p['p_f']:,.0f}x</td><td>${p['tvl']/1e6:,.0f}M</td><td>{p['mc_tvl']:,.1f}x</td></tr>" for k, p in m["peers"].items())
html = open(os.path.join(B, "pipeline", "template.html")).read()
html = html.replace("{{CHARTS}}", json.dumps(charts)).replace("{{ROWS}}", rows).replace("{{PEERS}}", prow).replace("{{SCORE}}", f"{m['score']}/{m['score_max']}").replace("{{TS}}", m["fetched_utc"])
open(os.path.join(B, "docs", "index.html"), "w").write(html)
print(json.dumps({k: v for k, v in m.items() if k not in ("peers", "claims")}, indent=1, default=float))
for c in m["claims"]: print(c["id"], c["side"], round(c["value"], 2), c["bullish"])
for k, p in m["peers"].items(): print(k, round(p["p_f"]), round(p["mc_tvl"], 1))
