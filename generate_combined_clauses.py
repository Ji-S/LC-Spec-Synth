import random
import json
import os
import argparse
from typing import Dict, List, Any, Optional, Tuple

def sort_gt_json(gt_json: List[Dict]) -> List[Dict]:
    """
    Sort gt_json deterministically:
    1. By `doc` — all `BL` entries before all `IV` entries.
    2. Within the same `doc`, by `key` alphabetically.
    3. Inside a combinator, sort `conditions` by `key` alphabetically (recursively).
    4. A combinator is positioned by the `key` of its **first** condition (after step 3), and by
       the `doc` of that same condition.
    """
    def get_first_key_and_doc(item: Dict, default_doc: str = "BL") -> tuple:
        """Return the first key and doc of an item (recursing into combinators)."""
        if "key" in item:
            return item.get("key", ""), item.get("doc", default_doc)
        elif "combinator" in item and "conditions" in item and len(item["conditions"]) > 0:
            return get_first_key_and_doc(item["conditions"][0], default_doc)
        return "", default_doc
    
    def sort_conditions_recursive(conditions: List[Dict]) -> List[Dict]:
        """Sort conditions inside a combinator by key alphabetically (recursively)."""
        # Recurse into nested combinators first
        sorted_conditions = []
        for cond in conditions:
            if "combinator" in cond and "conditions" in cond:
                cond["conditions"] = sort_conditions_recursive(cond["conditions"])
            sorted_conditions.append(cond)
        # Then sort this level by key (a combinator uses its first condition's key)
        return sorted(sorted_conditions, key=lambda c: get_first_key_and_doc(c)[0])
    
    def get_sort_key(item: Dict) -> tuple:
        doc = item.get("doc", "BL")
        # BL before IV
        doc_order = 0 if doc == "BL" else 1
        
        # A combinator is positioned by its first condition
        if "combinator" in item and "conditions" in item:
            first_item = item["conditions"][0] if item["conditions"] else {}
            first_key, first_doc = get_first_key_and_doc(first_item, doc)
            first_doc_order = 0 if first_doc == "BL" else 1
            return (first_doc_order, first_doc, first_key)
        
        key = item.get("key", "")
        return (doc_order, doc, key)
    
    # First, sort conditions inside each combinator (mutates item["conditions"] in place)
    for item in gt_json:
        if "combinator" in item and "conditions" in item:
            item["conditions"] = sort_conditions_recursive(item["conditions"])
    
    # Then sort the main array
    return sorted(gt_json, key=get_sort_key)

from templates.make_generate_clause_consignee import generate_clause_and_gtjson as gen_consignee
from templates.make_generate_clause_consignee import TEMPLATES as CONSIGNEE_TEMPLATES
from templates.make_generate_clause_notify_party import generate_clause_and_gtjson as gen_notify_party
from templates.make_generate_clause_notify_party import TEMPLATES as NOTIFY_TEMPLATES
from templates.make_generate_clause_others import generate_clause_and_gtjson as gen_others_func
from templates.make_generate_clause_others import TEMPLATES as OTHERS_TEMPLATES
from templates import make_generate_clause_consignee
from templates import make_generate_clause_notify_party

DEFAULT_BL_DATA_PATH = make_generate_clause_consignee.DEFAULT_BL_DATA_PATH


def load_bl_data(path: str = DEFAULT_BL_DATA_PATH) -> None:
    """Load consignee / notify party names and addresses from an extracted B/L data file."""
    make_generate_clause_consignee.load_bl_data(path)
    make_generate_clause_notify_party.load_bl_data(path)


def _has_combinator(make_json: Any) -> bool:
    """True if a combinator appears anywhere in a make_json structure."""
    if isinstance(make_json, dict):
        return "combinator" in make_json or any(_has_combinator(v) for v in make_json.values())
    if isinstance(make_json, list):
        return any(_has_combinator(v) for v in make_json)
    return False


def _template_indices(templates: List[Dict], with_combinator: bool) -> List[int]:
    return [i for i, t in enumerate(templates) if _has_combinator(t["make_json"]) == with_combinator]


