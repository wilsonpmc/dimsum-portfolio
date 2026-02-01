import requests
import json
import time
from datetime import datetime

# =========================================================================
# Configuration (Keep your API Keys here)
# =========================================================================
ALPHAVANTAGE_API_KEY = "98TR939RKXQ1MMKS"
EXCHANGERATE_API_KEY = "390764610849850b23dfe230"

PORTFOLIO = {
    "stocks": {"NVDA": 69, "ACHR": 1322, "AMD": 30},
    "crypto": {"ethereum": 3.89944, "curve-dao-token": 36252, "hedera-hashgraph": 23473},
    "cash": 2540
}

COST_BASIS = {
    "stocks": {"NVDA": 8764, "ACHR": 10451, "AMD": 3882},
    "crypto": {"ethereum": 11580, "curve-dao-token": 26672, "hedera-hashgraph": 2235}
}

CRYPTO_ACRONYMS = {"ethereum": "ETH", "curve-dao-token": "CRV", "hedera-hashgraph": "HBAR"}

# =========================================================================
# Data Fetching Logic
# =========================================================================

def get_stock_price(ticker):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHAVANTAGE_API_KEY}"
    try:
        data = requests.get(url).json()
        return float(data["Global Quote"]["05. price"])
    except: return None

def get_crypto_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try: return requests.get(url).json()[coin_id]["usd"]
    except: return None

def main():
    rate_resp = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD").json()
    myr_rate = rate_resp["conversion_rates"]["MYR"]
    
    cash_usd = PORTFOLIO["cash"]
    s_rows = ""; c_rows = ""
    s_cost = s_val = c_cost = c_val = 0

    # Process Stocks
    for t, u in PORTFOLIO["stocks"].items():
        time.sleep(15) # Safety delay
        p = get_stock_price(t)
        c = COST_BASIS["stocks"][t]
        s_cost += c
        if p:
            v = p * u
            pnl = v - c
            pct = (pnl/c*100)
            s_val += v
            color = "#4caf50" if pnl >= 0 else "#ff5252"
            s_rows += f"<tr><td>{t}</td><td>${c:,.0f}</td><td>${v:,.0f}</td><td style='color:{color}'>${pnl:+,.0f} ({pct:+.0f}%)</td></tr>"

    # Process Crypto
    for cid, u in PORTFOLIO["crypto"].items():
        p = get_crypto_price(cid)
        c = COST_BASIS["crypto"][cid]
        c_cost += c
        if p:
            v = p * u
            pnl = v - c
            pct = (pnl/c*100)
            c_val += v
            color = "#4caf50" if pnl >= 0 else "#ff5252"
            sym = CRYPTO_ACRONYMS.get(cid, cid[:3].upper())
            c_rows += f"<tr><td>{sym}</td><td>${c:,.0f}</td><td>${v:,.0f}</td><td style='color:{color}'>${pnl:+,.0f} ({pct:+.0f}%)</td></tr>"

    total_cap = s_cost + c_cost + cash_usd
    total_val = s_val + c_val + cash_usd
    net_pnl = total_val - total_cap
    net_pct = (net_pnl/total_cap*100)
    pnl_color = "#4caf50" if net_pnl >= 0 else "#ff5252"

    # Diversity
    s_per = (s_val/total_val*100); c_per = (c_val/total_val*100); cash_per = (cash_usd/total_val*100)

    # PLTR-Inspired HTML Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Portfolio OS</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {{ --bg: #0a0a0a; --panel: #141414; --accent: #c3a343; --text: #e0e0e0; }}
            body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 2vw; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .card {{ background: var(--panel); border: 1px solid #222; padding: 20px; border-radius: 4px; }}
            h1, h2 {{ color: var(--accent); text-transform: uppercase; letter-spacing: 2px; font-size: 14px; margin-top: 0; }}
            .big-num {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
            th {{ text-align: left; color: #666; padding-bottom: 10px; text-transform: uppercase; font-size: 10px; }}
            td {{ padding: 8px 0; border-bottom: 1px solid #1f1f1f; }}
            .footer {{ margin-top: 40px; font-size: 10px; color: #444; text-align: center; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <h1>System_Portfolio_v2.0</h1>
        <div class="grid">
            <div class="card">
                <h2>Total Net Value</h2>
                <div class="big-num">${total_val:,.0f}</div>
                <div style="color: #888">RM {total_val*myr_rate:,.0f}</div>
            </div>
            <div class="card">
                <h2>Total P/L</h2>
                <div class="big-num" style="color:{pnl_color}">${net_pnl:+,.0f}</div>
                <div style="color:{pnl_color}">{net_pct:+.2f}% Performance</div>
            </div>
            <div class="card">
                <h2>Allocation</h2>
                <table>
                    <tr><td>Stocks</td><td align="right">{s_per:.0f}%</td></tr>
                    <tr><td>Crypto</td><td align="right">{c_per:.0f}%</td></tr>
                    <tr><td>Cash</td><td align="right">{cash_per:.0f}%</td></tr>
                </table>
            </div>
        </div>

        <div style="margin-top:20px" class="card">
            <h2>Equity & Assets</h2>
            <table>
                <thead><tr><th>Asset</th><th>Cost</th><th>Value</th><th>P/L</th></tr></thead>
                <tbody>{s_rows}{c_rows}</tbody>
            </table>
        </div>

        <div class="footer">Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC | RM Rate: {myr_rate:.2f}</div>
    </body>
    </html>
    """
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    main()