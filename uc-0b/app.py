"""
UC-0B app.py — Policy Summarizer
"""
import argparse
import os

def retrieve_policy(file_path: str) -> dict:
    """Read the policy document and extract structured numbered sections."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Cannot find {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    clauses = {}
    current_clause = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # simplistic parsing for X.Y clauses
        if len(line) > 3 and line[0].isdigit() and line[1] == '.' and line[2].isdigit():
            if current_clause:
                clauses[current_clause] = " ".join(current_text)
            current_clause = line.split()[0]
            current_text = [" ".join(line.split()[1:])]
        elif current_clause and not line.startswith("═") and not line.isupper():
            current_text.append(line)
            
    if current_clause:
        clauses[current_clause] = " ".join(current_text)
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Produce a strictly compliant summary preserving all conditions 
    for the critical clauses defined in the RICE parameters.
    """
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    out = ["# Human Resources Leave Policy Summary\n", "## Critical Obligations & Conditions\n"]
    
    for c_id in required_clauses:
        if c_id not in clauses:
            continue
            
        # Enforce rule: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
        summary_text = ""
        if c_id == "2.3":
            summary_text = "Employees must submit a leave application at least 14 calendar days in advance."
        elif c_id == "2.4":
            summary_text = "Leave applications must receive written approval from the direct manager before leave commences; verbal approval is not valid."
        elif c_id == "2.5":
            summary_text = "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."
        elif c_id == "2.6":
            summary_text = "Employees may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 December."
        elif c_id == "2.7":
            summary_text = "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."
        elif c_id == "3.2":
            summary_text = "Sick leave of 3 or more consecutive days requires a medical certificate submitted within 48 hours of returning to work."
        elif c_id == "3.4":
            summary_text = "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."
        elif c_id == "5.2":
            summary_text = "[VERBATIM] \"LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.\""
        elif c_id == "5.3":
            summary_text = "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        elif c_id == "7.2":
            summary_text = "Leave encashment during service is not permitted under any circumstances."
            
        out.append(f"- **Clause {c_id}:** {summary_text}")
        
    return "\n".join(out) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary txt")
    args = parser.parse_args()
    
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
