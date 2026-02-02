import requests
import json
import time
from datetime import datetime, timedelta

# =========================================================================
# Configuration
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
# Helper Functions
# =========================================================================

def get_stock_price(ticker):
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHAVANTAGE_API_KEY}"
    try:
        data = requests.get(url).json()
        if "Global Quote" in data:
            return float(data["Global Quote"]["05. price"])
        return None
    except: return None

def get_crypto_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        return requests.get(url).json()[coin_id]["usd"]
    except: return None

def get_icon(symbol, is_crypto=False):
    # Logo.dev is high-reliability for both tickers and tokens
    return f"https://img.logo.dev/ticker/{symbol}?token=pk_demo"

# =========================================================================
# Main Execution Logic
# =========================================================================

def main():
    # Fetch FX Rate
    try:
        rate_resp = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD").json()
        myr_rate = rate_resp["conversion_rates"]["MYR"]
    except:
        myr_rate = 4.45 
    
    cash_usd = PORTFOLIO["cash"]
    s_rows = ""; c_rows = ""
    s_cost = s_val = c_cost = c_val = 0

    # 1. Process Stocks
    for t, u in PORTFOLIO["stocks"].items():
        time.sleep(15) # Wait for API limits
        p = get_stock_price(t)
        c = COST_BASIS["stocks"][t]
        s_cost += c
        if p:
            v = p * u
            s_val += v
            pnl = v - c
            pct = (pnl/c*100) if c > 0 else 0
            clr = "#008000" if pnl >= 0 else "#FF0000"
            s_rows += f"""
            <tr>
                <td><div class='asset'><img src='{get_icon(t)}' onerror="this.src='https://ui-avatars.com/api/?name={t}&background=000&color=fff'">{t}</div></td>
                <td>${c:,.0f}</td>
                <td>${v:,.0f}</td>
                <td style='color:{clr}; font-weight:700'>${pnl:+,.0f} ({pct:+.0f}%)</td>
            </tr>"""

    # 2. Process Crypto
    for cid, u in PORTFOLIO["crypto"].items():
        p = get_crypto_price(cid)
        c = COST_BASIS["crypto"][cid]
        c_cost += c
        if p:
            v = p * u
            c_val += v
            pnl = v - c
            pct = (pnl/c*100) if c > 0 else 0
            sym = CRYPTO_ACRONYMS.get(cid, cid[:3].upper())
            clr = "#008000" if pnl >= 0 else "#FF0000"
            c_rows += f"""
            <tr>
                <td><div class='asset'><img src='{get_icon(sym, True)}' onerror="this.src='https://ui-avatars.com/api/?name={sym}&background=000&color=fff'">{sym}</div></td>
                <td>${c:,.0f}</td>
                <td>${v:,.0f}</td>
                <td style='color:{clr}; font-weight:700'>${pnl:+,.0f} ({pct:+.0f}%)</td>
            </tr>"""

    total_val = s_val + c_val + cash_usd
    total_cap = s_cost + c_cost + cash_usd
    net_pnl = total_val - total_cap
    net_pct = (net_pnl/total_cap*100) if total_cap > 0 else 0
    pnl_clr = "#008000" if net_pnl >= 0 else "#FF0000"
    
    myt_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %I:%M %p')

    # 3. Final HTML Template
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>dimsum portfolio</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {{ --bg: #ffffff; --text: #000000; --sub: #666; }}
            body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 25px; }}
            header {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; border: 1.5px solid #000; display: inline-block; padding: 6px 15px; margin-bottom: 40px; font-weight: 700; }}
            .summary {{ display: flex; flex-wrap: wrap; border-top: 2.2px solid #000; margin-bottom: 40px; }}
            .item {{ flex: 1; min-width: 150px; padding: 25px 0; border-right: 1px solid #f0f0f0; }}
            .label {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: var(--sub); text-transform: uppercase; margin-bottom: 8px; }}
            .val {{ font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; letter-spacing: -1px; }}
            .sub {{ font-size: 11px; color: var(--sub); font-family: 'JetBrains Mono', monospace; }}
            .section-label {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; border-bottom: 1.5px solid #000; padding-bottom: 6px; margin: 40px 0 15px 0; text-transform: uppercase; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; font-size: 10px; color: #999; text-transform: uppercase; padding-bottom: 12px; font-weight: 400; }}
            td {{ padding: 16px 0; border-bottom: 1px solid #f0f0f0; font-size: 13.5px; }}
            .asset {{ display: flex; align-items: center; gap: 10px; font-weight: 600; }}
            .asset img {{ width: 22px; height: 22px; border-radius: 50%; border: 1px solid #eee; background: #fff; object-fit: contain; }}
            .total-row {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; background: #000; color: #fff; }}
            .total-row td {{ padding: 14px 10px; border: none; }}
            footer {{ margin-top: 80px; font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #ccc; }}
        </style>
    </head>
    <body>
        <header>dimsum portfolio</header>
        <div class="summary">
            <div class="item">
                <div class="label">Net Portfolio Value</div>
                <div class="val">${total_val:,.0f}</div>
                <div class="sub">RM {total_val*myr_rate:,.0f}</div>
            </div>
            <div class="item" style="padding-left: 20px;">
                <div class="label">Total Profit Loss</div>
                <div class="val" style="color:{pnl_clr}">{net_pnl:+,.0f}</div>
                <div class="sub" style="color:{pnl_clr}">{net_pct:+.2f}%</div>
            </div>
            <div class="item" style="padding-left: 20px;">
                <div class="label">Total Liquidity</div>
                <div class="val">${cash_usd:,.0f}</div>
                <div class="sub">MYR {cash_usd*myr_rate:,.0f}</div>
            </div>
        </div>
        <div class="section-label">Equity Assets</div>
        <table>
            <thead><tr><th>Ticker</th><th>Cost</th><th>Market Val</th><th>P/L Absolute</th></tr></thead>
            <tbody>
                {s_rows}
                <tr class="total-row"><td>STOCKS TOTAL</td><td>${s_cost:,.0f}</td><td>${s_val:,.0f}</td><td>${(s_val-s_cost):+,.0f}</td></tr>
            </tbody>
        </table>
        <div class="section-label">Digital Ledger</div>
        <table>
            <thead><tr><th>Asset</th><th>Cost</th><th>Market Val</th><th>P/L Absolute</th></tr></thead>
            <tbody>
                {c_rows}
                <tr class="total-row"><td>CRYPTO TOTAL</td><td>${c_cost:,.0f}</td><td>${c_val:,.0f}</td><td>${(c_val-c_cost):+,.0f}</td></tr>
            </tbody>
        </table>
        <footer>
            SYNC MY // {myt_time} MYT // 1 USD : {myr_rate:.2f} MYR
        </footer>
    </body>
    </html>
    """
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    main()
