const FORMS = {
	"additional_info": [
		{
			"classes": "form-container",
			"elems": [
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_purchase_business_type"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Business or Home:"
						},
						{
							"attrs": {
								"id": "id_purchase_business_type",
								"name": "purchase_business_type"
							},
							"elems": [
								{
									"attrs": {
										"value": "b_r"
									},
									"tag": "option",
									"text": "Bar or Restaurant"
								},
								{
									"attrs": {
										"value": "h"
									},
									"tag": "option",
									"text": "Home"
								},
								{
									"attrs": {
										"value": "o"
									},
									"tag": "option",
									"text": "Other"
								}
							],
							"tag": "select"
						},
						{
							"attrs": {
								"class": [
									"helptext"
								]
							},
							"tag": "span",
							"text": "Is this for home or commercial use?"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_business_name"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Business name:"
						},
						{
							"attrs": {
								"id": "id_business_name",
								"maxlength": "100",
								"name": "business_name",
								"required": "",
								"type": "text"
							},
							"classes": "required",
							"tag": "input"
						},
						{
							"attrs": {
								"class": [
									"helptext"
								]
							},
							"tag": "span",
							"text": "What is the name of your Bar/Restaurant/Business?"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		},
		{
			"classes": "error-container button-container",
			"elems": [
				{
					"attrs": {
						"id": "error_container"
					},
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"id": "errors"
							},
							"classes": "col-12 errors",
							"tag": "div"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"aria-label": "Continue",
								"hidden": "",
								"type": "submit"
							},
							"classes": "col-12",
							"tag": "button",
							"text": "Continue"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		}
	],
	"billing_address": [
		{
			"classes": "form-container",
			"elems": [
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_same_as_shipping"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Use shipping address:"
						},
						{
							"attrs": {
								"checked": "",
								"id": "id_same_as_shipping",
								"name": "same_as_shipping",
								"type": "checkbox"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_first_name"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "First name:"
						},
						{
							"attrs": {
								"id": "id_first_name",
								"maxlength": "255",
								"name": "first_name",
								"placeholder": "First name",
								"required": "",
								"type": "text",
								"value": "aaaa"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_last_name"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Last name:"
						},
						{
							"attrs": {
								"id": "id_last_name",
								"maxlength": "255",
								"name": "last_name",
								"placeholder": "Last name",
								"required": "",
								"type": "text",
								"value": "bbbb"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_line1"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "First line of address:"
						},
						{
							"attrs": {
								"id": "id_line1",
								"maxlength": "255",
								"name": "line1",
								"placeholder": "Address 1",
								"required": "",
								"type": "text",
								"value": "4444 Hello Der Dr"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_line2"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Second line of address:"
						},
						{
							"attrs": {
								"id": "id_line2",
								"maxlength": "255",
								"name": "line2",
								"placeholder": "Address 2",
								"type": "text"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_line4"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "City:"
						},
						{
							"attrs": {
								"id": "id_line4",
								"maxlength": "255",
								"name": "line4",
								"placeholder": "City",
								"required": "",
								"type": "text",
								"value": "AUSTIN"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_state"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "State/County:"
						},
						{
							"attrs": {
								"id": "id_state",
								"maxlength": "255",
								"name": "state",
								"placeholder": "State",
								"type": "text",
								"value": "TX"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_postcode"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Post/Zip-code:"
						},
						{
							"attrs": {
								"id": "id_postcode",
								"maxlength": "64",
								"name": "postcode",
								"placeholder": "ZIP Code",
								"required": "",
								"type": "text",
								"value": "78751"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_country"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Country:"
						},
						{
							"attrs": {
								"id": "id_country",
								"name": "country",
								"placeholder": "Country"
							},
							"elems": [
								{
									"attrs": {
										"selected": "",
										"value": "US"
									},
									"tag": "option",
									"text": "United States"
								},
								{
									"attrs": {
										"value": "AF"
									},
									"tag": "option",
									"text": "Afghanistan"
								},
								{
									"attrs": {
										"value": "AL"
									},
									"tag": "option",
									"text": "Albania"
								},
								{
									"attrs": {
										"value": "DZ"
									},
									"tag": "option",
									"text": "Algeria"
								},
								{
									"attrs": {
										"value": "AS"
									},
									"tag": "option",
									"text": "American Samoa"
								},
								{
									"attrs": {
										"value": "AD"
									},
									"tag": "option",
									"text": "Andorra"
								},
								{
									"attrs": {
										"value": "AO"
									},
									"tag": "option",
									"text": "Angola"
								},
								{
									"attrs": {
										"value": "AI"
									},
									"tag": "option",
									"text": "Anguilla"
								},
								{
									"attrs": {
										"value": "AQ"
									},
									"tag": "option",
									"text": "Antarctica"
								},
								{
									"attrs": {
										"value": "AG"
									},
									"tag": "option",
									"text": "Antigua and Barbuda"
								},
								{
									"attrs": {
										"value": "AR"
									},
									"tag": "option",
									"text": "Argentina"
								},
								{
									"attrs": {
										"value": "AM"
									},
									"tag": "option",
									"text": "Armenia"
								},
								{
									"attrs": {
										"value": "AW"
									},
									"tag": "option",
									"text": "Aruba"
								},
								{
									"attrs": {
										"value": "AU"
									},
									"tag": "option",
									"text": "Australia"
								},
								{
									"attrs": {
										"value": "AT"
									},
									"tag": "option",
									"text": "Austria"
								},
								{
									"attrs": {
										"value": "AZ"
									},
									"tag": "option",
									"text": "Azerbaijan"
								},
								{
									"attrs": {
										"value": "BS"
									},
									"tag": "option",
									"text": "Bahamas"
								},
								{
									"attrs": {
										"value": "BH"
									},
									"tag": "option",
									"text": "Bahrain"
								},
								{
									"attrs": {
										"value": "BD"
									},
									"tag": "option",
									"text": "Bangladesh"
								},
								{
									"attrs": {
										"value": "BB"
									},
									"tag": "option",
									"text": "Barbados"
								},
								{
									"attrs": {
										"value": "BY"
									},
									"tag": "option",
									"text": "Belarus"
								},
								{
									"attrs": {
										"value": "BE"
									},
									"tag": "option",
									"text": "Belgium"
								},
								{
									"attrs": {
										"value": "BZ"
									},
									"tag": "option",
									"text": "Belize"
								},
								{
									"attrs": {
										"value": "BJ"
									},
									"tag": "option",
									"text": "Benin"
								},
								{
									"attrs": {
										"value": "BM"
									},
									"tag": "option",
									"text": "Bermuda"
								},
								{
									"attrs": {
										"value": "BT"
									},
									"tag": "option",
									"text": "Bhutan"
								},
								{
									"attrs": {
										"value": "BO"
									},
									"tag": "option",
									"text": "Bolivia, Plurinational State of"
								},
								{
									"attrs": {
										"value": "BQ"
									},
									"tag": "option",
									"text": "Bonaire, Sint Eustatius and Saba"
								},
								{
									"attrs": {
										"value": "BA"
									},
									"tag": "option",
									"text": "Bosnia and Herzegovina"
								},
								{
									"attrs": {
										"value": "BW"
									},
									"tag": "option",
									"text": "Botswana"
								},
								{
									"attrs": {
										"value": "BV"
									},
									"tag": "option",
									"text": "Bouvet Island"
								},
								{
									"attrs": {
										"value": "BR"
									},
									"tag": "option",
									"text": "Brazil"
								},
								{
									"attrs": {
										"value": "IO"
									},
									"tag": "option",
									"text": "British Indian Ocean Territory"
								},
								{
									"attrs": {
										"value": "BN"
									},
									"tag": "option",
									"text": "Brunei Darussalam"
								},
								{
									"attrs": {
										"value": "BG"
									},
									"tag": "option",
									"text": "Bulgaria"
								},
								{
									"attrs": {
										"value": "BF"
									},
									"tag": "option",
									"text": "Burkina Faso"
								},
								{
									"attrs": {
										"value": "BI"
									},
									"tag": "option",
									"text": "Burundi"
								},
								{
									"attrs": {
										"value": "CV"
									},
									"tag": "option",
									"text": "Cabo Verde"
								},
								{
									"attrs": {
										"value": "KH"
									},
									"tag": "option",
									"text": "Cambodia"
								},
								{
									"attrs": {
										"value": "CM"
									},
									"tag": "option",
									"text": "Cameroon"
								},
								{
									"attrs": {
										"value": "CA"
									},
									"tag": "option",
									"text": "Canada"
								},
								{
									"attrs": {
										"value": "KY"
									},
									"tag": "option",
									"text": "Cayman Islands"
								},
								{
									"attrs": {
										"value": "CF"
									},
									"tag": "option",
									"text": "Central African Republic"
								},
								{
									"attrs": {
										"value": "TD"
									},
									"tag": "option",
									"text": "Chad"
								},
								{
									"attrs": {
										"value": "CL"
									},
									"tag": "option",
									"text": "Chile"
								},
								{
									"attrs": {
										"value": "CN"
									},
									"tag": "option",
									"text": "China"
								},
								{
									"attrs": {
										"value": "CX"
									},
									"tag": "option",
									"text": "Christmas Island"
								},
								{
									"attrs": {
										"value": "CC"
									},
									"tag": "option",
									"text": "Cocos (Keeling) Islands"
								},
								{
									"attrs": {
										"value": "CO"
									},
									"tag": "option",
									"text": "Colombia"
								},
								{
									"attrs": {
										"value": "KM"
									},
									"tag": "option",
									"text": "Comoros"
								},
								{
									"attrs": {
										"value": "CG"
									},
									"tag": "option",
									"text": "Congo"
								},
								{
									"attrs": {
										"value": "CD"
									},
									"tag": "option",
									"text": "Congo, The Democratic Republic of the"
								},
								{
									"attrs": {
										"value": "CK"
									},
									"tag": "option",
									"text": "Cook Islands"
								},
								{
									"attrs": {
										"value": "CR"
									},
									"tag": "option",
									"text": "Costa Rica"
								},
								{
									"attrs": {
										"value": "HR"
									},
									"tag": "option",
									"text": "Croatia"
								},
								{
									"attrs": {
										"value": "CU"
									},
									"tag": "option",
									"text": "Cuba"
								},
								{
									"attrs": {
										"value": "CW"
									},
									"tag": "option",
									"text": "Curaçao"
								},
								{
									"attrs": {
										"value": "CY"
									},
									"tag": "option",
									"text": "Cyprus"
								},
								{
									"attrs": {
										"value": "CZ"
									},
									"tag": "option",
									"text": "Czechia"
								},
								{
									"attrs": {
										"value": "CI"
									},
									"tag": "option",
									"text": "Côte d'Ivoire"
								},
								{
									"attrs": {
										"value": "DK"
									},
									"tag": "option",
									"text": "Denmark"
								},
								{
									"attrs": {
										"value": "DJ"
									},
									"tag": "option",
									"text": "Djibouti"
								},
								{
									"attrs": {
										"value": "DM"
									},
									"tag": "option",
									"text": "Dominica"
								},
								{
									"attrs": {
										"value": "DO"
									},
									"tag": "option",
									"text": "Dominican Republic"
								},
								{
									"attrs": {
										"value": "EC"
									},
									"tag": "option",
									"text": "Ecuador"
								},
								{
									"attrs": {
										"value": "EG"
									},
									"tag": "option",
									"text": "Egypt"
								},
								{
									"attrs": {
										"value": "SV"
									},
									"tag": "option",
									"text": "El Salvador"
								},
								{
									"attrs": {
										"value": "GQ"
									},
									"tag": "option",
									"text": "Equatorial Guinea"
								},
								{
									"attrs": {
										"value": "ER"
									},
									"tag": "option",
									"text": "Eritrea"
								},
								{
									"attrs": {
										"value": "EE"
									},
									"tag": "option",
									"text": "Estonia"
								},
								{
									"attrs": {
										"value": "SZ"
									},
									"tag": "option",
									"text": "Eswatini"
								},
								{
									"attrs": {
										"value": "ET"
									},
									"tag": "option",
									"text": "Ethiopia"
								},
								{
									"attrs": {
										"value": "FK"
									},
									"tag": "option",
									"text": "Falkland Islands (Malvinas)"
								},
								{
									"attrs": {
										"value": "FO"
									},
									"tag": "option",
									"text": "Faroe Islands"
								},
								{
									"attrs": {
										"value": "FJ"
									},
									"tag": "option",
									"text": "Fiji"
								},
								{
									"attrs": {
										"value": "FI"
									},
									"tag": "option",
									"text": "Finland"
								},
								{
									"attrs": {
										"value": "FR"
									},
									"tag": "option",
									"text": "France"
								},
								{
									"attrs": {
										"value": "GF"
									},
									"tag": "option",
									"text": "French Guiana"
								},
								{
									"attrs": {
										"value": "PF"
									},
									"tag": "option",
									"text": "French Polynesia"
								},
								{
									"attrs": {
										"value": "TF"
									},
									"tag": "option",
									"text": "French Southern Territories"
								},
								{
									"attrs": {
										"value": "GA"
									},
									"tag": "option",
									"text": "Gabon"
								},
								{
									"attrs": {
										"value": "GM"
									},
									"tag": "option",
									"text": "Gambia"
								},
								{
									"attrs": {
										"value": "GE"
									},
									"tag": "option",
									"text": "Georgia"
								},
								{
									"attrs": {
										"value": "DE"
									},
									"tag": "option",
									"text": "Germany"
								},
								{
									"attrs": {
										"value": "GH"
									},
									"tag": "option",
									"text": "Ghana"
								},
								{
									"attrs": {
										"value": "GI"
									},
									"tag": "option",
									"text": "Gibraltar"
								},
								{
									"attrs": {
										"value": "GR"
									},
									"tag": "option",
									"text": "Greece"
								},
								{
									"attrs": {
										"value": "GL"
									},
									"tag": "option",
									"text": "Greenland"
								},
								{
									"attrs": {
										"value": "GD"
									},
									"tag": "option",
									"text": "Grenada"
								},
								{
									"attrs": {
										"value": "GP"
									},
									"tag": "option",
									"text": "Guadeloupe"
								},
								{
									"attrs": {
										"value": "GU"
									},
									"tag": "option",
									"text": "Guam"
								},
								{
									"attrs": {
										"value": "GT"
									},
									"tag": "option",
									"text": "Guatemala"
								},
								{
									"attrs": {
										"value": "GG"
									},
									"tag": "option",
									"text": "Guernsey"
								},
								{
									"attrs": {
										"value": "GN"
									},
									"tag": "option",
									"text": "Guinea"
								},
								{
									"attrs": {
										"value": "GW"
									},
									"tag": "option",
									"text": "Guinea-Bissau"
								},
								{
									"attrs": {
										"value": "GY"
									},
									"tag": "option",
									"text": "Guyana"
								},
								{
									"attrs": {
										"value": "HT"
									},
									"tag": "option",
									"text": "Haiti"
								},
								{
									"attrs": {
										"value": "HM"
									},
									"tag": "option",
									"text": "Heard Island and McDonald Islands"
								},
								{
									"attrs": {
										"value": "VA"
									},
									"tag": "option",
									"text": "Holy See (Vatican City State)"
								},
								{
									"attrs": {
										"value": "HN"
									},
									"tag": "option",
									"text": "Honduras"
								},
								{
									"attrs": {
										"value": "HK"
									},
									"tag": "option",
									"text": "Hong Kong"
								},
								{
									"attrs": {
										"value": "HU"
									},
									"tag": "option",
									"text": "Hungary"
								},
								{
									"attrs": {
										"value": "IS"
									},
									"tag": "option",
									"text": "Iceland"
								},
								{
									"attrs": {
										"value": "IN"
									},
									"tag": "option",
									"text": "India"
								},
								{
									"attrs": {
										"value": "ID"
									},
									"tag": "option",
									"text": "Indonesia"
								},
								{
									"attrs": {
										"value": "IR"
									},
									"tag": "option",
									"text": "Iran, Islamic Republic of"
								},
								{
									"attrs": {
										"value": "IQ"
									},
									"tag": "option",
									"text": "Iraq"
								},
								{
									"attrs": {
										"value": "IE"
									},
									"tag": "option",
									"text": "Ireland"
								},
								{
									"attrs": {
										"value": "IM"
									},
									"tag": "option",
									"text": "Isle of Man"
								},
								{
									"attrs": {
										"value": "IL"
									},
									"tag": "option",
									"text": "Israel"
								},
								{
									"attrs": {
										"value": "IT"
									},
									"tag": "option",
									"text": "Italy"
								},
								{
									"attrs": {
										"value": "JM"
									},
									"tag": "option",
									"text": "Jamaica"
								},
								{
									"attrs": {
										"value": "JP"
									},
									"tag": "option",
									"text": "Japan"
								},
								{
									"attrs": {
										"value": "JE"
									},
									"tag": "option",
									"text": "Jersey"
								},
								{
									"attrs": {
										"value": "JO"
									},
									"tag": "option",
									"text": "Jordan"
								},
								{
									"attrs": {
										"value": "KZ"
									},
									"tag": "option",
									"text": "Kazakhstan"
								},
								{
									"attrs": {
										"value": "KE"
									},
									"tag": "option",
									"text": "Kenya"
								},
								{
									"attrs": {
										"value": "KI"
									},
									"tag": "option",
									"text": "Kiribati"
								},
								{
									"attrs": {
										"value": "KP"
									},
									"tag": "option",
									"text": "Korea, Democratic People's Republic of"
								},
								{
									"attrs": {
										"value": "KR"
									},
									"tag": "option",
									"text": "Korea, Republic of"
								},
								{
									"attrs": {
										"value": "KW"
									},
									"tag": "option",
									"text": "Kuwait"
								},
								{
									"attrs": {
										"value": "KG"
									},
									"tag": "option",
									"text": "Kyrgyzstan"
								},
								{
									"attrs": {
										"value": "LA"
									},
									"tag": "option",
									"text": "Lao People's Democratic Republic"
								},
								{
									"attrs": {
										"value": "LV"
									},
									"tag": "option",
									"text": "Latvia"
								},
								{
									"attrs": {
										"value": "LB"
									},
									"tag": "option",
									"text": "Lebanon"
								},
								{
									"attrs": {
										"value": "LS"
									},
									"tag": "option",
									"text": "Lesotho"
								},
								{
									"attrs": {
										"value": "LR"
									},
									"tag": "option",
									"text": "Liberia"
								},
								{
									"attrs": {
										"value": "LY"
									},
									"tag": "option",
									"text": "Libya"
								},
								{
									"attrs": {
										"value": "LI"
									},
									"tag": "option",
									"text": "Liechtenstein"
								},
								{
									"attrs": {
										"value": "LT"
									},
									"tag": "option",
									"text": "Lithuania"
								},
								{
									"attrs": {
										"value": "LU"
									},
									"tag": "option",
									"text": "Luxembourg"
								},
								{
									"attrs": {
										"value": "MO"
									},
									"tag": "option",
									"text": "Macao"
								},
								{
									"attrs": {
										"value": "MG"
									},
									"tag": "option",
									"text": "Madagascar"
								},
								{
									"attrs": {
										"value": "MW"
									},
									"tag": "option",
									"text": "Malawi"
								},
								{
									"attrs": {
										"value": "MY"
									},
									"tag": "option",
									"text": "Malaysia"
								},
								{
									"attrs": {
										"value": "MV"
									},
									"tag": "option",
									"text": "Maldives"
								},
								{
									"attrs": {
										"value": "ML"
									},
									"tag": "option",
									"text": "Mali"
								},
								{
									"attrs": {
										"value": "MT"
									},
									"tag": "option",
									"text": "Malta"
								},
								{
									"attrs": {
										"value": "MH"
									},
									"tag": "option",
									"text": "Marshall Islands"
								},
								{
									"attrs": {
										"value": "MQ"
									},
									"tag": "option",
									"text": "Martinique"
								},
								{
									"attrs": {
										"value": "MR"
									},
									"tag": "option",
									"text": "Mauritania"
								},
								{
									"attrs": {
										"value": "MU"
									},
									"tag": "option",
									"text": "Mauritius"
								},
								{
									"attrs": {
										"value": "YT"
									},
									"tag": "option",
									"text": "Mayotte"
								},
								{
									"attrs": {
										"value": "MX"
									},
									"tag": "option",
									"text": "Mexico"
								},
								{
									"attrs": {
										"value": "FM"
									},
									"tag": "option",
									"text": "Micronesia, Federated States of"
								},
								{
									"attrs": {
										"value": "MD"
									},
									"tag": "option",
									"text": "Moldova, Republic of"
								},
								{
									"attrs": {
										"value": "MC"
									},
									"tag": "option",
									"text": "Monaco"
								},
								{
									"attrs": {
										"value": "MN"
									},
									"tag": "option",
									"text": "Mongolia"
								},
								{
									"attrs": {
										"value": "ME"
									},
									"tag": "option",
									"text": "Montenegro"
								},
								{
									"attrs": {
										"value": "MS"
									},
									"tag": "option",
									"text": "Montserrat"
								},
								{
									"attrs": {
										"value": "MA"
									},
									"tag": "option",
									"text": "Morocco"
								},
								{
									"attrs": {
										"value": "MZ"
									},
									"tag": "option",
									"text": "Mozambique"
								},
								{
									"attrs": {
										"value": "MM"
									},
									"tag": "option",
									"text": "Myanmar"
								},
								{
									"attrs": {
										"value": "NA"
									},
									"tag": "option",
									"text": "Namibia"
								},
								{
									"attrs": {
										"value": "NR"
									},
									"tag": "option",
									"text": "Nauru"
								},
								{
									"attrs": {
										"value": "NP"
									},
									"tag": "option",
									"text": "Nepal"
								},
								{
									"attrs": {
										"value": "NL"
									},
									"tag": "option",
									"text": "Netherlands"
								},
								{
									"attrs": {
										"value": "NC"
									},
									"tag": "option",
									"text": "New Caledonia"
								},
								{
									"attrs": {
										"value": "NZ"
									},
									"tag": "option",
									"text": "New Zealand"
								},
								{
									"attrs": {
										"value": "NI"
									},
									"tag": "option",
									"text": "Nicaragua"
								},
								{
									"attrs": {
										"value": "NE"
									},
									"tag": "option",
									"text": "Niger"
								},
								{
									"attrs": {
										"value": "NG"
									},
									"tag": "option",
									"text": "Nigeria"
								},
								{
									"attrs": {
										"value": "NU"
									},
									"tag": "option",
									"text": "Niue"
								},
								{
									"attrs": {
										"value": "NF"
									},
									"tag": "option",
									"text": "Norfolk Island"
								},
								{
									"attrs": {
										"value": "MK"
									},
									"tag": "option",
									"text": "North Macedonia"
								},
								{
									"attrs": {
										"value": "MP"
									},
									"tag": "option",
									"text": "Northern Mariana Islands"
								},
								{
									"attrs": {
										"value": "NO"
									},
									"tag": "option",
									"text": "Norway"
								},
								{
									"attrs": {
										"value": "OM"
									},
									"tag": "option",
									"text": "Oman"
								},
								{
									"attrs": {
										"value": "PK"
									},
									"tag": "option",
									"text": "Pakistan"
								},
								{
									"attrs": {
										"value": "PW"
									},
									"tag": "option",
									"text": "Palau"
								},
								{
									"attrs": {
										"value": "PS"
									},
									"tag": "option",
									"text": "Palestine, State of"
								},
								{
									"attrs": {
										"value": "PA"
									},
									"tag": "option",
									"text": "Panama"
								},
								{
									"attrs": {
										"value": "PG"
									},
									"tag": "option",
									"text": "Papua New Guinea"
								},
								{
									"attrs": {
										"value": "PY"
									},
									"tag": "option",
									"text": "Paraguay"
								},
								{
									"attrs": {
										"value": "PE"
									},
									"tag": "option",
									"text": "Peru"
								},
								{
									"attrs": {
										"value": "PH"
									},
									"tag": "option",
									"text": "Philippines"
								},
								{
									"attrs": {
										"value": "PN"
									},
									"tag": "option",
									"text": "Pitcairn"
								},
								{
									"attrs": {
										"value": "PL"
									},
									"tag": "option",
									"text": "Poland"
								},
								{
									"attrs": {
										"value": "PT"
									},
									"tag": "option",
									"text": "Portugal"
								},
								{
									"attrs": {
										"value": "PR"
									},
									"tag": "option",
									"text": "Puerto Rico"
								},
								{
									"attrs": {
										"value": "QA"
									},
									"tag": "option",
									"text": "Qatar"
								},
								{
									"attrs": {
										"value": "RO"
									},
									"tag": "option",
									"text": "Romania"
								},
								{
									"attrs": {
										"value": "RU"
									},
									"tag": "option",
									"text": "Russian Federation"
								},
								{
									"attrs": {
										"value": "RW"
									},
									"tag": "option",
									"text": "Rwanda"
								},
								{
									"attrs": {
										"value": "RE"
									},
									"tag": "option",
									"text": "Réunion"
								},
								{
									"attrs": {
										"value": "BL"
									},
									"tag": "option",
									"text": "Saint Barthélemy"
								},
								{
									"attrs": {
										"value": "SH"
									},
									"tag": "option",
									"text": "Saint Helena, Ascension and Tristan da Cunha"
								},
								{
									"attrs": {
										"value": "KN"
									},
									"tag": "option",
									"text": "Saint Kitts and Nevis"
								},
								{
									"attrs": {
										"value": "LC"
									},
									"tag": "option",
									"text": "Saint Lucia"
								},
								{
									"attrs": {
										"value": "MF"
									},
									"tag": "option",
									"text": "Saint Martin (French part)"
								},
								{
									"attrs": {
										"value": "PM"
									},
									"tag": "option",
									"text": "Saint Pierre and Miquelon"
								},
								{
									"attrs": {
										"value": "VC"
									},
									"tag": "option",
									"text": "Saint Vincent and the Grenadines"
								},
								{
									"attrs": {
										"value": "WS"
									},
									"tag": "option",
									"text": "Samoa"
								},
								{
									"attrs": {
										"value": "SM"
									},
									"tag": "option",
									"text": "San Marino"
								},
								{
									"attrs": {
										"value": "ST"
									},
									"tag": "option",
									"text": "Sao Tome and Principe"
								},
								{
									"attrs": {
										"value": "SA"
									},
									"tag": "option",
									"text": "Saudi Arabia"
								},
								{
									"attrs": {
										"value": "SN"
									},
									"tag": "option",
									"text": "Senegal"
								},
								{
									"attrs": {
										"value": "RS"
									},
									"tag": "option",
									"text": "Serbia"
								},
								{
									"attrs": {
										"value": "SC"
									},
									"tag": "option",
									"text": "Seychelles"
								},
								{
									"attrs": {
										"value": "SL"
									},
									"tag": "option",
									"text": "Sierra Leone"
								},
								{
									"attrs": {
										"value": "SG"
									},
									"tag": "option",
									"text": "Singapore"
								},
								{
									"attrs": {
										"value": "SX"
									},
									"tag": "option",
									"text": "Sint Maarten (Dutch part)"
								},
								{
									"attrs": {
										"value": "SK"
									},
									"tag": "option",
									"text": "Slovakia"
								},
								{
									"attrs": {
										"value": "SI"
									},
									"tag": "option",
									"text": "Slovenia"
								},
								{
									"attrs": {
										"value": "SB"
									},
									"tag": "option",
									"text": "Solomon Islands"
								},
								{
									"attrs": {
										"value": "SO"
									},
									"tag": "option",
									"text": "Somalia"
								},
								{
									"attrs": {
										"value": "ZA"
									},
									"tag": "option",
									"text": "South Africa"
								},
								{
									"attrs": {
										"value": "GS"
									},
									"tag": "option",
									"text": "South Georgia and the South Sandwich Islands"
								},
								{
									"attrs": {
										"value": "SS"
									},
									"tag": "option",
									"text": "South Sudan"
								},
								{
									"attrs": {
										"value": "ES"
									},
									"tag": "option",
									"text": "Spain"
								},
								{
									"attrs": {
										"value": "LK"
									},
									"tag": "option",
									"text": "Sri Lanka"
								},
								{
									"attrs": {
										"value": "SD"
									},
									"tag": "option",
									"text": "Sudan"
								},
								{
									"attrs": {
										"value": "SR"
									},
									"tag": "option",
									"text": "Suriname"
								},
								{
									"attrs": {
										"value": "SJ"
									},
									"tag": "option",
									"text": "Svalbard and Jan Mayen"
								},
								{
									"attrs": {
										"value": "SE"
									},
									"tag": "option",
									"text": "Sweden"
								},
								{
									"attrs": {
										"value": "CH"
									},
									"tag": "option",
									"text": "Switzerland"
								},
								{
									"attrs": {
										"value": "SY"
									},
									"tag": "option",
									"text": "Syrian Arab Republic"
								},
								{
									"attrs": {
										"value": "TW"
									},
									"tag": "option",
									"text": "Taiwan, Province of China"
								},
								{
									"attrs": {
										"value": "TJ"
									},
									"tag": "option",
									"text": "Tajikistan"
								},
								{
									"attrs": {
										"value": "TZ"
									},
									"tag": "option",
									"text": "Tanzania, United Republic of"
								},
								{
									"attrs": {
										"value": "TH"
									},
									"tag": "option",
									"text": "Thailand"
								},
								{
									"attrs": {
										"value": "TL"
									},
									"tag": "option",
									"text": "Timor-Leste"
								},
								{
									"attrs": {
										"value": "TG"
									},
									"tag": "option",
									"text": "Togo"
								},
								{
									"attrs": {
										"value": "TK"
									},
									"tag": "option",
									"text": "Tokelau"
								},
								{
									"attrs": {
										"value": "TO"
									},
									"tag": "option",
									"text": "Tonga"
								},
								{
									"attrs": {
										"value": "TT"
									},
									"tag": "option",
									"text": "Trinidad and Tobago"
								},
								{
									"attrs": {
										"value": "TN"
									},
									"tag": "option",
									"text": "Tunisia"
								},
								{
									"attrs": {
										"value": "TR"
									},
									"tag": "option",
									"text": "Turkey"
								},
								{
									"attrs": {
										"value": "TM"
									},
									"tag": "option",
									"text": "Turkmenistan"
								},
								{
									"attrs": {
										"value": "TC"
									},
									"tag": "option",
									"text": "Turks and Caicos Islands"
								},
								{
									"attrs": {
										"value": "TV"
									},
									"tag": "option",
									"text": "Tuvalu"
								},
								{
									"attrs": {
										"value": "UG"
									},
									"tag": "option",
									"text": "Uganda"
								},
								{
									"attrs": {
										"value": "UA"
									},
									"tag": "option",
									"text": "Ukraine"
								},
								{
									"attrs": {
										"value": "AE"
									},
									"tag": "option",
									"text": "United Arab Emirates"
								},
								{
									"attrs": {
										"value": "GB"
									},
									"tag": "option",
									"text": "United Kingdom"
								},
								{
									"attrs": {
										"value": "UM"
									},
									"tag": "option",
									"text": "United States Minor Outlying Islands"
								},
								{
									"attrs": {
										"value": "UY"
									},
									"tag": "option",
									"text": "Uruguay"
								},
								{
									"attrs": {
										"value": "UZ"
									},
									"tag": "option",
									"text": "Uzbekistan"
								},
								{
									"attrs": {
										"value": "VU"
									},
									"tag": "option",
									"text": "Vanuatu"
								},
								{
									"attrs": {
										"value": "VE"
									},
									"tag": "option",
									"text": "Venezuela, Bolivarian Republic of"
								},
								{
									"attrs": {
										"value": "VN"
									},
									"tag": "option",
									"text": "Viet Nam"
								},
								{
									"attrs": {
										"value": "VG"
									},
									"tag": "option",
									"text": "Virgin Islands, British"
								},
								{
									"attrs": {
										"value": "VI"
									},
									"tag": "option",
									"text": "Virgin Islands, U.S."
								},
								{
									"attrs": {
										"value": "WF"
									},
									"tag": "option",
									"text": "Wallis and Futuna"
								},
								{
									"attrs": {
										"value": "EH"
									},
									"tag": "option",
									"text": "Western Sahara"
								},
								{
									"attrs": {
										"value": "YE"
									},
									"tag": "option",
									"text": "Yemen"
								},
								{
									"attrs": {
										"value": "ZM"
									},
									"tag": "option",
									"text": "Zambia"
								},
								{
									"attrs": {
										"value": "ZW"
									},
									"tag": "option",
									"text": "Zimbabwe"
								},
								{
									"attrs": {
										"value": "AX"
									},
									"tag": "option",
									"text": "Åland Islands"
								}
							],
							"tag": "select"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_phone_number"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Phone number:"
						},
						{
							"attrs": {
								"id": "id_phone_number",
								"maxlength": "32",
								"name": "phone_number",
								"placeholder": "Phone Number",
								"type": "text",
								"value": "+13863448079"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		},
		{
			"classes": "error-container button-container",
			"elems": [
				{
					"attrs": {
						"id": "error_container"
					},
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"id": "errors"
							},
							"classes": "col-12 errors",
							"tag": "div"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"aria-label": "Continue",
								"hidden": "",
								"type": "submit"
							},
							"classes": "col-12",
							"tag": "button",
							"text": "Continue"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		}
	],
	"place_order": [
		{
			"classes": "form-container",
			"elems": [
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_create_new_account"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Create an account for faster checkout:"
						},
						{
							"attrs": {
								"id": "id_create_new_account",
								"name": "create_new_account",
								"type": "checkbox"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_remember_payment_info"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Remember my payment information:"
						},
						{
							"attrs": {
								"hidden": "",
								"id": "id_remember_payment_info",
								"name": "remember_payment_info",
								"type": "checkbox"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		},
		{
			"classes": "error-container button-container",
			"elems": [
				{
					"attrs": {
						"id": "error_container"
					},
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"id": "errors"
							},
							"classes": "col-12 errors",
							"tag": "div"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"aria-label": "Continue",
								"hidden": "",
								"type": "submit"
							},
							"classes": "col-12",
							"tag": "button",
							"text": "Continue"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		}
	],
	"shipping_address": [
		{
			"classes": "form-container",
			"elems": [
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_first_name"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "First name:"
						},
						{
							"attrs": {
								"id": "id_first_name",
								"maxlength": "255",
								"name": "first_name",
								"required": "",
								"type": "text"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_last_name"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Last name:"
						},
						{
							"attrs": {
								"id": "id_last_name",
								"maxlength": "255",
								"name": "last_name",
								"required": "",
								"type": "text"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_line1"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "First line of address:"
						},
						{
							"attrs": {
								"id": "id_line1",
								"maxlength": "255",
								"name": "line1",
								"required": "",
								"type": "text"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_line2"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Second line of address:"
						},
						{
							"attrs": {
								"id": "id_line2",
								"maxlength": "255",
								"name": "line2",
								"type": "text"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_line4"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "City:"
						},
						{
							"attrs": {
								"id": "id_line4",
								"maxlength": "255",
								"name": "line4",
								"required": "",
								"type": "text"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_state"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "State/County:"
						},
						{
							"attrs": {
								"id": "id_state",
								"maxlength": "255",
								"name": "state",
								"type": "text"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_postcode"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Post/Zip-code:"
						},
						{
							"attrs": {
								"id": "id_postcode",
								"maxlength": "64",
								"name": "postcode",
								"required": "",
								"type": "text"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_country"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Country:"
						},
						{
							"attrs": {
								"id": "id_country",
								"name": "country"
							},
							"elems": [
								{
									"attrs": {
										"value": "US"
									},
									"tag": "option",
									"text": "United States"
								},
								{
									"attrs": {
										"value": "CA"
									},
									"tag": "option",
									"text": "Canada"
								}
							],
							"tag": "select"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_phone_number"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Phone number:"
						},
						{
							"attrs": {
								"id": "id_phone_number",
								"maxlength": "128",
								"name": "phone_number",
								"type": "text"
							},
							"tag": "input"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		},
		{
			"classes": "error-container button-container",
			"elems": [
				{
					"attrs": {
						"id": "error_container"
					},
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"id": "errors"
							},
							"classes": "col-12 errors",
							"tag": "div"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"aria-label": "Continue",
								"hidden": "",
								"type": "submit"
							},
							"classes": "col-12",
							"tag": "button",
							"text": "Continue"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		}
	],
	"user_info": [
		{
			"classes": "form-container",
			"elems": [
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_username"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Email:"
						},
						{
							"attrs": {
								"id": "id_username",
								"maxlength": "150",
								"name": "username",
								"required": "",
								"type": "email"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_password"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Password:"
						},
						{
							"attrs": {
								"autocomplete": "current-password",
								"id": "id_password",
								"name": "password",
								"required": "",
								"type": "password"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-control row",
					"elems": [
						{
							"attrs": {
								"for": "id_options_0"
							},
							"classes": "floating-label",
							"tag": "label",
							"text": "Options:"
						},
						{
							"attrs": {
								"for": "id_options_0"
							},
							"classes": "floating-label",
							"elems": [
								{
									"attrs": {
										"checked": "",
										"id": "id_options_0",
										"name": "options",
										"required": "",
										"type": "radio",
										"value": "anonymous"
									},
									"classes": "required",
									"tag": "input",
									"text": ""
								}
							],
							"tag": "label",
							"text": "\n I am a new customer and want to checkout as a guest"
						},
						{
							"attrs": {
								"checked": "",
								"id": "id_options_0",
								"name": "options",
								"required": "",
								"type": "radio",
								"value": "anonymous"
							},
							"classes": "required",
							"tag": "input"
						},
						{
							"attrs": {
								"for": "id_options_1"
							},
							"classes": "floating-label",
							"elems": [
								{
									"attrs": {
										"id": "id_options_1",
										"name": "options",
										"required": "",
										"type": "radio",
										"value": "new"
									},
									"classes": "required",
									"tag": "input",
									"text": ""
								}
							],
							"tag": "label",
							"text": "\n I am a new customer and want to create an account before checking out"
						},
						{
							"attrs": {
								"id": "id_options_1",
								"name": "options",
								"required": "",
								"type": "radio",
								"value": "new"
							},
							"classes": "required",
							"tag": "input"
						},
						{
							"attrs": {
								"for": "id_options_2"
							},
							"classes": "floating-label",
							"elems": [
								{
									"attrs": {
										"id": "id_options_2",
										"name": "options",
										"required": "",
										"type": "radio",
										"value": "existing"
									},
									"classes": "required",
									"tag": "input",
									"text": ""
								}
							],
							"tag": "label",
							"text": "\n I am a returning customer, and my password is"
						},
						{
							"attrs": {
								"id": "id_options_2",
								"name": "options",
								"required": "",
								"type": "radio",
								"value": "existing"
							},
							"classes": "required",
							"tag": "input"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		},
		{
			"classes": "error-container button-container",
			"elems": [
				{
					"attrs": {
						"id": "error_container"
					},
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"id": "errors"
							},
							"classes": "col-12 errors",
							"tag": "div"
						}
					],
					"tag": "div"
				},
				{
					"classes": "form-group row",
					"elems": [
						{
							"attrs": {
								"aria-label": "Continue",
								"hidden": "",
								"type": "submit"
							},
							"classes": "col-12",
							"tag": "button",
							"text": "Continue"
						}
					],
					"tag": "div"
				}
			],
			"tag": "div"
		}
	]
}