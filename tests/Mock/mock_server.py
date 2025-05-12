from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

# Basit bot tespit kuralları
BLOCKED_USER_AGENTS = ["python-requests", "curl", "bot", "scraper"]
MIN_REQUEST_INTERVAL = 2  # seconds

last_request_time = {}

@app.route("/product", methods=["GET"])
def product_page():
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "").lower()
    current_time = time.time()

    # 1. User-Agent Bot Kontrolü
    if any(bot in user_agent for bot in BLOCKED_USER_AGENTS):
        return jsonify({"status": "blocked", "reason": "User-Agent looks like a bot!"}), 403

    # 2. IP Rate Limit Kontrolü
    last_time = last_request_time.get(client_ip, 0)
    if current_time - last_time < MIN_REQUEST_INTERVAL:
        return jsonify({"status": "blocked", "reason": "Too many requests!"}), 429

    last_request_time[client_ip] = current_time

    # 3. Header Kontrolü
    if "accept-language" not in request.headers:
        return jsonify({"status": "blocked", "reason": "Missing Accept-Language header!"}), 400

    # Başarılı istek
    return jsonify({
        "status": "ok",
        "message": "Welcome to the fake product page!",
        "product": random.choice(["Laptop", "Phone", "Headphones"])
    })

if __name__ == "__main__":
    app.run(port=5050)