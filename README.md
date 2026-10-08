# LC Clause Synthesis (B/L)

Synthesizes Bill of Lading requirement clauses as they appear in documentary credits
(SWIFT MT700 field 46A), each paired with a structured ground truth (`gt_json`).

## Data Availability

This repository contains:
- ✅ Synthesis pipeline code (BL)

This repository does NOT contain:
- ❌ Re-processed AI Hub source documents (per AI Hub redistribution policy)

> Only the B/L (Bill of Lading) generator is released for now.
> The generator for IV (Commercial Invoice) will be released soon, followed by a generator
> that combines B/L and IV requirements into a single clause.

## Usage

1. Apply for access to AI Hub Dataset No. 71301 at https://aihub.or.kr
2. Extract consignee / notify party names and addresses from the B/L documents and save
   them in this format (by default as `extracted_bl/dummy.json`).
   `notify_party` needs at least 3 distinct names and `consignee` at least 2.

   ```json
   {
     "consignee":            { "split_extracted_bl": ["ABC LTD.", "BCD LTD."] },
     "consignee_details":    { "split_extracted_bl": ["123, Seoul, S.Korea"] },
     "notify_party":         { "split_extracted_bl": ["ABC ENGINEERS", "ABC CORPORATION", "ABC CT"] },
     "notify_party_details": { "split_extracted_bl": ["123 VILLAGE COURT ..., UNITED STATES"] }
   }
   ```

(Optional) Fill the other `real_name` lists with your own values.
In `templates/make_generate_clause_others.py`, replace
`TEMPLATES[<category>]["value_candidate"]["real_name"]` for any of:
`on_board_date`, `freight_terms`, `port_of_discharge`, `shipper`, `goods_description`,
`hs_code`, `lc_number`, `contract_number`, `issuer`
(and `TEMPLATES["issuer"]["detail_candidate"]["real_name"]` for agent countries).
If you skip this step, the built-in placeholder values are used.

```bash
python generate_combined_clauses.py --no-combinator-random-template --bl-data path/to/your_bl.json --num-samples 1000
python generate_combined_clauses.py --combinator-random-template --bl-data path/to/your_bl.json --num-samples 1000
```

- `--no-combinator-random-template`: no combinators, except the CLEAN / ON BOARD conditions
- `--combinator-random-template`: combinators in consignee, notify party, freight terms and port of discharge
- Without either flag, any template is used. Samples are saved as `generated_clause_bl/sample{n}.json`
  (`--output-dir` to change, `--seed` for reproducible output).
  See `examples/sample1.json` for an example.

Keys (24): `consignee`, `consignee_details`, `endorsement`, `notify_party`,
`notify_party_details`, `shipper`, `issuer`, `issuer_details`, `on_board_date`,
`on_board_notation`, `pre_printed_shipment_wording`, `clean_wording`, `adverse_remarks`,
`freight_terms`, `port_of_discharge`, `goods_description`, `hs_code`, `lc_number`,
`contract_number`, `charter_party`, `surrendered`, `signed/stamped`,
`number_of_originals`, `number_of_copies`

## Roadmap

- [x] B/L (Bill of Lading) clause generator
- [ ] IV (Commercial Invoice) clause generator — coming soon
- [ ] Combined B/L + IV clause generator — after the IV release
