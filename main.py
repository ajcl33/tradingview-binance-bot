from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)

SYMBOL = "BTCUSDT"
QUANTITY_USDT = 35  # Valor da ordem em USDT

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data or "code" not in data:
        return jsonify({"error": "JSON inválido"}), 400

    code = data["code"]

    if code.startswith("ENTER-LONG"):
        return entrar()
    elif code.startswith("EXIT-ALL"):
        return sair()
    else:
        return jsonify({"error": "Código não reconhecido"}), 400

def entrar():
    try:
        ticker = client.get_symbol_ticker(symbol=SYMBOL)
        price = float(ticker["price"])
        quantity = round(QUANTITY_USDT / price, 6)

        order = client.order_market_buy(symbol=SYMBOL, quantity=quantity)
        return jsonify({"message": "Compra executada", "order": order}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def sair():
    try:
        balance = client.get_asset_balance(asset="BTC")
        quantidade_btc = float(balance["free"])
        if quantidade_btc < 0.0001:
            return jsonify({"message": "Sem BTC suficiente"}), 200

        order = client.order_market_sell(symbol=SYMBOL, quantity=round(quantidade_btc, 6))
        return jsonify({"message": "Venda executada", "order": order}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
