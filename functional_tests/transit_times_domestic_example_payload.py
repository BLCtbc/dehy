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


import requests, json, os

FEDEX_SHIPPING_ACCOUNT,FEDEX_TEST_API_KEY,FEDEX_TEST_SECRET_KEY="740561073",'l73997ca49b8154d50ac74dec90581488b','f45d98b788424359907078e9da1158cf'

oauth_payload = f"grant_type=client_credentials&client_id={FEDEX_TEST_API_KEY}&client_secret={FEDEX_TEST_SECRET_KEY}"

oauth_url,oauth_headers = "https://apis-sandbox.fedex.com/oauth/token", {'Content-Type': "application/x-www-form-urlencoded"}

oauth_response = requests.request("POST", oauth_url, data=oauth_payload, headers=oauth_headers)
response = json.loads(oauth_response.text)
oauth_token,oauth_bearer = response["access_token"],response["token_type"]




# working payload
url,headers,payload="https://apis-sandbox.fedex.com/rate/v1/rates/quotes", {
   'Content-Type': "application/json",
   'X-locale': "en_US",
   'Authorization': "Bearer " + oauth_token
},{
  "accountNumber": {
    "value": FEDEX_SHIPPING_ACCOUNT
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


response_list = json.loads(response.text)

rate_list = response_list['output']['rateReplyDetails']
for rate in rate_list:
	cost = rate['ratedShipmentDetails'][0]['totalNetCharge']
	print('code: ', rate['serviceType'])
	print('name: ', rate['serviceName'])
	print('cost: ', cost)

	methods.append(
		BaseFedex(code=rate['serviceType'], name=rate['serviceName'], charge_excl_tax=cost, charge_incl_tax=cost)
	)

# for testing
file_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), 'rate_output.json'))

with open(file_path, 'w+') as f:
	json.dumps(response.text, f, indent=4)

with open(file_path, 'w+') as f:
	f.write(response.text)

with open(file_path, 'r') as f:
	json_rate_data = json.loads(f.read())

f.close()
json_rate_data = json.loads(open(file_path, "r"))

payload={
  "accountNumber": {
    "value": FEDEX_SHIPPING_ACCOUNT
  },
  "carrierCodes": ["FDXE", "FDXG"],
  "requestedShipment": {
	  "recipient": {
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
    "shipper": {
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

payload={
  "accountNumber": {
	"value": FEDEX_SHIPPING_ACCOUNT
  },
  "carrierCodes": ["FDXE", "FDXG"],
  "rateRequestControlParameters": {
	"returnTransitTimes": True,
	"rateSortOrder": "COMMITASCENDING"
  },
  "requestedShipment": {
	"shipper": {
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
	"recipient": {
	  "address": {
	  "streetLines": [
			"11112 Furrow Hill Drive"
		  ],
		"postalCode": 78759,
		"city": "Austin",
		"stateOrProvinceCode": "TX",
		"countryCode": "US"
	  }
	},
	"pickupType": "DROPOFF_AT_FEDEX_LOCATION",
	"rateRequestType": [
	  "LIST",
	  "ACCOUNT"
	],
	"requestedPackageLineItems": [
	  {
		"weight": {
		  "units": "LB",
		  "value": 11.1
		}
	  }
	]
  }
}