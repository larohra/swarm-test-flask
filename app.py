from flask import Flask, jsonify, request

app = Flask(__name__)

items = []


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/items", methods=["GET"])
def get_items():
    return jsonify(items)


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data or "name" not in data or "description" not in data:
        return jsonify({"error": "name and description are required"}), 400
    item = {"id": len(items) + 1, "name": data["name"], "description": data["description"]}
    items.append(item)
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)