# Categories whose template choice follows the *_random_template flags
_FLAGGED_TEMPLATES = {
    "consignee": CONSIGNEE_TEMPLATES["consignee"]["templates"],
    "notify_party": NOTIFY_TEMPLATES["notify_party"]["templates"],
    "freight_terms": OTHERS_TEMPLATES["freight_terms"]["templates"],
    "port_of_discharge": OTHERS_TEMPLATES["port_of_discharge"]["templates"],
}


# Template indices without / with a combinator, for the *_random_template flags
NO_COMBINATOR_TEMPLATE_IDX = {k: _template_indices(v, False) for k, v in _FLAGGED_TEMPLATES.items()}
COMBINATOR_TEMPLATE_IDX = {k: _template_indices(v, True) for k, v in _FLAGGED_TEMPLATES.items()}


def generate_bill_of_lading_clause(
    originals_result: Optional[Dict] = None,
    clean_result: Optional[Dict] = None,
    copies_result: Optional[Dict] = None,
    surrendered: bool = False
) -> Tuple[str, List[Dict]]:
    """
    Combine number_of_originals, clean_on_board and number_of_copies
    into a single BILL OF LADING clause.

    Args:
        originals_result: result of a number_of_originals template (clause, gt_json)
        clean_result: result of a clean_on_board template (clause, gt_json)
        copies_result: result of a number_of_copies template (clause, gt_json)
        surrendered: never use "ORIGINAL" wording (a surrendered B/L has no originals)

    Returns:
        (clause, gt_json) tuple
    """
    gt_json = []
    
    # Each part is included with 90% probability
    include_originals = (originals_result is not None) and (random.random() < 0.9)
    include_clean = (clean_result is not None) and (random.random() < 0.9)
    include_copies = (copies_result is not None) and (random.random() < 0.9)
    
    num_original = originals_result["clause"] if include_originals and originals_result else None
    clean_on_board = clean_result["clause"] if include_clean and clean_result else None
    num_copies = copies_result["clause"] if include_copies and copies_result else None
    
    if include_originals and originals_result:
        gt_json.extend(originals_result["gt_json"])
    if include_clean and clean_result:
        gt_json.extend(clean_result["gt_json"])
    if include_copies and copies_result:
        gt_json.extend(copies_result["gt_json"])
    
    clause = ""
    
    if num_original:
        if num_copies:
            clause = f"{num_original} {num_copies}"
        else:
            clause = num_original
        
        if clean_on_board:
            clause = clause.replace("BILL OF", f"{clean_on_board} BILL OF")
    else:
        # Without originals, start from a plain BILL OF LADING heading
        if surrendered or random.random() < 0.8:
            clause = "BILL OF LADING"
        else:
            clause = "ORIGINAL BILL OF LADING"
        
        if num_copies:
            clause = f"{clause} {num_copies}"
        
        if clean_on_board:
            clause = clause.replace("BILL OF", f"{clean_on_board} BILL OF")
    
    return clause, gt_json


