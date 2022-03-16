import base64, json, requests

### begin get carrier info example
url = "https://ssapi.shipstation.com/carriers/listservices?carrierCode=fedex"
API_KEY,API_SECRET = '47723157d4684200a411a6b9c0987048','b1ca69fafef54cc98dfd05e7f60b5dea'

SHIPSTATION_AUTH_STR = bytes(f"{API_KEY}:{API_SECRET}", encoding='utf-8')
SHIPSTATION_AUTH_KEY = base64.b64encode(SHIPSTATION_AUTH_STR)

AUTH_TOKEN = f"Basic {SHIPSTATION_AUTH_KEY.decode()}"

auth_headers,auth_payload = {
  'Host': 'ssapi.shipstation.com',
  'Authorization': AUTH_TOKEN
},{}

response = requests.request("GET", url, headers=auth_headers, data=auth_payload)

response_text = json.loads(response.text)
print(response.text)
### end carrier info example

### begin get rates example

url = "https://ssapi.shipstation.com/shipments/getrates"

example_payload = "{\n  \"carrierCode\": \"fedex\",\n  \"serviceCode\": null,\n  \"packageCode\": null,\n  \"fromPostalCode\": \"78703\",\n  \"toState\": \"DC\",\n  \"toCountry\": \"US\",\n  \"toPostalCode\": \"20500\",\n  \"toCity\": \"Washington\",\n  \"weight\": {\n    \"value\": 3,\n    \"units\": \"ounces\"\n  },\n  \"dimensions\": {\n    \"units\": \"inches\",\n    \"length\": 7,\n    \"width\": 5,\n    \"height\": 6\n  },\n  \"confirmation\": \"delivery\",\n  \"residential\": false\n}"

payload = {"carrierCode":"fedex", "serviceCode": None,"packageCode": None,"fromPostalCode":"78759","toState":"TX","toCountry":"US","toPostalCode": "78701","toCity": "Austin","weight": {"value": 3,"units":"ounces"},"dimensions":{"units":"inches","height": 4,"length": 4,"width": 4},"confirmation": "delivery","residential": False}
headers = {
  'Host': 'ssapi.shipstation.com',
  'Authorization': AUTH_TOKEN,
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.text.encode('utf8'))