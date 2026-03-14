"""
UC-0C app.py — Budget Growth Tracker
"""
import argparse
import csv
import os

def load_dataset(file_path: str):
    """
    Reads CSV, validates columns, reports null count and which rows.
    Returns list of parsed dicts.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cannot find {file_path}")
        
    data = []
    null_rows = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Check for missing/blank actual_spend
            if not row.get('actual_spend') or row['actual_spend'].strip() == '' or row['actual_spend'].strip().upper() == 'NULL':
                null_rows.append(f"Row {i+2}: {row.get('period')} · {row.get('ward')} · {row.get('category')} — Reason: {row.get('notes', 'No notes')}")
            data.append(row)
            
    print(f"Loaded {len(data)} rows.")
    if null_rows:
        print(f"WARNING: Discovered {len(null_rows)} deliberately null actual_spend rows:")
        for nr in null_rows:
            print(f"  - {nr}")
            
    return data

def compute_growth(data: list, ward: str, category: str, growth_type: str) -> list:
    """
    Takes ward + category + growth_type, returns per-period table with formula shown.
    Refuses any aggregation across multiple wards/categories explicitly.
    """
    if not ward or not category:
        raise ValueError("REFUSAL: Never aggregate across wards or categories. Ward and category must be explicitly specified.")
        
    if not growth_type:
        raise ValueError("REFUSAL: Growth type not specified. Cannot guess.")
        
    if growth_type.upper() != 'MOM':
        raise ValueError("ERROR: Only MoM (Month-over-Month) is supported in this implementation.")

    # Filter data to specific ward and category, sort by period (YYYY-MM string sorting is safe)
    filtered = [r for r in data if r['ward'] == ward and r['category'] == category]
    filtered.sort(key=lambda x: x['period'])
    
    results = []
    prev_spend = None
    
    for row in filtered:
        period = row['period']
        actual_raw = row['actual_spend']
        notes = row.get('notes', '')
        
        is_null = not actual_raw or actual_raw.strip() == '' or actual_raw.strip().upper() == 'NULL'
        
        current_spend = None
        if not is_null:
            try:
                current_spend = float(actual_raw)
            except ValueError:
                is_null = True
                
        if is_null:
            results.append({
                'ward': ward,
                'category': category,
                'period': period,
                'actual_spend': 'NULL',
                'growth': 'Must be flagged — not computed',
                'formula': 'N/A',
                'notes': notes
            })
            prev_spend = None  # Resets chain
            continue
            
        growth_str = "n/a"
        formula_str = "N/A"
        
        if prev_spend is not None:
            if prev_spend == 0:
                growth_str = "undefined (division by zero)"
                formula_str = f"(({current_spend} - 0) / 0) * 100"
            else:
                growth_val = ((current_spend - prev_spend) / prev_spend) * 100
                sign = "+" if growth_val >= 0 else "−"  # Using minus sign to match readme
                growth_str = f"{sign}{abs(growth_val):.1f}%"
                formula_str = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
        
        results.append({
            'ward': ward,
            'category': category,
            'period': period,
            'actual_spend': f"{current_spend}",
            'growth': growth_str,
            'formula': formula_str,
            'notes': notes
        })
        
        prev_spend = current_spend
        
    return results

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Tracker")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Specific Ward to analyze (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Specific Category to analyze")
    parser.add_argument("--growth-type", required=True, help="Type of calculation (e.g. 'MoM')")
    parser.add_argument("--output", required=True, help="Path to write output csv")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        print("\nREFUSAL: Incomplete arguments. Do not aggregate or guess. You must provide --ward, --category, and --growth-type.")
        return

    data = load_dataset(args.input)
    
    try:
        results = compute_growth(data, args.ward, args.category, args.growth_type)
    except Exception as e:
        print(e)
        return
        
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ward', 'category', 'period', 'actual_spend', 'growth', 'formula', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Success. Wrote {len(results)} computed rows to {args.output}")

if __name__ == "__main__":
    main()
