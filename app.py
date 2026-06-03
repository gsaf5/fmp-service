from flask import Flask, jsonify, request, Response
import requests
import os

app = Flask(__name__)

FMP_KEY = os.environ.get("FMP_API_KEY", "TiUMLS7qhCpwLRIPcJKodOAKn4Bm82RC")
FMP_BASE = "https://financialmodelingprep.com/stable"

@app.route("/")
def health():
    # HTML root page — indexed by search engines so Claude can unlock the domain via web_search
    html = """<!DOCTYPE html>
<html>
<head><title>FMP Price Service</title></head>
<body>
<h1>FMP Price Service</h1>
<p>Live stock price API. Endpoint: https://web-production-fa80.up.railway.app/quote?symbols=NVDA,AAPL</p>
<p>Status: live</p>
</body>
</html>"""
    return Response(html, mimetype="text/html")

@app.route("/quote")
def quote():
    symbols = request.args.get("symbols", "")
    if not symbols:
        return jsonify({"error": "No symbols provided"}), 400

    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    results = []

    for symbol in symbol_list:
        try:
            r = requests.get(
                f"{FMP_BASE}/quote",
                params={"symbol": symbol, "apikey": FMP_KEY},
                timeout=5
            )
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                q = data[0]
                results.append({
                    "symbol": q.get("symbol"),
                    "name": q.get("name"),
                    "price": q.get("price"),
                    "change": q.get("change"),
                    "changePercent": q.get("changePercentage"),
                    "dayHigh": q.get("dayHigh"),
                    "dayLow": q.get("dayLow"),
                    "yearHigh": q.get("yearHigh"),
                    "yearLow": q.get("yearLow"),
                    "volume": q.get("volume"),
                    "avgVolume": q.get("avgVolume"),
                    "marketCap": q.get("marketCap"),
                    "open": q.get("open"),
                    "previousClose": q.get("previousClose"),
                    "exchange": q.get("exchange"),
                })
            else:
                results.append({"symbol": symbol, "error": "No data returned"})
        except Exception as e:
            results.append({"symbol": symbol, "error": str(e)})

    return jsonify(results)

@app.route("/news")
def news():
    symbol = request.args.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
    try:
        r = requests.get(
            f"{FMP_BASE}/news/stock",
            params={"symbols": symbol, "limit": 5, "apikey": FMP_KEY},
            timeout=5
        )
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/insider")
def insider():
    symbol = request.args.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
    try:
        r = requests.get(
            f"{FMP_BASE}/insider-trading",
            params={"symbol": symbol, "limit": 10, "apikey": FMP_KEY},
            timeout=5
        )
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/earnings")
def earnings():
    symbol = request.args.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
    try:
        r = requests.get(
            f"{FMP_BASE}/earnings-surprises",
            params={"symbol": symbol, "limit": 8, "apikey": FMP_KEY},
            timeout=5
        )
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