def generate_combined_clauses(
    random_template: bool = False,
    no_combinator_random_template: bool = False,
    combinator_random_template: bool = False
) -> Dict[str, Any]:
    """
    Generate every category according to its probability.

    Template choice for consignee, notify_party, freight_terms and port_of_discharge
    (at most one flag may be set):
        random_template: any template at random
        no_combinator_random_template: only templates without a combinator, at random
        combinator_random_template: only templates with a combinator, at random
        none set: consignee / notify_party use Template 0; freight_terms and
                  port_of_discharge keep their default random choice

    Probabilities:
    - consignee: 99%
    - notify_party: 95%
    - on_board_date: 30%
    - freight_terms: 90%
    - port_of_discharge: 40%
    - shipper: 40%
    - goods_description: 40%
    - hs_code: 40%
    - lc_number: 40%
    - contract_number: 40%
    - charter_party: 20%
    - surrendered: 20%
    - signed/stamped: 10%
    - issuer: 40%
    - number_of_originals: 90% (never together with surrendered)
    - clean_on_board: 90%
    - number_of_copies: 90%
    
    Ordering:
    - 90%: bill_of_lading, then consignee, then the rest shuffled
    - 10%: bill_of_lading, then everything else shuffled
    - no consignee: bill_of_lading, then everything else shuffled
    """
    if sum([random_template, no_combinator_random_template, combinator_random_template]) > 1:
        raise ValueError("Set at most one of random_template, no_combinator_random_template, combinator_random_template")

    all_clauses = []
    all_gt_json = []
    all_details = []
    other_clauses = []  # every clause except bill_of_lading
    
    # 1. consignee (99%)
    consignee_result = None
    if random.random() < 0.99:
        if no_combinator_random_template:
            consignee_result = gen_consignee(template_idx=random.choice(NO_COMBINATOR_TEMPLATE_IDX["consignee"]))
        elif combinator_random_template:
            consignee_result = gen_consignee(template_idx=random.choice(COMBINATOR_TEMPLATE_IDX["consignee"]))
        elif random_template:
            consignee_result = gen_consignee(template_idx=None)
        else:
            consignee_result = gen_consignee(template_idx=0)

    # 2. notify_party (95%)
    if random.random() < 0.95:
        if no_combinator_random_template:
            result = gen_notify_party(template_idx=random.choice(NO_COMBINATOR_TEMPLATE_IDX["notify_party"]))
        elif combinator_random_template:
            result = gen_notify_party(template_idx=random.choice(COMBINATOR_TEMPLATE_IDX["notify_party"]))
        elif random_template:
            result = gen_notify_party(template_idx=None)
        else:
            result = gen_notify_party(template_idx=0)
        
        other_clauses.append({
            "category": "notify_party",
            "clause": result["clause"],
            "gt_json": result["gt_json"],
            "template_idx": result["template_idx"]
        })
    
    # 3. Other categories, each with its own probability
    other_categories_with_prob = [
        ("on_board_date", 0.3),
        ("freight_terms", 0.9),
        ("port_of_discharge", 0.4),
        ("shipper", 0.4),
        ("goods_description", 0.4),
        ("hs_code", 0.4),
        ("lc_number", 0.4),
        ("contract_number", 0.4),
        ("charter_party", 0.2),
        ("surrendered", 0.2),
        ("signed/stamped", 0.1),
        ("issuer", 0.4)
    ]
    
    for category, prob in other_categories_with_prob:
        if random.random() < prob:
            if no_combinator_random_template and category in NO_COMBINATOR_TEMPLATE_IDX:
                template_idx = random.choice(NO_COMBINATOR_TEMPLATE_IDX[category])
                result = gen_others_func(key=category, template_idx=template_idx)
            elif combinator_random_template and category in COMBINATOR_TEMPLATE_IDX:
                template_idx = random.choice(COMBINATOR_TEMPLATE_IDX[category])
                result = gen_others_func(key=category, template_idx=template_idx)
            # freight_terms uses the combinator template (Template 1) 20% of the time
            elif category == "freight_terms":
                template_idx = 1 if random.random() < 0.2 else 0
                result = gen_others_func(key=category, template_idx=template_idx)
            else:
                result = gen_others_func(key=category, template_idx=None)
            other_clauses.append({
                "category": f"others.{category}",
                "clause": result["clause"],
                "gt_json": result["gt_json"],
                "template_idx": result["template_idx"]
            })
    
    # 4. number_of_originals, clean_on_board, number_of_copies (90% each, random template).
    #    A surrendered B/L has no originals in circulation, so originals are skipped then.
    surrendered = any(item["category"] == "others.surrendered" for item in other_clauses)
    originals_result = gen_others_func(key="number_of_originals", template_idx=None) if not surrendered and random.random() < 0.9 else None
    clean_result = gen_others_func(key="clean_on_board", template_idx=None) if random.random() < 0.9 else None
    copies_result = gen_others_func(key="number_of_copies", template_idx=None) if random.random() < 0.9 else None

    bol_clause, bol_gt_json = generate_bill_of_lading_clause(
        originals_result=originals_result,
        clean_result=clean_result,
        copies_result=copies_result,
        surrendered=surrendered
    )
    
    if bol_clause:
        all_clauses.append({
            "category": "others.bill_of_lading_combined",
            "clause": bol_clause,
            "gt_json": bol_gt_json,
            "template_idx": "combined"
        })
    
    if consignee_result:
        other_clauses.insert(0, {
            "category": "consignee",
            "clause": consignee_result["clause"],
            "gt_json": consignee_result["gt_json"],
            "template_idx": consignee_result["template_idx"]
        })
    
    # 90%: bill_of_lading, then consignee, then the rest shuffled
    # 10% (or no consignee): bill_of_lading, then everything else shuffled
    use_fixed_order = (random.random() < 0.9)
    
    if use_fixed_order and consignee_result:
        bol_item = all_clauses[0] if all_clauses and all_clauses[0]["category"] == "others.bill_of_lading_combined" else None
        if bol_item:
            all_clauses = [bol_item]
            if other_clauses and other_clauses[0]["category"] == "consignee":
                consignee_item = other_clauses.pop(0)
                all_clauses.append(consignee_item)
            random.shuffle(other_clauses)
            all_clauses.extend(other_clauses)
        else:
            # No bill_of_lading clause: consignee first, the rest shuffled
            if other_clauses and other_clauses[0]["category"] == "consignee":
                consignee_item = other_clauses.pop(0)
                all_clauses.append(consignee_item)
            random.shuffle(other_clauses)
            all_clauses.extend(other_clauses)
    else:
        random.shuffle(other_clauses)
        all_clauses.extend(other_clauses)
    
    # Join the clauses with a randomly weighted connector
    connectors = [" ", ", ", " AND "]
    connector_weights = [0.4, 0.5, 0.1]
    
    clause_parts = [item["clause"] for item in all_clauses]
    if len(clause_parts) == 0:
        combined_clause = ""
    elif len(clause_parts) == 1:
        combined_clause = clause_parts[0]
    else:
        combined_parts = [clause_parts[0]]
        for part in clause_parts[1:]:
            selected_connector = random.choices(connectors, weights=connector_weights, k=1)[0]
            combined_parts.append(selected_connector + part)
        combined_clause = "".join(combined_parts)
    
    for item in all_clauses:
        all_gt_json.extend(item["gt_json"])
    
    all_details = all_clauses
    
    return {
        "clause": combined_clause,
        "gt_json": all_gt_json,
        "details": all_details
    }


