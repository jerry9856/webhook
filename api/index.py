from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()

    # 從傳入的訊息中取得 userId
    for event in data['events']:
        user_id = event['source']['userId']
        print(f"Received message from user: {user_id}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run()
