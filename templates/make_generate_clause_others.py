import random
import json
from typing import Dict, List, Any, Optional

# Template definitions
TEMPLATES = {
    "on_board_date": {
        "clause_candidate": [
            "ON BOARD DATE:", "ON BOARD NOT LATER THAN", "SHIPMENT DATE:",
            "DATE OF SHIPMENT:", "SHIPPED ON OR BEFORE", "LATEST SHIPMENT DATE:"
        ],
        "clause_candidate_weights": [0.2, 0.2, 0.2, 0.15, 0.15, 0.1],
        "value_candidate": {
            "real_name": [
                "2021-10-25", "2021-11-02", "2021-11-08", "2021-11-15", "2021-11-22",
                "2021-11-29", "2021-12-06", "2021-12-13", "2021-12-20", "2021-12-27",
                "2022-01-03", "2022-01-10", "2022-01-17", "2022-01-24", "2022-01-31",
                "2023-01-02", "2023-01-09", "2023-01-16", "2023-01-23", "2023-01-30",
                "2023-02-06", "2023-02-13", "2023-02-20", "2023-02-27", "2023-03-06",
                "2025-04-07", "2025-04-14", "2025-04-21", "2025-04-28", "2025-05-05"
            ]
        },
        "value_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} {value_1}",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "on_board_date",
                        "expected_value": "value_1",
                        "operator": "LTE"
                    }
                ]
            },
            {
                "clause_template": [
                    "INDICATING ON BOARD DATE",
                    "SHOWING SHIPMENT DATE",
                    "IT MUST SHOW AN ON BOARD NOTATION INDICATING THE DATE"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "on_board_date",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    }
                ]
            }
        ]
    },
    "freight_terms": {
        "clause_candidate": ["MARKED", "BE MARKED", "SHOWING", "INDICATING", "STATING"],
        "clause_candidate_weights": [0.3, 0.1, 0.3, 0.2, 0.1],
        "value_candidate": {
            "real_name": [
                "FREIGHT PREPAID", "FREIGHT COLLECT", "FREIGHT TO COLLECT",
                "FREIGHT AS ARRANGED", "FREIGHT PAYABLE AS PER CHARTER PARTY",
                "FREIGHT PRE-PAID"
            ]
        },
        "combinator_candidate": ["OR", "AND/OR", "/"],
        "combinator_candidate_weights": [0.4, 0.2, 0.4],
        "value_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} {value_1}",
                    "{clause_candidate} `{value_1}`",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "freight_terms",
                        "expected_value": "value_1",
                        "operator": "CONTAINS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {combinator_candidate} {value_2}"
                ],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "freight_terms",
                                "expected_value": "value_1",
                                "operator": "CONTAINS"
                            },
                            {
                                "doc": "BL",
                                "key": "freight_terms",
                                "expected_value": "value_2",
                                "operator": "CONTAINS"
                            },
                        ]
                    }
                 ]
            }
        ]   
    },
    "port_of_discharge": {
        "clause_candidate": ["FOR SHIPMENT TO", "FOR SHIP TO", "DISCHARGE AT:", "DISCHARGE PORT:"],
        "clause_candidate_weights": [0.3, 0.1, 0.3, 0.3],
        "value_candidate": {
            "real_name": [
                "HONG KONG", "INCHEON", "BUSAN", "SHANGHAI", "SINGAPORE",
                "ROTTERDAM", "HAMBURG", "LOS ANGELES", "LONG BEACH", "SEATTLE",
                "NEW YORK", "SAVANNAH", "OAKLAND", "TOKYO", "YOKOHAMA"
            ]
        },
        "value_candidate_weights": [1.0],
        "combinator_candidate": ["OR", "AND/OR", "/"],
        "combinator_candidate_weights": [0.5, 0.2, 0.3],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} {value_1}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "port_of_discharge",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} {value_1}, {value_2} AND {value_3}",
                    "{clause_candidate} {value_1}, {value_2}, {value_3}"
                ],
                "clause_template_weights": [0.7, 0.3],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "port_of_discharge",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "port_of_discharge",
                        "expected_value": "value_2",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "port_of_discharge",
                        "expected_value": "value_3",
                        "operator": "EQUALS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {combinator_candidate} {value_2} {combinator_candidate} {value_3}"
                ],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "port_of_discharge",
                                "expected_value": "value_1",
                                "operator": "EQUALS"
                            },
                            {
                                "doc": "BL",
                                "key": "port_of_discharge",
                                "expected_value": "value_2",
                                "operator": "EQUALS"
                            },
                            {
                                "doc": "BL",
                                "key": "port_of_discharge",
                                "expected_value": "value_3",
                                "operator": "EQUALS"
                            }
                        ]
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {combinator_candidate} {value_2}"
                ],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "port_of_discharge",
                                "expected_value": "value_1",
                                "operator": "EQUALS"
                            },
                            {
                                "doc": "BL",
                                "key": "port_of_discharge",
                                "expected_value": "value_2",
                                "operator": "EQUALS"
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "clean_on_board": {
        "clause_candidate": [],
        "value_candidate": {},
        "templates": [
            {
                "clause_template": [
                    "CLEAN ON BOARD", "CLEAN SHIPPED ON BOARD"
                ],
                "clause_template_weights": [0.5, 0.5],
                "make_json": [
                    {
                        "combinator": "OR",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "adverse_remarks",
                                "expected_value": "null",
                                "operator": "NEGATION"
                            },
                            {
                                "doc": "BL",
                                "key": "clean_wording",
                                "expected_value": "true",
                                "operator": "EXISTS"
                            }
                        ]
                    },
                    {
                        "combinator": "OR",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "on_board_notation",
                                "expected_value": "true",
                                "operator": "EXISTS"
                            },
                            {
                                "doc": "BL",
                                "key": "pre_printed_shipment_wording",
                                "expected_value": "true",
                                "operator": "EXISTS"
                            }
                        ]
                    }
                ]
            },
            {
                "clause_template": [
                    "ON BOARD", "SHIPPED ON BOARD"
                ],
                "clause_template_weights": [0.5, 0.5],
                "make_json": [
                    {
                        "combinator": "OR",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "on_board_notation",
                                "expected_value": "true",
                                "operator": "EXISTS"
                            },
                            {
                                "doc": "BL",
                                "key": "pre_printed_shipment_wording",
                                "expected_value": "true",
                                "operator": "EXISTS"
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "shipper": {
        "clause_candidate": ["SHIPPED BY", "CONSIGNOR:", "SHOWING SHIPPER AS"],
        "clause_candidate_weights": [0.4, 0.3, 0.3],
        "value_candidate": {
            "real_name": [
                "ABC TRADING CORPORATION", "BCD TECHNOLOGY CORPORATION", "EFG GROUP LIMITED",
                "HIJ CORPORATION", "QWE CORPORATION", "ASD CORPORATION",
                "ZXC INC.", "WER CORPORATION", "TYU CORPORATION", "AZQ CORPORATION"
            ]
        },
        "value_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "EVIDENCING NAME AND ADDRESS OF BENEFICIARY AS SHIPPER",
                    "ISSUED IN THE NAME OF BENEFICIARY AS SHIPPER"
                ],
                "clause_template_weights": [0.3, 0.3, 0.2, 0.2],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "shipper",
                        "expected_value": "$LC_BENEFICIARY",
                        "operator": "EQUALS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} {value_1}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "shipper",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    }
                ]
            }
        ]
    },
    "goods_description": {
        "clause_candidate": ["COVERING", "SHOWING", "INDICATING", "COVERING SHIPMENT OF:"],
        "clause_candidate_weights": [0.3, 0.3, 0.2, 0.2],
        "value_candidate": {
            "real_name": [
                "PACKAGING MATERIALS", "POLYETHYLENE", "POLYPROPYLENE", "ACRYLIC",
                "VINYL CHLORIDE RESIN", "SYNTHETIC RESIN", "ORGANIC COMPOUNDS", "CHEMICAL PRODUCTS",
                "PLASTIC RAW MATERIALS", "POLYMER COMPOUNDS",
                "STEEL COILS", "COTTON YARN", "ELECTRONIC COMPONENTS", "AUTO PARTS",
                "MACHINERY PARTS", "FROZEN SEAFOOD", "PAPER PRODUCTS"
            ]
        },
        "value_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "SHOWING DESCRIPTION OF GOODS",
                    "MARKED DESCRIPTION OF GOODS",
                    "EVIDENCING SHIPMENT OF MERCHANDISE DESCRIBED IN FIELD 45A",
                    "EVIDENCING SHIPMENT OF GOODS DESCRIBED IN FIELD 45A",
                    "EVIDENCING SHIPMENT OF GOODS DESCRIBED ABOVE",
                    "SHOWING GOODS"
                ],
                "clause_template_weights": [0.2, 0.2, 0.2, 0.2, 0.1, 0.1],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "goods_description",
                        "expected_value": "$LC_45A",
                        "operator": "CONTAINS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} {value_1}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "goods_description",
                        "expected_value": "value_1",
                        "operator": "CONTAINS"
                    }
                ]
            }
        ]
    },
    "hs_code": {
        "clause_candidate": ["MARKED", "INDICATING", "STATING"],
        "clause_candidate_weights": [0.4, 0.3, 0.3],
        "value_candidate": {
            "real_name": [
                "12345678", "52369853", "12378945", "96385274",
                "123456", "745236", "794562", "235623"
            ]
        },
        "value_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} H.S. CODE: NO.{value_1}",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "hs_code",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} H.S. CODE",
                    "{clause_candidate} H.S CODE",
                    "{clause_candidate} HARMONIZED SYSTEM CODE",
                    "MENTION THE H.S. CODE"
                ],
                "clause_template_weights": [0.3, 0.2, 0.2, 0.1],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "hs_code",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    }
                ]
            }
        ]
    },
    "lc_number": {
        "clause_candidate": ["MARKED", "INDICATING", "STATING", "SHOWING", "BEARING", "QUOTING"],
        "clause_candidate_weights": [0.2, 0.2, 0.2, 0.2, 0.1, 0.1],
        "value_candidate": {
            "real_name": [
                "LC2024-001234", "LC2024-567890", "LC2023-987654", "LC2023-456123",
                "L/C2024-111222", "L/C2024-333444", "DC2024-555666", "DC2023-777888",
                "2024LC001234", "2024LC567890", "24LC-001234", "24LC-567890"
            ]
        },
        "value_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} LC NUMBER: {value_1}",
                    "COVERING L/C NUMBER: {value_1}",
                    "COVERING LC NO.{value_1}"
                ],
                "clause_template_weights": [0.5, 0.3, 0.2],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "lc_number",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} L/C NUMBER",
                    "{clause_candidate} THIS DC NUMBER",
                    "{clause_candidate} OUR L/C NO.",
                    "L/C NUMBER IS TO BE INDICATED"
                ],
                "clause_template_weights": [0.3, 0.2, 0.2, 0.3],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "lc_number",
                        "expected_value": "$LC_NUMBER",
                        "operator": "EQUALS"
                    }
                ]
            }
        ],
        "templates_weights": [0.3, 0.7]
    },
    "contract_number": {
        "clause_candidate": ["MARKED", "INDICATING", "STATING", "SHOWING", "BEARING", "QUOTING", "AS PER"],
        "clause_candidate_weights": [0.2, 0.2, 0.15, 0.15, 0.1, 0.1, 0.1],
        "value_candidate": {
            "real_name": [
                "CTR2024-001234", "CTR2024-567890", "SALES-2024-001", "SALES-2023-456",
                "PO-2024-789012", "CONTRACT-24-003", "S/C2024-111222", "P/I2024-333444",
                "2024-CONTRACT-001", "24CTR-567890"
            ]
        },
        "value_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} CONTRACT NUMBER: {value_1}",
                    "CONTRACT NUMBER: {value_1}"
                ],
                "clause_template_weights": [0.8, 0.2],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "contract_number",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    }
                ]
            },
            {
                "clause_template": [
                    "{clause_candidate} CONTRACT NUMBER",
                    "CONTRACT NUMBER IS TO BE INDICATED"
                ],
                "clause_template_weights": [0.7, 0.3],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "contract_number",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    }
                ]
            }
        ]
    },
    "charter_party": {
        "clause_candidate": [],
        "value_candidate": {},
        "templates": [
            {
                "clause_template": [
                    "FREE FROM CHARTER PARTY",
                    "CHARTER PARTY NOT APPLICABLE",
                    "INDEPENDENT OF CHARTER PARTY",
                    "NOT UNDER CHARTER PARTY TERMS",
                ],
                "clause_template_weights": [0.2, 0.2, 0.2, 0.15, 0.15, 0.1],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "charter_party",
                        "expected_value": "null",
                        "operator": "NEGATION"
                    }
                ]
            }
        ]
    },
    "surrendered": {
        "clause_candidate": [],
        "value_candidate": {},
        "templates": [
            {
                "clause_template": [
                    "SURRENDERED B/L",
                    "SURRENDERED B/L ACCEPTABLE"
                ],
                "clause_template_weights": [0.4, 0.6],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "surrendered",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    }
                ]
            }
        ]
    },
    "signed/stamped": {
        "clause_candidate": [],
        "value_candidate": {},
        "templates": [
            {
                "clause_template": [
                    "MANUALLY SIGNED"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "signed/stamped",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    }
                ]
            }
        ]
    },
    "number_of_originals": {
        "clause_candidate": ["FULL SET"],
        "clause_candidate_weights": [1.0],
        "value_candidate": {
            "real_name": ["1", "2", "3"]
        },
        "value_candidate_weights": [0.3, 0.3, 0.4],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} BILL OF LADING",
                    "{clause_candidate} OF ORIGINAL BILL OF LADING",
                ],
                "clause_template_weights": [0.5, 0.5],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "number_of_originals",
                        "expected_value": "3",
                        "operator": "GTE"
                    }
                ]
            },
            {
                "clause_template": [
                    "{value_1}/3 ORIGINAL BILL OF LADING"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "number_of_originals",
                        "expected_value": "value_1",
                        "operator": "GTE"
                    }
                ]
            }
        ]
    },
    "number_of_copies": {
        "clause_candidate": ["COPY", "COPIES", "NON-NEGOTIABLE COPY", "NON-NEGOTIABLE COPIES"],
        "clause_candidate_weights": [0.2, 0.3, 0.2, 0.3],
        "value_candidate": {
            "real_name": ["1", "2", "3", "4", "5"]
        },
        "value_candidate_weights": [0.3, 0.4, 0.3],
        "templates": [
            {
                "clause_template": [
                    "PLUS {value_1} {clause_candidate}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "number_of_copies",
                        "expected_value": "value_1",
                        "operator": "GTE"
                    }
                ]
            }
        ]
    },
    "issuer": {
        "clause_candidate": ["ISSUED BY", "AS AGENT FOR CARRIER:", "AS CARRIER:"],
        "clause_candidate_weights": [0.3, 0.3, 0.2],
        "value_candidate": {
            "real_name": [
                "ABC TRADING CORPORATION", "BCD TECHNOLOGY CORPORATION", "EFG GROUP LIMITED",
                "HIJ CORPORATION", "QWE CORPORATION", "ASD CORPORATION",
                "ZXC INC.", "WER CORPORATION", "TYU CORPORATION", "AZQ CORPORATION"
            ]
        },
        "value_candidate_weights": [1.0],
        "detail_candidate": {
            "real_name": ["VIETNAM", "KOREA", "SINGAPORE", "USA", "JAPAN", "TAIWAN", "CHINA", "INDIA"]
        },
        "detail_candidate_weights": [1.0],
        "templates": [
            {
                "clause_template": [
                    "{clause_candidate} {value_1}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "issuer",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    }
                ]
            },
            {
                "clause_template": [
                    "NAME AND ADDRESS OF THE CARRIER'S AGENT IN {detail_value_1}",
                    "B/L MUST SHOW NAME, ADDRESS, TEL/FAX NO. OF SHIPPING AGENT IN {detail_value_1}"
                ],
                "clause_template_weights": [0.5, 0.5],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "issuer",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    },
                    {
                        "doc": "BL",
                        "key": "issuer_details",
                        "expected_value": "detail_value_1",
                        "operator": "CONTAINS"
                    }
                ]
            },
            {
                "clause_template": [
                    "B/L MUST SHOW NAME AND ADDRESS OF CARRYING VESSEL'S AGENT AT PORT OF DESTINATION"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "issuer",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    },
                    {
                        "doc": "BL",
                        "key": "issuer_details",
                        "expected_value": "true",
                        "operator": "EXISTS"
                    }
                ]
            }
        ]
    }
}


