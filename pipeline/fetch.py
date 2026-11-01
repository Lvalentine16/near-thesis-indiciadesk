"""Fetch raw public NEAR data into data/raw/. No API keys needed."""
import json, os, time, urllib.request
RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw"); os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "near-thesis-indiciadesk/1.0"}
def get(url, data=None):
    for i in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                         headers={**UA, **({"Content-Type": "application/json"} if data else {})})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status == 202: time.sleep(5); continue
                return json.load(r)
        except Exception as e:
            print("retry", url, e); time.sleep(3 * (i + 1))
    raise RuntimeError(url)
def save(name, obj):
    json.dump(obj, open(os.path.join(RAW, name + ".json"), "w")); print("saved", name)
SOURCES = {
 "nearblocks_charts": ("https://api.nearblocks.io/v1/charts", None),
 "llama_tvl_near": ("https://api.llama.fi/v2/historicalChainTvl/Near", None),
 "llama_chains": ("https://api.llama.fi/v2/chains", None),
 "llama_stables_near": ("https://stablecoins.llama.fi/stablecoincharts/Near", None),
 "llama_intents": ("https://api.llama.fi/summary/dexs/near-intents", None),
 "coingecko_markets": ("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=near,solana,sui,aptos,avalanche-2", None),
 "hyperliquid_ctx": ("https://api.hyperliquid.xyz/info", {"type": "metaAndAssetCtxs"}),
 "near_rpc_validators": ("https://rpc.mainnet.near.org", {"jsonrpc": "2.0", "id": 1, "method": "validators", "params": [None]}),
 "github_nearcore": ("https://api.github.com/repos/near/nearcore/stats/commit_activity", None),
}
PEERS = ["near", "solana", "sui", "aptos", "avalanche"]
if __name__ == "__main__":
    for k, (u, d) in SOURCES.items(): save(k, get(u, d))
    for p in PEERS: save("llama_fees_" + p, get(f"https://api.llama.fi/summary/fees/{p}?dataType=dailyFees"))
    now = int(time.time() * 1000)
    save("hyperliquid_funding_near", get("https://api.hyperliquid.xyz/info",
         {"type": "fundingHistory", "coin": "NEAR", "startTime": now - 30 * 86400000}))
    json.dump({"fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, open(os.path.join(RAW, "_meta.json"), "w"))
