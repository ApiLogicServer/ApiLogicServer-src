# Step 1: Install Flask and Requests libraries
# Run this once: pip install flask requests

import json
from flask import Flask, jsonify, request
from flask import make_response
import requests

app = Flask(__name__)

@app.before_request
def before_any_request():
    print(f"[DEBUG] Incoming request: {request.method} {request.url}")

# Step 2: Proxy endpoint to fix /api/Customer
@app.route('/api/Customer')
def proxy_customer():
    import pprint
    real_url = 'https://your-ngrok-url.ngrok-free.app/api/Customer'
    real_url = 'http://localhost:5656/api/Customer'

    try:
        print(f"[Proxy] Forwarding to: {real_url}")
        print(f"[Proxy] With params: {request.args}")

        response = requests.get(real_url, params=request.args, headers={'Accept': 'application/json'})
        response.raise_for_status()
        real_data = response.json()

        print("[Proxy] Got response:")
        pprint.pprint(real_data)

        transformed_data = {
            "data": []
        }

        transformed_data = {
            "data": [
                {
                    "type": "Customer",
                    "id": attributes.get("Id"),
                    "attributes": attributes
                } for item in real_data.get("data", [])
                if (attributes := item.get("attributes"))
            ]
        }

        for item in real_data.get("data", []):
            attributes = item.get("attributes", {})
            attributes.pop("Id", None)  # Remove duplicate ID TODO
            transformed_data["data"].append({
                "type": "Customer",
                "id": item.get("id") or attributes.get("Id"),
                "attributes": attributes
            })


        response_json = json.dumps(transformed_data)
        response_obj = make_response(response_json)
        response_obj.headers["Content-Type"] = "application/vnd.api+json"
        return response_obj
    except Exception as e:
        print("[Proxy] ERROR:", e)
        return jsonify({"error": str(e)}), 500

# Run the proxy locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)

#  test:
# http://localhost:6000/api/Customer
# curl "http://localhost:6000/api/Customer?filter%5BCountry%5D=Germany&page%5Blimit%5D=2"