def select_from_candidate(candidate: Any) -> Any:
    """Pick a random element from a list; return anything else as-is."""
    if isinstance(candidate, list):
        return random.choice(candidate)
    return candidate


def generate_clause_and_gtjson(key: str, template_idx: int = None) -> Dict[str, Any]:
    """
    Generate a clause and its gt_json from a template.
    
    Args:
        key: category to generate (e.g. "on_board_date", "freight_terms")
        template_idx: index of the template to use; picked at random if None.
    
    Returns:
        {"clause": str, "gt_json": List[Dict], "key": str, "template_idx": int}
    """
    if key not in TEMPLATES:
        raise ValueError(f"Unknown key: {key}")
    
    config = TEMPLATES[key]
    
    if template_idx is None:
        template_idx = random.randint(0, len(config["templates"]) - 1)
    
    template = config["templates"][template_idx]
    
    clause_candidate = ""
    if config.get("clause_candidate"):
        clause_candidate = random.choices(
            config["clause_candidate"],
            weights=config.get("clause_candidate_weights"),
            k=1
        )[0]
    
    combinator_candidate = ""
    if config.get("combinator_candidate"):
        combinator_candidate = random.choices(
            config["combinator_candidate"],
            weights=config.get("combinator_candidate_weights"),
            k=1
        )[0]
    
    value_candidate = config.get("value_candidate", {})
    detail_candidate = config.get("detail_candidate", {})
    
    selected_values = {}
    
    # value_1..value_3 are distinct when the candidate list allows it
    value_keys = list(value_candidate.keys())
    if value_keys and value_candidate.get(value_keys[0]):
        selected_key_1 = value_keys[0]
        selected_values["value_1"] = select_from_candidate(value_candidate[selected_key_1])
        selected_values["value_1_key"] = selected_key_1
        # gt_json gets the real value for real_name and the key name for $LC_*
        if selected_key_1 == "real_name":
            selected_values["value_1_expected"] = selected_values["value_1"]
        else:
            selected_values["value_1_expected"] = selected_key_1
        
        if len(value_candidate[selected_key_1]) > 1:
            available_values = [v for v in value_candidate[selected_key_1] if v != selected_values["value_1"]]
            if available_values:
                selected_values["value_2"] = random.choice(available_values)
            else:
                selected_values["value_2"] = selected_values["value_1"]
        else:
            selected_values["value_2"] = selected_values["value_1"]
        selected_values["value_2_key"] = selected_key_1
        if selected_key_1 == "real_name":
            selected_values["value_2_expected"] = selected_values["value_2"]
        else:
            selected_values["value_2_expected"] = selected_key_1
        
        if len(value_candidate[selected_key_1]) > 2:
            available_values = [v for v in value_candidate[selected_key_1] if v not in [selected_values["value_1"], selected_values["value_2"]]]
            if available_values:
                selected_values["value_3"] = random.choice(available_values)
            else:
                selected_values["value_3"] = selected_values["value_1"]
        else:
            selected_values["value_3"] = selected_values["value_1"]
        selected_values["value_3_key"] = selected_key_1
        if selected_key_1 == "real_name":
            selected_values["value_3_expected"] = selected_values["value_3"]
        else:
            selected_values["value_3_expected"] = selected_key_1
    
    detail_keys = list(detail_candidate.keys()) if detail_candidate else []
    if detail_keys and detail_candidate.get(detail_keys[0]):
        selected_values["detail_value_1"] = select_from_candidate(detail_candidate[detail_keys[0]])
        selected_values["detail_value_1_key"] = detail_keys[0]
        if detail_keys[0] == "real_name":
            selected_values["detail_value_1_expected"] = selected_values["detail_value_1"]
        else:
            selected_values["detail_value_1_expected"] = detail_keys[0]
    
    if "clause_template_weights" in template and len(template.get("clause_template_weights", [])) == len(template["clause_template"]):
        clause_template = random.choices(
            template["clause_template"],
            weights=template["clause_template_weights"],
            k=1
        )[0]
    else:
        clause_template = select_from_candidate(template["clause_template"])
    
    clause = clause_template.format(
        clause_candidate=clause_candidate,
        combinator_candidate=combinator_candidate,
        value_1=selected_values.get("value_1", ""),
        value_2=selected_values.get("value_2", ""),
        value_3=selected_values.get("value_3", ""),
        detail_value_1=selected_values.get("detail_value_1", "")
    )
    
    gt_json = []
    for item in template["make_json"]:
        gt_item = process_make_json_item(item, selected_values, combinator_candidate)
        gt_json.append(gt_item)
    
    return {
        "clause": clause,
        "gt_json": gt_json,
        "key": key,
        "template_idx": template_idx
    }


