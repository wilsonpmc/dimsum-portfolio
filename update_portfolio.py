import requests
import json
import time
import os
from datetime import datetime, timedelta

# =========================================================================
# Configuration
# =========================================================================
ALPHAVANTAGE_API_KEY = "98TR939RKXQ1MMKS"
EXCHANGERATE_API_KEY = "390764610849850b23dfe230"

GOAL_USD = 250000

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
        return float(data["Global Quote"]["05. price"])
    except: return None

def get_crypto_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try: return requests.get(url).json()[coin_id]["usd"]
    except: return None

def format_currency(val, is_pnl=False, decimals=2):
    """Creates a fixed-width container to align $ signs vertically."""
    prefix = "+" if is_pnl and val > 0 else ""
    return f"<div class='cur-container'><span>$</span><span>{prefix}{val:,.{decimals}f}</span></div>"

def get_icon(symbol):
    return f"https://img.logo.dev/ticker/{symbol}?token=pk_demo"

def main():
    try:
        rate_resp = requests.get(f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/USD").json()
        myr_rate = rate_resp["conversion_rates"]["MYR"]
    except:
        myr_rate = 4.45 
    
    cash_usd = PORTFOLIO["cash"]
    s_rows = ""; c_rows = ""
    s_cost = s_val = c_cost = c_val = 0

    # Equity Processing
    for t, u in PORTFOLIO["stocks"].items():
        time.sleep(15) 
        p = get_stock_price(t); c = COST_BASIS["stocks"][t]
        avg = c / u
        s_cost += c
        if p:
            v = p * u; s_val += v
            pnl = v - c; pct = (pnl/c*100)
            clr = "#008000" if pnl >= 0 else "#FF0000"
            s_rows += f"""
            <tr>
                <td><div class='asset'><img src='{get_icon(t)}' onerror="this.src='https://ui-avatars.com/api/?name={t}&background=000&color=fff'">{t}</div></td>
                <td class='mono'>{format_currency(avg)}</td>
                <td class='mono'>{format_currency(p)}</td>
                <td class='mono'>{format_currency(v, decimals=0)} <small>(RM {v*myr_rate:,.0f})</small></td>
                <td class='mono' style='color:{clr};font-weight:700'>{format_currency(pnl, True, 0)} ({pct:+.0f}%) <small style='color:#888'>[RM {pnl*myr_rate:+,.0f}]</small></td>
            </tr>"""

    # Crypto Processing
    for cid, u in PORTFOLIO["crypto"].items():
        p = get_crypto_price(cid); c = COST_BASIS["crypto"][cid]
        avg = c / u
        c_cost += c
        if p:
            v = p * u; c_val += v
            pnl = v - c; pct = (pnl/c*100)
            sym = CRYPTO_ACRONYMS.get(cid, cid[:3].upper())
            clr = "#008000" if pnl >= 0 else "#FF0000"
            c_rows += f"""
            <tr>
                <td><div class='asset'><img src='{get_icon(sym)}' onerror="this.src='https://ui-avatars.com/api/?name={sym}&background=000&color=fff'">{sym}</div></td>
                <td class='mono'>{format_currency(avg, decimals=4)}</td>
                <td class='mono'>{format_currency(p, decimals=4)}</td>
                <td class='mono'>{format_currency(v, decimals=0)} <small>(RM {v*myr_rate:,.0f})</small></td>
                <td class='mono' style='color:{clr};font-weight:700'>{format_currency(pnl, True, 0)} ({pct:+.0f}%) <small style='color:#888'>[RM {pnl*myr_rate:+,.0f}]</small></td>
            </tr>"""

    total_val = s_val + c_val + cash_usd
    total_cap = s_cost + c_cost + cash_usd
    net_pnl = total_val - total_cap
    net_pct = (net_pnl/total_cap*100)
    
    # Section PNL %
    s_pnl = s_val - s_cost; s_pct = (s_pnl/s_cost*100) if s_cost > 0 else 0
    c_pnl = c_val - c_cost; c_pct = (c_pnl/c_cost*100) if c_cost > 0 else 0

    goal_pct = min((total_val / GOAL_USD) * 100, 100)
    distance_usd = max(GOAL_USD - total_val, 0)
    now_myt = datetime.utcnow() + timedelta(hours=8)
    today_str = now_myt.strftime('%Y-%m-%d')
    myt_time_str = now_myt.strftime('%Y-%m-%d %I:%M %p')

    # History Logic
    history_file = 'history.json'
    history = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f: history = json.load(f)
        except: pass
    history[today_str] = {"val": total_val, "pnl": net_pnl}
    with open(history_file, 'w') as f: json.dump(history, f)

    hist_rows = ""
    for date in sorted(history.keys(), reverse=True):
        d = history[date]
        clr = "#008000" if d['pnl'] >= 0 else "#FF0000"
        hist_rows += f"<tr><td>{date}</td><td class='mono'>{format_currency(d['val'], decimals=0)} <small>(RM {d['val']*myr_rate:,.0f})</small></td><td class='mono' style='color:{clr}'>{format_currency(d['pnl'], True, 0)} <small style='color:#888'>[RM {d['pnl']*myr_rate:+,.0f}]</small></td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>dimsum portfolio</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {{ --bg: #ffffff; --orange: #ff6600; --sub: #666; --table-grey: #f4f4f4; }}
            body {{ background: var(--bg); color: #000; font-family: 'Inter', sans-serif; margin: 0; padding: 25px; }}
            .sync-remark {{ color: var(--orange); font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; margin-bottom: 5px; text-transform: uppercase; }}
            header {{ font-family: 'JetBrains Mono', monospace; font-size: 14px; border: 1.5px solid #000; display: inline-block; padding: 6px 15px; margin-bottom: 30px; font-weight: 700; }}
            .summary {{ display: flex; flex-wrap: wrap; border-top: 2.2px solid #000; margin-bottom: 20px; }}
            .item {{ flex: 1; min-width: 150px; padding: 25px 0; border-right: 1px solid #f0f0f0; }}
            .label {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; color: var(--sub); text-transform: uppercase; margin-bottom: 8px; }}
            .val {{ font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 700; letter-spacing: -1px; }}
            .sub-rm {{ font-size: 11px; color: var(--sub); font-family: 'JetBrains Mono', monospace; margin-top: 4px; display: block; }}
            .goal-container {{ margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
            .progress-bar {{ width: 100%; height: 8px; background: #eee; border-radius: 4px; overflow: hidden; margin: 10px 0; }}
            .progress-fill {{ width: {goal_pct}%; height: 100%; background: #000; }}
            .section-label {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; border-bottom: 1.5px solid #000; padding-bottom: 6px; margin: 40px 0 15px 0; text-transform: uppercase; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            th {{ text-align: left; font-size: 10px; color: #999; text-transform: uppercase; padding-bottom: 10px; font-weight: 400; }}
            td {{ padding: 14px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }}
            .mono {{ font-family: 'JetBrains Mono', monospace; }}
            .cur-container {{ display: inline-flex; justify-content: space-between; width: 110px; }}
            small {{ font-family: 'JetBrains Mono', monospace; color: #888; font-size: 10px; margin-left: 8px; }}
            .asset {{ display: flex; align-items: center; gap: 10px; font-weight: 600; }}
            .asset img {{ width: 22px; height: 22px; border-radius: 50%; border: 1px solid #eee; background: #fff; }}
            .total-row {{ font-family: 'JetBrains Mono', monospace; font-weight: 700; background: #000; color: #fff; }}
            .total-row td {{ padding: 14px 10px; border: none; }}
            .total-row small {{ color: #bbb; }}
            .hist-table {{ background: var(--table-grey); }}
            .hist-table td {{ padding: 15px 10px; border-bottom: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="sync-remark">SYNC NODE MY // {myt_time_str} MYT</div>
        <header>dimsum portfolio</header>

        <div class="summary">
            <div class="item">
                <div class="label">Net Portfolio Value</div>
                <div class="val">${total_val:,.0f}</div>
                <span class="sub-rm">RM {total_val*myr_rate:,.0f}</span>
            </div>
            <div class="item" style="padding-left: 20px;">
                <div class="label">Total Profit Loss</div>
                <div class="val" style="color:{'#008000' if net_pnl >= 0 else '#FF0000'}">{net_pnl:+,.0f}</div>
                <span class="sub-rm" style="color:{'#008000' if net_pnl >= 0 else '#FF0000'}">{net_pct:+.2f}% / RM {net_pnl*myr_rate:+,.0f}</span>
            </div>
            <div class="item" style="padding-left: 20px;">
                <div class="label">Cash on Hand</div>
                <div class="val">${cash_usd:,.0f}</div>
                <span class="sub-rm">MYR {cash_usd*myr_rate:,.0f}</span>
            </div>
        </div>

        <div class="goal-container">
            <div class="label">Goal Tracking: Target $250,000</div>
            <div class="progress-bar"><div class="progress-fill"></div></div>
            <div style="display:flex; justify-content:space-between;">
                <span class="sub-rm">{goal_pct:.1f}% Complete</span>
                <span class="sub-rm">Distance: ${distance_usd:,.0f} USD (RM {distance_usd*myr_rate:,.0f})</span>
            </div>
        </div>

        <div class="section-label">Equity Assets</div>
        <table>
            <thead><tr><th>Ticker</th><th>Avg Cost</th><th>Current Price</th><th>Market Val</th><th>P/L Absolute</th></tr></thead>
            <tbody>
                {s_rows}
                <tr class="total-row">
                    <td>EQUITY TOTAL</td>
                    <td><div class='cur-container'><span> </span><span>-</span></div></td>
                    <td><div class='cur-container'><span> </span><span>-</span></div></td>
                    <td>{format_currency(s_val, decimals=0)} <small>(RM {s_val*myr_rate:,.0f})</small></td>
                    <td>{format_currency(s_pnl, True, 0)} ({s_pct:+.0f}%) <small>(RM {s_pnl*myr_rate:+,.0f})</small></td>
                </tr>
            </tbody>
        </table>

        <div class="section-label">Crypto Assets</div>
        <table>
            <thead><tr><th>Asset</th><th>Avg Cost</th><th>Current Price</th><th>Market Val</th><th>P/L Absolute</th></tr></thead>
            <tbody>
                {c_rows}
                <tr class="total-row">
                    <td>CRYPTO TOTAL</td>
                    <td><div class='cur-container'><span> </span><span>-</span></div></td>
                    <td><div class='cur-container'><span> </span><span>-</span></div></td>
                    <td>{format_currency(c_val, decimals=0)} <small>(RM {c_val*myr_rate:,.0f})</small></td>
                    <td>{format_currency(c_pnl, True, 0)} ({c_pct:+.0f}%) <small>(RM {c_pnl*myr_rate:+,.0f})</small></td>
                </tr>
            </tbody>
        </table>

        <div class="section-label">Daily History Log</div>
        <table class="hist-table">
            <thead><tr><th>Date</th><th>Net Value</th><th>Total P/L</th></tr></thead>
            <tbody>{hist_rows}</tbody>
        </table>
    </body>
    </html>
    """
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    main()
