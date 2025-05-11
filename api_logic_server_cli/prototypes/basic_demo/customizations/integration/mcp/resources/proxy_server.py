from flask import Flask, request, make_response
import requests
import json

app = Flask(__name__)

@app.route('/api/Customer')
def proxy_customer():
    # The real API endpoint
    real_url = 'https://your-real-server.ngrok-free.app/api/Customer'

    try:
        # Fetch from the actual API
        response = requests.get(real_url, params=request.args, headers={'Accept': 'application/json'})
        response.raise_for_status()
        real_data = response.json()

        transformed_data = {
            "data": [],
            "jsonapi": {"version": "1.0"},
            "links": {"self": request.url}
        }

        # Convert each customer to JSON:API format
        for item in real_data.get("data", []):
            attributes = item.get("attributes", {})
            attributes.pop("Id", None)  # Remove duplicate ID if present

            transformed_data["data"].append({
                "type": "Customer",
                "id": item.get("id") or attributes.get("Id"),
                "attributes": attributes
            })

        # JSON:API-compliant response
        response_json = json.dumps(transformed_data)
        response_obj = make_response(response_json)
        response_obj.headers["Content-Type"] = "application/vnd.api+json"
        return response_obj

    except Exception as e:
        error_response = {"errors": [{"title": "Proxy Error", "detail": str(e)}]}
        response_json = json.dumps(error_response)
        response_obj = make_response(response_json, 500)
        response_obj.headers["Content-Type"] = "application/vnd.api+json"
        return response_obj

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)

# test: curl "http://localhost:6000/api/Customer?filter%5BCountry%5D=Germany&page%5Blimit%5D=2"