def process_make_json_item(item: Dict, selected_values: Dict, combinator_candidate: str,
                           parent_key: str = None) -> Dict:
    """
    Convert a make_json item to a gt_json item.
    
    Args:
        item: make_json item to convert
        selected_values: values chosen for this clause
        combinator_candidate: chosen combinator ("/" is written as "OR")
        parent_key: key of the parent node, inherited by nested conditions
    """
    result = {}
    
    # Nested conditions inherit the parent key
    current_key = item.get("key", parent_key)
    
    for key, value in item.items():
        if key == "combinator":
            if value == "combinator_candidate":
                result[key] = "OR" if combinator_candidate == "/" else combinator_candidate
            else:
                result[key] = value
        elif key == "expected_value":
            if value == "value_1":
                result[key] = selected_values.get("value_1_expected", value)
            elif value == "value_2":
                result[key] = selected_values.get("value_2_expected", value)
            elif value == "value_3":
                result[key] = selected_values.get("value_3_expected", value)
            elif value == "detail_value_1":
                result[key] = selected_values.get("detail_value_1_expected", value)
            elif value == "true":
                result[key] = True
            elif value == "null":
                result[key] = None
            else:
                result[key] = value
            
            # Counts are stored as ints
            if current_key in ("number_of_originals", "number_of_copies"):
                if isinstance(result.get("expected_value"), str):
                    try:
                        result["expected_value"] = int(result["expected_value"])
                    except (ValueError, TypeError):
                        pass  # leave non-numeric values as-is
        elif key == "conditions":
            if isinstance(value, list):
                result[key] = [process_make_json_item(cond, selected_values, combinator_candidate, current_key) for cond in value]
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result


def generate_all_keys(num_samples: int = 1) -> Dict[str, List[Dict]]:
    """
    Generate clauses and gt_json for every key.
    
    Args:
        num_samples: number of samples per key
    
    Returns:
        {key: [{"clause": str, "gt_json": List[Dict]}, ...]}
    """
    results = {}
    for key in TEMPLATES.keys():
        results[key] = []
        for _ in range(num_samples):
            result = generate_clause_and_gtjson(key)
            results[key].append(result)
    return results


if __name__ == "__main__":
    # Example: generate one sample per template for every key
    print("=" * 80)
    print("Template-based clause and GT_JSON examples (others)")
    print("=" * 80)
    
    for key in TEMPLATES.keys():
        print(f"\n{'='*60}")
        print(f"Key: {key}")
        print(f"{'='*60}")
        
        config = TEMPLATES[key]
        for i in range(len(config["templates"])):
            result = generate_clause_and_gtjson(key, template_idx=i)
            print(f"\n--- Template {i} ---")
            print(f"Clause: {result['clause']}")
            print(f"GT_JSON: {json.dumps(result['gt_json'], indent=2)}")