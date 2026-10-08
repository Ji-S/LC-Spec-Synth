import random
import json
from typing import Dict, List, Any, Optional

# Template definitions
TEMPLATES = {
    "consignee": {
        "clause_candidate": ["MADE OUT", "ISSUED", "CONSIGNED", "DRAWN"],
        "clause_candidate_weights": [0.4, 0.25, 0.25, 0.1],
        "value_candidate": {
            "$LC_ISSUING_BANK": ["ISSUING BANK"],
            "$LC_APPLICANT": ["APPLICANT"],
            "real_name": ["ABC CORPORATION", "XYZ TRADING CO."]
        },
        "value_candidate_weights": [0.1, 0.3, 0.6],
        "value_internal_weights": {
            "$LC_ISSUING_BANK": [1.0],
            "$LC_APPLICANT": [1.0]
        },
        "value_prefix_candidate": ["TO", "TO THE ORDER OF", "TO ORDER OF"],
        "value_prefix_candidate_weights": [0.1, 0.45, 0.45],
        "detail_candidate": {
            "$LC_APPLICANT_DETAILS": ["WITH FULL NAME AND ADDRESS", "WITH FULL ADDRESS"],
            "$LC_ISSUING_BANK_DETAILS": ["WITH FULL NAME AND ADDRESS", "WITH FULL ADDRESS"],
            "real_name": ["SEOUL, KOREA", "NEW YORK, USA"]
        },
        "detail_candidate_weights": {
            "$LC_APPLICANT_DETAILS": [0.5, 0.5],
            "$LC_ISSUING_BANK_DETAILS": [0.5, 0.5]
        },
        "combinator_candidate": ["OR", "AND/OR", "/"],
        "combinator_candidate_weights": [0.5, 0.1, 0.4],
        "templates": [
            # Template 1
            {
                "clause_template": [
                    "{clause_candidate} {value_prefix_candidate} {value_1}",
                    "{value_prefix_candidate} {value_1}"
                ],
                "clause_template_weights": [0.9, 0.1],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": ["value_prefix_candidate", "value_1"],
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 2
            {
                "clause_template": [
                    "{clause_candidate} {value_prefix_candidate} {value_1}, ENDORSED IN BLANK",
                    "{clause_candidate} {value_prefix_candidate} {value_1} AND ENDORSED IN BLANK",
                    "{clause_candidate} {value_prefix_candidate} {value_1}, BLANK ENDORSED",
                    "{clause_candidate} {value_prefix_candidate} {value_1} AND BLANK ENDORSED",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": ["value_prefix_candidate", "value_1"],
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "endorsement",
                        "expected_value": "BLANK",
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 3
            {
                "clause_template": [
                    "ISSUED OR ENDORSED TO THE ORDER OF {value_1}",
                ],
                "make_json": [
                    {
                        "combinator": "OR",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "consignee",
                                "expected_value": ["TO THE ORDER OF", "value_1"],
                                "operator": "EQUALS"
                            },
                            {
                                "doc": "BL",
                                "key": "endorsement",
                                "expected_value": ["TO THE ORDER OF", "value_1"],
                                "operator": "EQUALS"
                            }
                        ]
                    }
                ]
            },
            # Template 4
            {
                "clause_template": [
                    "{clause_candidate} TO ORDER",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": "TO ORDER",
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 5
            {
                "clause_template": [
                    "{clause_candidate} TO THE ORDER OF SHIPPER",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": "TO THE ORDER OF SHIPPER",
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 6
            {
                "clause_template": [
                    "{clause_candidate} {value_prefix_candidate} {value_1} {detail_value_1}",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": ["value_prefix_candidate", "value_1"],
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "consignee_details",
                        "expected_value": "detail_value_1",
                        "operator": "CONTAINS"
                    }
                ]
            },
            # Template 7
            {
                "clause_template": [
                    "ISSUED OR ENDORSED TO THE ORDER OF {value_1} {detail_value_1}",
                ],
                "make_json": [
                    {
                        "combinator": "OR",
                        "conditions": [
                            {
                                "combinator": "AND",
                                "conditions": [
                                    {
                                        "doc": "BL",
                                        "key": "consignee",
                                        "expected_value": ["TO THE ORDER OF", "value_1"],
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "consignee_details",
                                        "expected_value": "detail_value_1",
                                        "operator": "CONTAINS"
                                    }
                                ]
                            },
                            {
                                "doc": "BL",
                                "key": "endorsement",
                                "expected_value": ["TO THE ORDER OF", "value_1"],
                                "operator": "EQUALS"
                            }
                        ]
                    }
                ]
            },
            # Template 8
            {
                "clause_template": [
                    "{clause_candidate} {value_prefix_candidate} {value_1} {value_2}",
                    "{clause_candidate} {value_prefix_candidate} {value_1}, {value_2}",
                    "{clause_candidate} {value_prefix_candidate} {value_1} AND {value_2}",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": ["value_prefix_candidate","value_1"],
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": ["value_prefix_candidate", "value_2"],
                        "operator": "EQUALS"
                    }
                ]
            },
            # Template 9
            {
                "clause_template": [
                    "{clause_candidate} {value_prefix_candidate} {value_1} {value_2} {detail_value_2}",
                    "{clause_candidate} {value_prefix_candidate} {value_1}, {value_2} {detail_value_2}",
                    "{clause_candidate} {value_prefix_candidate} {value_1} AND {value_2} {detail_value_2}",
                ],
                "make_json": [
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": ["value_prefix_candidate", "value_1"],
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "consignee",
                        "expected_value": ["value_prefix_candidate","value_2"],
                        "operator": "EQUALS"
                    },
                    {
                        "doc": "BL",
                        "key": "consignee_details",
                        "expected_value": "detail_value_2",
                        "operator": "CONTAINS"
                    }
                ]
            },
            # Template 10
            {
                "clause_template": [
                    "{clause_candidate} {value_prefix_candidate} {value_1} {combinator_candidate} {value_2} {detail_value_2}"
                ],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "doc": "BL",
                                "key": "consignee",
                                "expected_value": ["value_prefix_candidate", "value_1"],
                                "operator": "EQUALS"
                            },
                            {
                                "combinator": "AND",
                                "conditions": [
                                    {
                                        "doc": "BL",
                                        "key": "consignee",
                                        "expected_value": ["value_prefix_candidate", "value_2"],
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "consignee_details",
                                        "expected_value": "detail_value_2",
                                        "operator": "CONTAINS"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            # Template 11
            {
                "clause_template": [
                    "{clause_candidate} {value_prefix_candidate} {value_1} {detail_value_1} {combinator_candidate} {value_2} {detail_value_2}"
                ],
                "clause_template_weights": [0.9, 0.1],
                "make_json": [
                    {
                        "combinator": "combinator_candidate",
                        "conditions": [
                            {
                                "combinator": "AND",
                                "conditions": [
                                    {
                                        "doc": "BL",
                                        "key": "consignee",
                                        "expected_value": ["value_prefix_candidate", "value_1"],
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "consignee_details",
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
                                        "key": "consignee",
                                        "expected_value": ["value_prefix_candidate", "value_2"],
                                        "operator": "EQUALS"
                                    },
                                    {
                                        "doc": "BL",
                                        "key": "consignee_details",
                                        "expected_value": "detail_value_2",
                                        "operator": "CONTAINS"
                                    }
                                ]
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
    """Fill the consignee real_name candidates from an extracted B/L data file."""
    with open(path, 'r', encoding='utf-8') as f:
        bl_data = json.load(f)
    
    names = bl_data['consignee']['split_extracted_bl']
    # A clause can name up to 2 distinct consignees
    if len(set(names)) < 2:
        raise ValueError(f"{path} needs at least 2 distinct consignee names")
    
    TEMPLATES['consignee']['value_candidate']['real_name'] = names
    TEMPLATES['consignee']['detail_candidate']['real_name'] = bl_data['consignee_details']['split_extracted_bl']


# Default data, so the module also works on its own; load_bl_data(path) overrides it
if os.path.exists(DEFAULT_BL_DATA_PATH):
    load_bl_data()


def select_from_candidate(candidate: Any) -> Any:
    if isinstance(candidate, list):
        return random.choice(candidate)
    return candidate


def get_value_for_key(key: str, value_candidate: Dict, detail_candidate: Dict) -> str:
    if key in value_candidate:
        return select_from_candidate(value_candidate[key])
    elif key in detail_candidate:
        return select_from_candidate(detail_candidate[key])
    else:
        return key


def get_detail_for_key(key: str, detail_candidate: Dict) -> str:
    if key in detail_candidate:
        return select_from_candidate(detail_candidate[key])
    return key


def select_detail_key_for_value(selected_key: str, detail_candidate: Dict) -> str:
    if selected_key == "real_name":
        return "real_name"
    elif selected_key == "$LC_ISSUING_BANK":
        if random.random() < 0.5:
            return "$LC_ISSUING_BANK_DETAILS"
        else:
            return "real_name"
    elif selected_key == "$LC_APPLICANT":
        if random.random() < 0.5:
            return "$LC_APPLICANT_DETAILS"
        else:
            return "real_name"
    else:
        return "real_name"


def generate_clause_and_gtjson(template_idx: int = None) -> Dict[str, Any]:
    consignee_config = TEMPLATES["consignee"]
    
    if template_idx is None:
        template_idx = random.randint(0, len(consignee_config["templates"]) - 1)
    
    template = consignee_config["templates"][template_idx]
    
    clause_candidate = random.choices(
        consignee_config["clause_candidate"],
        weights=consignee_config["clause_candidate_weights"],
        k=1
    )[0]
    combinator_candidate = random.choices(
        consignee_config["combinator_candidate"],
        weights=consignee_config["combinator_candidate_weights"],
        k=1
    )[0]
    
    value_candidate = consignee_config["value_candidate"]
    detail_candidate = consignee_config["detail_candidate"]
    
    selected_values = {}
    
    value_keys = list(value_candidate.keys())
    selected_key_1 = random.choices(
        value_keys,
        weights=consignee_config["value_candidate_weights"],
        k=1
    )[0]
    value_items = value_candidate[selected_key_1]
    if selected_key_1 in consignee_config["value_internal_weights"]:
        selected_values["value_1"] = random.choices(
            value_items,
            weights=consignee_config["value_internal_weights"][selected_key_1],
            k=1
        )[0]
    else:
        selected_values["value_1"] = select_from_candidate(value_items)
    selected_values["value_1_key"] = selected_key_1
    
    detail_key_1 = select_detail_key_for_value(selected_key_1, detail_candidate)
    selected_values["detail_value_1_key_for_value_1"] = detail_key_1
    
    if selected_key_1 in ["$LC_ISSUING_BANK", "$LC_APPLICANT"]:
        available_keys_for_v2 = [k for k in value_keys if k != selected_key_1]
        available_weights_for_v2 = [
            consignee_config["value_candidate_weights"][value_keys.index(k)]
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
            weights=consignee_config["value_candidate_weights"],
            k=1
        )[0]
    
    value_items = value_candidate[selected_key_2]
    if selected_key_2 in consignee_config["value_internal_weights"]:
        selected_values["value_2"] = random.choices(
            value_items,
            weights=consignee_config["value_internal_weights"][selected_key_2],
            k=1
        )[0]
    else:
        # A name never repeats within one clause
        selected_values["value_2"] = random.choice(
            [v for v in value_items if v != selected_values["value_1"]]
        )
    selected_values["value_2_key"] = selected_key_2
    
    detail_key_2 = select_detail_key_for_value(selected_key_2, detail_candidate)
    selected_values["detail_value_2_key_for_value_2"] = detail_key_2
    
    if detail_key_1 in consignee_config["detail_candidate_weights"]:
        selected_values["detail_value_1"] = random.choices(
            detail_candidate[detail_key_1],
            weights=consignee_config["detail_candidate_weights"][detail_key_1],
            k=1
        )[0]
    else:
        selected_values["detail_value_1"] = select_from_candidate(detail_candidate[detail_key_1])
    selected_values["detail_value_1_key"] = detail_key_1
    if detail_key_1 == "real_name":
        selected_values["detail_value_1_expected"] = selected_values["detail_value_1"]
    else:
        selected_values["detail_value_1_expected"] = detail_key_1
    
    if detail_key_2 in consignee_config["detail_candidate_weights"]:
        selected_values["detail_value_2"] = random.choices(
            detail_candidate[detail_key_2],
            weights=consignee_config["detail_candidate_weights"][detail_key_2],
            k=1
        )[0]
    else:
        selected_values["detail_value_2"] = select_from_candidate(detail_candidate[detail_key_2])
    selected_values["detail_value_2_key"] = detail_key_2
    if detail_key_2 == "real_name":
        selected_values["detail_value_2_expected"] = selected_values["detail_value_2"]
    else:
        selected_values["detail_value_2_expected"] = detail_key_2
    
    # Every value gets a prefix in the clause (TO / TO THE ORDER OF / TO ORDER OF),
    # so B/Ls read "TO THE ORDER OF ISSUING BANK" too; gt_json drops it for $LC_* keys
    selected_values["value_1_prefix"] = random.choices(
        consignee_config["value_prefix_candidate"],
        weights=consignee_config["value_prefix_candidate_weights"],
        k=1
    )[0]

    selected_values["value_2_prefix"] = random.choices(
        consignee_config["value_prefix_candidate"],
        weights=consignee_config["value_prefix_candidate_weights"],
        k=1
    )[0]
    
    # Prefix actually rendered in the clause (defaults to "TO")
    actual_prefix_used_in_clause = selected_values["value_1_prefix"] if selected_values["value_1_prefix"] else "TO"
    selected_values["actual_prefix"] = actual_prefix_used_in_clause
    
    # expected_value: the real value for real_name, the key name for $LC_*.
    # The prefix is joined in later from ["value_prefix_candidate", "value_N"].
    if selected_key_1 == "real_name":
        selected_values["value_1_expected"] = selected_values["value_1"]
    else:
        selected_values["value_1_expected"] = selected_key_1
    
    if selected_key_2 == "real_name":
        selected_values["value_2_expected"] = selected_values["value_2"]
    else:
        selected_values["value_2_expected"] = selected_key_2
    
    # {value_prefix_candidate} gets the chosen prefix; {value_N} gets the bare value
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
        value_1=selected_values["value_1"],
        value_2=selected_values["value_2"],
        detail_value_1=selected_values["detail_value_1"],
        detail_value_2=selected_values["detail_value_2"],
        value_prefix_candidate=selected_values["value_1_prefix"] if selected_values["value_1_prefix"] else "TO"
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
    result = {}
    
    for key, value in item.items():
        if key == "combinator":
            if value == "combinator_candidate":
                result[key] = "OR" if combinator_candidate == "/" else combinator_candidate
            else:
                result[key] = value
        elif key == "expected_value":
            # List form: join the parts, e.g. ["TO", "value_1"] -> "TO ABC LTD."
            if isinstance(value, list):
                parts = []
                prev_was_prefix = False
                for i, v in enumerate(value):
                    if v == "value_1":
                        parts.append(selected_values["value_1_expected"])
                        prev_was_prefix = False
                    elif v == "value_2":
                        parts.append(selected_values["value_2_expected"])
                        prev_was_prefix = False
                    elif v == "detail_value_1":
                        parts.append(selected_values["detail_value_1_expected"])
                        prev_was_prefix = False
                    elif v == "detail_value_2":
                        parts.append(selected_values["detail_value_2_expected"])
                        prev_was_prefix = False
                    elif v == "value_prefix_candidate":
                        # Use the prefix rendered in the clause, but drop it before an $LC_* key
                        next_v = value[i+1] if i+1 < len(value) else None
                        if next_v == "value_1":
                            if selected_values.get("value_1_key", "").startswith("$LC_"):
                                prev_was_prefix = True
                                continue
                            else:
                                parts.append(selected_values.get("actual_prefix", "TO"))
                        elif next_v == "value_2":
                            if selected_values.get("value_2_key", "").startswith("$LC_"):
                                prev_was_prefix = True
                                continue
                            else:
                                parts.append(selected_values.get("actual_prefix", "TO"))
                        else:
                            parts.append(selected_values.get("actual_prefix", "TO"))
                        prev_was_prefix = True
                    elif v in ("TO", "TO THE ORDER OF"):
                        # Drop a fixed prefix before an $LC_* key
                        next_v = value[i+1] if i+1 < len(value) else None
                        if next_v == "value_1":
                            if selected_values.get("value_1_key", "").startswith("$LC_"):
                                prev_was_prefix = True
                                continue
                            else:
                                parts.append(v)
                        elif next_v == "value_2":
                            if selected_values.get("value_2_key", "").startswith("$LC_"):
                                prev_was_prefix = True
                                continue
                            else:
                                parts.append(v)
                        else:
                            parts.append(v)
                        prev_was_prefix = True
                    else:
                        parts.append(v)
                        prev_was_prefix = False
                result[key] = " ".join(parts)
            elif value == "value_1":
                result[key] = selected_values["value_1_expected"]
            elif value == "value_2":
                result[key] = selected_values["value_2_expected"]
            elif value == "detail_value_1":
                result[key] = selected_values["detail_value_1_expected"]
            elif value == "detail_value_2":
                result[key] = selected_values["detail_value_2_expected"]
            else:
                result[key] = value
        elif key == "expected_value" and isinstance(value, list) and any(v in value for v in ["value_1", "value_2", "detail_value_1", "detail_value_2", "TO"]):

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
            result[key] = " ".join(concat_values)
        elif key == "conditions":
            if isinstance(value, list):
                result[key] = [process_make_json_item(cond, selected_values, combinator_candidate) for cond in value]
            else:
                result[key] = value
        else:
            result[key] = value
    
    return result


if __name__ == "__main__":
    import os
    
    print("=" * 80)
    print("Generating clauses and GT_JSON (Templates 3, 7, 10 only, 300 samples)")
    print("=" * 80)
    
    # Templates 3, 7, 10 only (indices 2, 6, 9)
    allowed_templates = [2, 6, 9]
    
    results = []
    for i in range(300):
        template_idx = allowed_templates[i % len(allowed_templates)]
        result = generate_clause_and_gtjson(template_idx=template_idx)
        results.append(result)
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated_consignee_endorsement_bl')
    os.makedirs(output_dir, exist_ok=True)
    
    for i, result in enumerate(results):
        output_path = os.path.join(output_dir, f'sample{i+1}.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(results)} clauses.")
    print(f"Output directory: {output_dir}")
    
    template_counts = {}
    for r in results:
        t = r['template_idx']
        template_counts[t] = template_counts.get(t, 0) + 1
    print(f"\nTemplate distribution:")
    for t, count in sorted(template_counts.items()):
        print(f"  Template {t}: {count}")
