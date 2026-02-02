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

# Helper to get official brand icons
def get_icon(symbol, is_crypto=False):
    if is_crypto:
        # Using a reliable crypto icon CDN
        return f"https://cryptoicons.org/api/icon/{symbol.lower()}/200"
    else:
        # Using Clearbit for stock logos based on company domain
        domains = {"NVDA": "nvidia.com", "ACHR": "archer.com", "AMD": "amd.com"}
        domain = domains.get(symbol, f"{symbol.lower()}.com")
        return f"https://logo.clearbit.com/{domain}"

# =========================================================================
# Main Logic
# =========================================================================

def main():
    rate_resp = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD").json()
    myr_rate = rate_resp["conversion_rates"]["MYR"]
    
    cash_usd = PORTFOLIO["cash"]
    s_rows = ""; c_rows = ""
    s_cost = s_val = c_cost = c_val = 0

    # Process Stocks
    for t, u in PORTFOLIO["stocks"].items():
        time.sleep(15) 
        p = get_stock_price(t); c = COST_BASIS["stocks"][t]
        s_cost += c
        if p:
            v = p * u
            s_val += v
            pnl = v - c; pct = (pnl/c*100)
            icon_url = get_icon(t)
            s_rows += f"""
            <tr>
                <td><div class='asset-cell'><img src='{icon_url}' class='logo'>{t}</div></td>
                <td>${c:,.0f}</td>
                <td>${v:,.0f}</td>
                <td style='font-weight:700'>${pnl:+,.0f} ({pct:+.0f}%)</td>
            </tr>"""

    # Process Crypto
    for cid, u in PORTFOLIO["crypto"].items():
        p = get_crypto_price(cid); c = COST_BASIS["crypto"][cid]
        c_cost += c
        if p:
            v = p * u
            c_val += v
            pnl = v - c; pct = (pnl/c*100)
            sym = CRYPTO_ACRONYMS.get(cid, cid[:3].upper())
            icon_url = get_icon(sym, is_crypto=True)
            c_rows += f"""
            <tr>
                <td><div class='asset-cell'><img src='{icon_url}' class='logo'>{sym}</div></td>
                <td>${c:,.0f}</td>
                <td>${v:,.0f}</td>
                <td style='font-weight:700'>${pnl:+,.0f} ({pct:+.0f}%)</td>
            </tr>"""

    total_val = s_val + c_val + cash_usd
    total_cap = s_cost + c_cost + cash_usd
    net_pnl = total_val - total_cap
    net_pct = (net_pnl/total_cap*100)
    malaysia_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')

    # HTML Output
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>dimsum_portfolio</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap" rel="stylesheet">
        <style>
            :root {{ --bg: #ffffff; --text: #000000; --border: #000000; --sub: #666; }}
            body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 40px; }}
            h1 {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; margin: 0 0 50px 0; border: 1px solid #000; display: inline-block; padding: 5px 12px; text-transform: lowercase; }}
            .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); border-top: 2px solid #000; margin-bottom: 60px; }}
            .summary-item {{ padding: 30px 0; border-right: 1px solid #eee; }}
            .label {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--sub); margin-bottom: 12px; }}
            .value {{ font-family: 'JetBrains Mono', monospace; font-size: 32px; font-weight: 700; letter-spacing: -1px; }}
            .sub-value {{ font-size: 12px; color: var(--sub); margin-top: 4px; font-family: 'JetBrains Mono', monospace; }}
            .section-label {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; border-bottom: 1px solid #000; padding-bottom: 8px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 60px; }}
            th {{ text-align: left; font-size: 10px; color: #999; text-transform: uppercase; padding-bottom: 15px; font-weight: 400; }}
            td {{ padding: 18px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
            .asset-cell {{ display: flex; align-items: center; gap: 12px; font-weight: 600; }}
            .logo {{ width: 24px; height: 24px; border-radius: 50%; border: 1px solid #eee; background: #fff; object-fit: contain; }}
            .total-row {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; background: #000; color: #fff; }}
            .total-row td {{ padding: 15px 10px; border: none; }}
            footer {{ margin-top: 100px; font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #ccc; text-align: left; }}
        </style>
    </head>
    <body>
        <h1>dimsum_portfolio</h1>
        
        <div class="summary-grid">
            <div class="summary-item">
                <div class="label">Net_Value</div>
                <div class="value">${total_val:,.0f}</div>
                <div class="sub-value">RM {total_val*myr_rate:,.0f}</div>
            </div>
            <div class="summary-item" style="padding-left: 20px;">
                <div class="label">P/L_Total</div>
                <div class="value">{net_pnl:+,.0f}</div>
                <div class="sub-value">{net_pct:+.2f}% Perf</div>
            </div>
            <div class="summary-item" style="padding-left: 20px;">
                <div class="label">Liquidity</div>
                <div class="value">${cash_usd:,.0f}</div>
                <div class="sub-value">MYR {cash_usd*myr_rate:,.0f}</div>
            </div>
        </div>

        <div class="section-label">EQUITY_MARKETS</div>
        <table>
            <thead><tr><th>Ticker</th><th>Cost</th><th>Market Val</th><th>P/L Absolute</th></tr></thead>
            <tbody>
                {s_rows}
                <tr class="total-row"><td>TOTAL_EQUITY</td><td>${s_cost:,.0f}</td><td>${s_val:,.0f}</td><td>${(s_val-s_cost):+,.0f}</td></tr>
            </tbody>
        </table>

        <div class="section-label">DIGITAL_LEDGER</div>
        <table>
            <thead><tr><th>Token</th><th>Cost</th><th>Market Val</th><th>P/L Absolute</th></tr></thead>
            <tbody>
                {c_rows}
                <tr class="total-row"><td>TOTAL_CRYPTO</td><td>${c_cost:,.0f}</td><td>${c_val:,.0f}</td><td>${(c_val-c_cost):+,.0f}</td></tr>
            </tbody>
        </table>

        <footer>
            TERMINAL_ID_DIMSUM // {malaysia_time} MYT // 1.00_USD:{myr_rate:.2f}_MYR
        </footer>
    </body>
    </html>
    """
    with open("index.html", "w") as f:
        f.write(html_content)

# Note: Ensure get_stock_price and get_crypto_price functions remain at top
if __name__ == "__main__":
    main()