def main():
    parser = argparse.ArgumentParser(description='Bill of Lading Clause Generator (all categories by probability)')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--random-template', '--random', dest='random_template', action='store_true',
                      help='Random templates (default when no template mode is given)')
    mode.add_argument('--no-combinator-random-template', dest='no_combinator_random_template', action='store_true',
                      help='Random templates without a combinator (consignee, notify_party, freight_terms, port_of_discharge)')
    mode.add_argument('--combinator-random-template', dest='combinator_random_template', action='store_true',
                      help='Random templates with a combinator (consignee, notify_party, freight_terms, port_of_discharge)')
    parser.add_argument('--bl-data', type=str, default=DEFAULT_BL_DATA_PATH,
                        help='Extracted B/L data JSON (default: extracted_bl/dummy.json)')
    parser.add_argument('--num-samples', type=int, default=1, help='Number of samples to generate (default: 1)')
    parser.add_argument('--output-dir', type=str, default='generated_clause_bl',
                        help='Directory for sample{n}.json files (default: generated_clause_bl)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducible output')

    args = parser.parse_args()
    load_bl_data(args.bl_data)
    if args.seed is not None:
        random.seed(args.seed)

    # Without an explicit template mode, pick any template at random
    if not (args.no_combinator_random_template or args.combinator_random_template):
        args.random_template = True

    os.makedirs(args.output_dir, exist_ok=True)
    for i in range(args.num_samples):
        result = generate_combined_clauses(
            random_template=args.random_template,
            no_combinator_random_template=args.no_combinator_random_template,
            combinator_random_template=args.combinator_random_template
        )

        # Sort gt_json deterministically so identical samples serialize identically
        output_data = {
            "clause": result["clause"],
            "gt_json": sort_gt_json(result["gt_json"])
        }
        with open(os.path.join(args.output_dir, f'sample{i+1}.json'), 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if (i + 1) % 100 == 0:
            print(f'Generated {i+1}/{args.num_samples} samples...')

    print(f'Done! Generated {args.num_samples} samples in {args.output_dir}/')


if __name__ == "__main__":
    main()