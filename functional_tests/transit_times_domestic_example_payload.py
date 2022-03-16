{ "accountNumber": {
    "value": "740561073"
  },
  "requestedShipment": {
    "shipper": {
      "address": {
		"streetLines": [
            "11112 Furrow Hill Drive"
          ],
        "postalCode": "78759",
        "city": "Austin",
        "stateOrProvinceCode":"TX",
        "countryCode": "US"
      }
    },
    "recipients": [
      {
        "address": {
			"streetlines": [
				"120 NE 9th Ave"
			],
	        "postalCode": "32054",
	        "city": "Lake Butler",
	        "stateOrProvinceCode":"FL",
	        "countryCode": "US"
        }
      }
    ],
    "packagingType": "YOUR_PACKAGING",
    "requestedPackageLineItems": [
      {
        "weight": {
          "units": "LB",
          "value": "2"
        }
      }
    ]
  },
  "carrierCodes": [
    "FDXG"
  ]
}


import requests, json

FEDEX_SHIPPING_ACCOUNT=740561073
FEDEX_TEST_API_KEY,FEDEX_TEST_SECRET_KEY='l73997ca49b8154d50ac74dec90581488b','f45d98b788424359907078e9da1158cf'

oauth_payload = f"grant_type=client_credentials&client_id={FEDEX_TEST_API_KEY}&client_secret={FEDEX_TEST_SECRET_KEY}"

oauth_url = "https://apis-sandbox.fedex.com/oauth/token"
oauth_headers = {
    'Content-Type': "application/x-www-form-urlencoded"
}

oauth_response = requests.request("POST", oauth_url, data=oauth_payload, headers=oauth_headers)
response = json.loads(oauth_response.text)
oauth_token,oauth_bearer = response["access_token"],response["token_type"]


headers = {
    'Content-Type': "application/json",
    'X-locale': "en_US",
    'Authorization': "Bearer " + oauth_token
}

url = "https://apis-sandbox.fedex.com/rate/v1/rates/quotes"
payload={
  "accountNumber": {
    "value": "740561073"
  },
  "requestedShipment": {
	  "shipper": {
        "address": {
  		"streetLines": [
              "11112 Furrow Hill Drive"
            ],
          "postalCode": 78759,
          "city": "Austin",
          "stateOrProvinceCode":"TX",
          "countryCode": "US"
        }
      },
    "recipient": {
      "address": {
		"streetLines": [
			"512 Rio Grande St"
		],
		"city":"Austin",
		"stateOrProvinceCode":"TX",
        "postalCode": 78701,
        "countryCode": "US"
      }
    },
    "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
    "serviceType": "PRIORITY_OVERNIGHT",
    "rateRequestType": [
      "LIST",
      "ACCOUNT"
    ],
    "requestedPackageLineItems": [
      {
        "weight": {
          "units": "LB",
          "value": 1
        }
      }
    ]
  }
}
response = requests.request("POST", url, data=json.dumps(payload), headers=headers)