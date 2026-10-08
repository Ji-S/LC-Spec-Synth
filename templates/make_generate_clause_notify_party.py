import random
import json
from typing import Dict, List, Any, Optional

# Template definitions
TEMPLATES = {
    "notify_party": {
        "clause_candidate": ["NOTIFY", "MARKED NOTIFY"],
        "clause_candidate_weights": [0.4, 0.15],
        "value_candidate": {
            "$LC_ISSUING_BANK": ["ISSUING BANK"],
            "$LC_APPLICANT": ["APPLICANT"],
            "real_name": ["ABC CORPORATION", "XYZ TRADING CO."]
        },
        "value_candidate_weights": [0.1, 0.7, 0.2],
        "value_internal_weights": {
            "$LC_ISSUING_BANK": [1.0],
            "$LC_APPLICANT": [1.0]
        },
        "detail_candidate": {
            "$LC_APPLICANT_DETAILS": ["WITH FULL NAME AND ADDRESS", "WITH FULL ADDRESS"],
            "$LC_ISSUING_BANK_DETAILS": ["WITH FULL NAME AND ADDRESS", "WITH FULL ADDRESS"],
            "real_name": ["SEOUL, KOREA", "NEW YORK, USA"]
        },
        "detail_candidate_weights": {
            "$LC_APPLICANT_DETAILS": [0.5, 0.5],
            "$LC_ISSUING_BANK_DETAILS": [0.5, 0.5]
            # real_name values are loaded from dummy.json, so they have no weights
        },
        "combinator_candidate": ["OR", "AND/OR", "/"],
        "combinator_candidate_weights": [0.4, 0.2, 0.4],
        "templates": [
            # Template 0: notify 1, notify_details 0
            {
                "clause_template": [
                    "{clause_candidate} {value_1}",
                    "SHOWING {value_1} AS NOTIFY PARTY",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 1: notify 1, notify_details 0 (SAME AS CONSIGNEE)
            {
                "clause_template": [
                    "NOTIFY SAME AS CONSIGNEE"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "SAME AS CONSIGNEE",
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 2: notify 1, notify_details 1
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {detail_value_1}",
                    "SHOWING {value_1} {detail_value_1} AS NOTIFY PARTY",
                    "SHOWING {value_1} AS NOTIFY PARTY {detail_value_1}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party_details",
                        "expected_value": "detail_value_1",
                        "operator": "CONTAINS"
                    }
                ]
            },
            # Template 3: notify 2, notify_details 1
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {detail_value_1}, {value_2}",
                    "{clause_candidate} {value_1} {detail_value_1} AND {value_2}",
                    "{clause_candidate} {value_1} {detail_value_1} AND ALSO NOTIFY {value_2}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party_details",
                        "expected_value": "detail_value_1",
                        "operator": "CONTAINS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_2",
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 4: notify 2, notify_details 1
            {
                "clause_template": [
                    "{clause_candidate} {value_1}, {value_2} {detail_value_2}",
                    "{clause_candidate} {value_1} AND {value_2} {detail_value_2}",
                    "{clause_candidate} {value_1} AND ALSO NOTIFY {value_2} {detail_value_2}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_2",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party_details",
                        "expected_value": "detail_value_2",
                        "operator": "CONTAINS"
                    }
                ]
            },
            # Template 5: notify 2, notify_details 2
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {detail_value_1}, {value_2} {detail_value_2}",
                    "{clause_candidate} {value_1} {detail_value_1} AND {value_2} {detail_value_2}",
                    "{clause_candidate} {value_1} {detail_value_1} AND ALSO NOTIFY {value_2} {detail_value_2}"
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_1",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party_details",
                        "expected_value": "detail_value_1",
                        "operator": "CONTAINS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party",
                        "expected_value": "value_2",
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "notify_party_details",
                        "expected_value": "detail_value_2",
                        "operator": "CONTAINS"
                    }
                ]
            },
            # Template 6: notify 2, notify_details 1, combinator
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {combinator_candidate} {value_2} {detail_value_2}",
                ],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "notify_party",
                                "expected_value": "value_1",
                                "operator": "EQUALS"
                            },
                            {
                                "combinator": "AND",
                                "conditions": [
                                    {
                                        "doc": "BL",
                                        "key": "notify_party",
                                        "expected_value": "value_2",
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "notify_party_details",
                                        "expected_value": "detail_value_2",
                                        "operator": "CONTAINS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            # Template 7: notify 2, notify_details 1, combinator
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {detail_value_1} {combinator_candidate} {value_2}",
                ],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "combinator": "AND",
                                "conditions": [
                                    {
                                        "doc": "BL",
                                        "key": "notify_party",
                                        "expected_value": "value_1",
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "notify_party_details",
                                        "expected_value": "detail_value_1",
                                        "operator": "CONTAINS"
                                    }
                                ]
                            },
                            {
                                "doc": "BL",
                                "key": "notify_party",
                                "expected_value": "value_2",
                                "operator": "EQUALS"
                            },
                        ]
                    }
                ]
            },
            # Template 8: notify 2, notify_details 2, combinator
            {
                "clause_template": [
                    "{clause_candidate} {value_1} {detail_value_1} {combinator_candidate} {value_2} {detail_value_2}",
                ],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "combinator": "AND",
                                "conditions": [
                                    {
                                        "doc": "BL",
                                        "key": "notify_party",
                                        "expected_value": "value_1",
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "notify_party_details",
                                        "expected_value": "detail_value_1",
                                        "operator": "CONTAINS"
                                    }
                                ]
                            },
                            {
                                "combinator": "AND",
                                "conditions": [
                                    {
                                        "doc": "BL",
                                        "key": "notify_party",
                                        "expected_value": "value_2",
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "notify_party_details",
                                        "expected_value": "detail_value_2",
                                        "operator": "CONTAINS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            # Template 9: notify 3, OR
            {
                "clause_template": [
                    "{clause_candidate} {value_1} OR {value_2} OR {value_3}",
                ],
                "make_json": [
                    {
                        "combinator": "OR",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "notify_party",
                                "expected_value": "value_1",
                                "operator": "EQUALS"
                            },
                            {
                                "doc": "BL",
                                "key": "notify_party",
                                "expected_value": "value_2",
                                "operator": "EQUALS"
                            },
                            {
                                "doc": "BL",
                                "key": "notify_party",
                                "expected_value": "value_3",
                                "operator": "EQUALS"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

# Extracted B/L data that fills the real_name candidates (see README)
import os
DEFAULT_BL_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'extracted_bl', 'dummy.json')


def load_bl_data(path: str = DEFAULT_BL_DATA_PATH) -> None:
    """Fill the notify_party real_name candidates from an extracted B/L data file."""
    with open(path, 'r', encoding='utf-8') as f:
        bl_data = json.load(f)
    
    names = bl_data['notify_party']['split_extracted_bl']
    # A clause can name up to 3 distinct notify parties
    if len(set(names)) < 3:
        raise ValueError(f"{path} needs at least 3 distinct notify_party names")
    
    TEMPLATES['notify_party']['value_candidate']['real_name'] = names
    TEMPLATES['notify_party']['detail_candidate']['real_name'] = bl_data['notify_party_details']['split_extracted_bl']


# Default data, so the module also works on its own; load_bl_data(path) overrides it
if os.path.exists(DEFAULT_BL_DATA_PATH):
    load_bl_data()


def select_from_candidate(candidate: Any) -> Any:
    """Pick a random element from a list; return anything else as-is."""
    if isinstance(candidate, list):
        return random.choice(candidate)
    return candidate


def get_value_for_key(key: str, value_candidate: Dict, detail_candidate: Dict) -> str:
    """Pick a value for key from value_candidate, then detail_candidate; otherwise return key itself."""
    if key in value_candidate:
        return select_from_candidate(value_candidate[key])
    elif key in detail_candidate:
        return select_from_candidate(detail_candidate[key])
    else:
        # key is itself the value (e.g. "BLANK")
        return key


def get_detail_for_key(key: str, detail_candidate: Dict) -> str:
    """Pick a value for key from detail_candidate; otherwise return key itself."""
    if key in detail_candidate:
        return select_from_candidate(detail_candidate[key])
    return key


def select_detail_key_for_value(selected_key: str, detail_candidate: Dict) -> str:
    """
    Choose the detail key that goes with a value key.
    - real_name: always real_name
    - $LC_ISSUING_BANK: $LC_ISSUING_BANK_DETAILS (55%) or real_name (45%)
    - $LC_APPLICANT: $LC_APPLICANT_DETAILS (55%) or real_name (45%)
    """
    if selected_key == "real_name":
        return "real_name"
    elif selected_key == "$LC_ISSUING_BANK":
        if random.random() < 0.55:
            return "$LC_ISSUING_BANK_DETAILS"
        else:
            return "real_name"
    elif selected_key == "$LC_APPLICANT":
        if random.random() < 0.55:
            return "$LC_APPLICANT_DETAILS"
        else:
            return "real_name"
    else:
        return "real_name"


def generate_clause_and_gtjson(template_idx: int = None) -> Dict[str, Any]:
    """
    Generate a clause and its gt_json from a template.
    
    Args:
        template_idx: index of the template to use; picked at random if None.
    
    Returns:
        {"clause": str, "gt_json": List[Dict], "template_idx": int}
    """
    notify_config = TEMPLATES["notify_party"]
    
    if template_idx is None:
        template_idx = random.randint(0, len(notify_config["templates"]) - 1)
    
    template = notify_config["templates"][template_idx]
    
    clause_candidate = random.choices(
        notify_config["clause_candidate"],
        weights=notify_config["clause_candidate_weights"],
        k=1
    )[0]
    combinator_candidate = random.choices(
        notify_config["combinator_candidate"],
        weights=notify_config["combinator_candidate_weights"],
        k=1
    )[0]
    
    value_candidate = notify_config["value_candidate"]
    detail_candidate = notify_config["detail_candidate"]
    
    selected_values = {}
    
    # value_1: pick a key ($LC_* or real_name) by weight, then a value within it
    # gt_json gets the real value for real_name and the key name for $LC_*
    value_keys = list(value_candidate.keys())
    selected_key_1 = random.choices(
        value_keys,
        weights=notify_config["value_candidate_weights"],
        k=1
    )[0]
    value_items = value_candidate[selected_key_1]
    if selected_key_1 in notify_config["value_internal_weights"]:
        selected_values["value_1"] = random.choices(
            value_items,
            weights=notify_config["value_internal_weights"][selected_key_1],
            k=1
        )[0]
    else:
        selected_values["value_1"] = select_from_candidate(value_items)
    selected_values["value_1_key"] = selected_key_1
    
    if selected_key_1 == "real_name":
        selected_values["value_1_expected"] = selected_values["value_1"]
    else:
        selected_values["value_1_expected"] = selected_key_1
    
    # The detail key depends on the value key
    detail_key_1 = select_detail_key_for_value(selected_key_1, detail_candidate)
    selected_values["detail_value_1_key_for_value_1"] = detail_key_1
    
    # value_2: avoid repeating the same $LC_* key (real_name may repeat)
    if selected_key_1 in ["$LC_ISSUING_BANK", "$LC_APPLICANT"]:
        available_keys_for_v2 = [k for k in value_keys if k != selected_key_1]
        available_weights_for_v2 = [
            notify_config["value_candidate_weights"][value_keys.index(k)]
            for k in available_keys_for_v2
        ]
        total_weight = sum(available_weights_for_v2)
        available_weights_for_v2 = [w / total_weight for w in available_weights_for_v2]
        selected_key_2 = random.choices(
            available_keys_for_v2,
            weights=available_weights_for_v2,
            k=1
        )[0]
    else:
        selected_key_2 = random.choices(
            value_keys,
            weights=notify_config["value_candidate_weights"],
            k=1
        )[0]
    
    value_items = value_candidate[selected_key_2]
    if selected_key_2 in notify_config["value_internal_weights"]:
        selected_values["value_2"] = random.choices(
            value_items,
            weights=notify_config["value_internal_weights"][selected_key_2],
            k=1
        )[0]
    else:
        # A name never repeats within one clause
        selected_values["value_2"] = random.choice(
            [v for v in value_items if v != selected_values["value_1"]]
        )
    selected_values["value_2_key"] = selected_key_2
    
    if selected_key_2 == "real_name":
        selected_values["value_2_expected"] = selected_values["value_2"]
    else:
        selected_values["value_2_expected"] = selected_key_2
    
    detail_key_2 = select_detail_key_for_value(selected_key_2, detail_candidate)
    selected_values["detail_value_2_key_for_value_2"] = detail_key_2
    
    # value_3: avoid repeating an $LC_* key already used
    if selected_key_1 in ["$LC_ISSUING_BANK", "$LC_APPLICANT"] and selected_key_2 in ["$LC_ISSUING_BANK", "$LC_APPLICANT"]:
        # Both are $LC_*: value_3 must be real_name
        selected_key_3 = "real_name"
    elif selected_key_1 in ["$LC_ISSUING_BANK", "$LC_APPLICANT"]:
        # value_1 is $LC_*: exclude its key
        available_keys_for_v3 = [k for k in value_keys if k != selected_key_1]
        available_weights_for_v3 = [
            notify_config["value_candidate_weights"][value_keys.index(k)]
            for k in available_keys_for_v3
        ]
        total_weight = sum(available_weights_for_v3)
        available_weights_for_v3 = [w / total_weight for w in available_weights_for_v3]
        selected_key_3 = random.choices(
            available_keys_for_v3,
            weights=available_weights_for_v3,
            k=1
        )[0]
    elif selected_key_2 in ["$LC_ISSUING_BANK", "$LC_APPLICANT"]:
        # value_2 is $LC_*: exclude its key
        available_keys_for_v3 = [k for k in value_keys if k != selected_key_2]
        available_weights_for_v3 = [
            notify_config["value_candidate_weights"][value_keys.index(k)]
            for k in available_keys_for_v3
        ]
        total_weight = sum(available_weights_for_v3)
        available_weights_for_v3 = [w / total_weight for w in available_weights_for_v3]
        selected_key_3 = random.choices(
            available_keys_for_v3,
            weights=available_weights_for_v3,
            k=1
        )[0]
    else:
        selected_key_3 = random.choices(
            value_keys,
            weights=notify_config["value_candidate_weights"],
            k=1
        )[0]
    
    value_items = value_candidate[selected_key_3]
    if selected_key_3 in notify_config["value_internal_weights"]:
        selected_values["value_3"] = random.choices(
            value_items,
            weights=notify_config["value_internal_weights"][selected_key_3],
            k=1
        )[0]
    else:
        selected_values["value_3"] = random.choice(
            [v for v in value_items if v not in (selected_values["value_1"], selected_values["value_2"])]
        )
    selected_values["value_3_key"] = selected_key_3
    
    if selected_key_3 == "real_name":
        selected_values["value_3_expected"] = selected_values["value_3"]
    else:
        selected_values["value_3_expected"] = selected_key_3
    
    # detail_value_1 / detail_value_2 use the detail key mapped from their value
    if detail_key_1 in notify_config["detail_candidate_weights"]:
        selected_values["detail_value_1"] = random.choices(
            detail_candidate[detail_key_1],
            weights=notify_config["detail_candidate_weights"][detail_key_1],
            k=1
        )[0]
    else:
        selected_values["detail_value_1"] = select_from_candidate(detail_candidate[detail_key_1])
    selected_values["detail_value_1_key"] = detail_key_1
    if detail_key_1 == "real_name":
        selected_values["detail_value_1_expected"] = selected_values["detail_value_1"]
    else:
        selected_values["detail_value_1_expected"] = detail_key_1
    
    if detail_key_2 in notify_config["detail_candidate_weights"]:
        selected_values["detail_value_2"] = random.choices(
            detail_candidate[detail_key_2],
            weights=notify_config["detail_candidate_weights"][detail_key_2],
            k=1
        )[0]
    else:
        selected_values["detail_value_2"] = select_from_candidate(detail_candidate[detail_key_2])
    selected_values["detail_value_2_key"] = detail_key_2
    if detail_key_2 == "real_name":
        selected_values["detail_value_2_expected"] = selected_values["detail_value_2"]
    else:
        selected_values["detail_value_2_expected"] = detail_key_2
    
    if "clause_template_weights" in template:
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
        value_1=selected_values["value_1"],
        value_2=selected_values["value_2"],
        value_3=selected_values.get("value_3", ""),
        detail_value_1=selected_values["detail_value_1"],
        detail_value_2=selected_values["detail_value_2"]
    )
    
    gt_json = []
    for item in template["make_json"]:
        gt_item = process_make_json_item(item, selected_values, combinator_candidate)
        gt_json.append(gt_item)
    
    return {
        "clause": clause,
        "gt_json": gt_json,
        "template_idx": template_idx
    }


def process_make_json_item(item: Dict, selected_values: Dict, combinator_candidate: str) -> Dict:
    """
    Convert a make_json item to a gt_json item.
    expected_value:
    - real_name: the actual value (e.g. "ABC CORPORATION")
    - $LC_*: the key name (e.g. "$LC_ISSUING_BANK")
    
    combinator:
    - "/" is written as "OR"
    """
    result = {}
    
    for key, value in item.items():
        if key == "combinator":
            if value == "combinator_candidate":
                result[key] = "OR" if combinator_candidate == "/" else combinator_candidate
            else:
                result[key] = value
        elif key == "expected_value":
            if value == "value_1":
                result[key] = selected_values["value_1_expected"]
            elif value == "value_2":
                result[key] = selected_values["value_2_expected"]
            elif value == "value_3":
                result[key] = selected_values.get("value_3_expected", "")
            elif value == "detail_value_1":
                result[key] = selected_values["detail_value_1_expected"]
            elif value == "detail_value_2":
                result[key] = selected_values["detail_value_2_expected"]
            else:
                result[key] = value
        elif key == "expected_value_concat":
            # expected_value_concat: substitute each element
            concat_values = []
            for v in value:
                if v == "value_1":
                    concat_values.append(selected_values["value_1_expected"])
                elif v == "value_2":
                    concat_values.append(selected_values["value_2_expected"])
                elif v == "detail_value_1":
                    concat_values.append(selected_values["detail_value_1_expected"])
                elif v == "detail_value_2":
                    concat_values.append(selected_values["detail_value_2_expected"])
                else:
                    concat_values.append(v)
            result[key] = concat_values
        elif key == "conditions":
            if isinstance(value, list):
                result[key] = [process_make_json_item(cond, selected_values, combinator_candidate) for cond in value]
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result


if __name__ == "__main__":
    # Example: generate one sample per template
    print("=" * 80)
    print("Template-based clause and GT_JSON examples (notify_party)")
    print("=" * 80)
    
    for i in range(len(TEMPLATES["notify_party"]["templates"])):
        result = generate_clause_and_gtjson(template_idx=i)
        print(f"\n--- Template {i} ---")
        print(f"Clause: {result['clause']}")
        print(f"GT_JSON: {json.dumps(result['gt_json'], indent=2)}")