"""
UC-0A — Complaint Classifier / Agent Router
"""
import argparse
import csv
import json
import os
import sys

def load_agents():
    """
    Loads agent configurations representing roles and operational boundaries.
    """
    return [
        {
            "name": "UC-0A Complaint Classifier",
            "keywords": ["complaint", "classify", "category", "priority", "pothole", "flooding", "streetlight", "waste", "noise", "road", "heritage", "heat", "drain"]
        },
        {
            "name": "Fallback Agent",
            "keywords": []
        }
    ]

def load_skills():
    """
    Loads skill configurations representing available capabilities.
    """
    return [
        {
            "name": "classify_complaint",
            "keywords": ["single", "one", "row", "individual"]
        },
        {
            "name": "batch_classify",
            "keywords": ["batch", "csv", "file", "all", "multiple", "list"]
        },
        {
            "name": "fallback_skill",
            "keywords": []
        }
    ]

def classify_query(query, options):
    """
    Detects intent by evaluating a raw query against keyword patterns.
    """
    query_lower = query.lower()
    best_match = None
    max_score = 0
    for option in options:
        keywords = option.get("keywords", [])
        if not keywords: continue
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > max_score:
            max_score = score
            best_match = option
    return best_match, max_score

def route_to_agent(query):
    """
    Parses user input, identifies intent, and maps the query to the correct 
    agent and skill based on the rule-based classification.
    """
    if not isinstance(query, str) or not query.strip():
        return {"agent": "Fallback Agent", "skill": "fallback_skill", "confidence": 0.0, "reason": "Empty or missing user query."}
        
    matched_agent, agent_score = classify_query(query, load_agents())
    matched_skill, skill_score = classify_query(query, load_skills())
    
    reasoning = []
    confidence = 0.0
    
    if matched_agent and agent_score > 0:
        agent_name = matched_agent["name"]
        reasoning.append(f"Keyword match aligned intent with '{agent_name}'.")
        confidence += 0.5
    else:
        agent_name = "Fallback Agent"
        reasoning.append("No clear agent matched the query intent.")
        
    if matched_skill and skill_score > 0:
        skill_name = matched_skill["name"]
        reasoning.append(f"Action routed to '{skill_name}' skill.")
        confidence += 0.4
    else:
        if agent_name == "UC-0A Complaint Classifier":
            skill_name = "batch_classify"
            reasoning.append("Assumed 'batch_classify' skill by default for complaint workflows.")
            confidence += 0.2
        else:
            skill_name = "fallback_skill"
            reasoning.append("No known skill capability detected.")

    return {
        "agent": agent_name,
        "skill": skill_name,
        "confidence": round(max(0.1, min(confidence, 0.99)), 2),
        "reason": " ".join(reasoning)
    }

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the agent's RICE rules.
    """
    desc = row.get('description', '').lower()
    
    # Category Identification
    category = 'Other'
    if 'pothole' in desc: category = 'Pothole'
    elif 'flood' in desc or 'rain' in desc: category = 'Flooding'
    elif 'streetlight' in desc or 'light' in desc: category = 'Streetlight'
    elif 'waste' in desc or 'garbage' in desc or 'animal' in desc: category = 'Waste'
    elif 'noise' in desc or 'music' in desc: category = 'Noise'
    elif 'crack' in desc or 'manhole' in desc or 'footpath' in desc or 'tiles' in desc: category = 'Road Damage'
    elif 'heritage' in desc: category = 'Heritage Damage'
    elif 'heat' in desc: category = 'Heat Hazard'
    elif 'drain' in desc: category = 'Drain Blockage'

    # Priority Identification
    urgent_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = 'Standard'
    found_urgent_word = None
    
    for kw in urgent_keywords:
        if kw in desc:
            priority = 'Urgent'
            found_urgent_word = kw
            break
            
    # Reason Generation
    if found_urgent_word:
        reason = f"Classified as Urgent because description contains severity keyword '{found_urgent_word}'."
    else:
        first_word = desc.split()[0] if desc else "word"
        reason = f"Classified as {category} based on description context mentioning '{first_word}'."
        
    return {
        'complaint_id': row.get('complaint_id', ''),
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': ''  # blank unless ambiguous
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Could not find input file {input_path}")
        return

    results = []
    fieldnames = []
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames if reader.fieldnames else []
            
        for row in reader:
            classification = classify_complaint(row)
            row['category'] = classification['category']
            row['priority'] = classification['priority']
            row['reason'] = classification['reason']
            row['flag'] = classification['flag']
            results.append(row)

    out_fields = list(fieldnames)
    for f in ['category', 'priority', 'reason', 'flag']:
        if f not in out_fields:
            out_fields.append(f)

    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Results written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier / Router")
    parser.add_argument("--input", help="Path to test_[city].csv")
    parser.add_argument("--output", help="Path to write results CSV")
    parser.add_argument("--query", help="Query to route to agent/skill")
    
    # Parse available arguments
    args, unknown = parser.parse_known_args()
    
    if args.input and args.output:
        batch_classify(args.input, args.output)
    elif args.query:
        result = route_to_agent(args.query)
        print(json.dumps(result, indent=2))
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Support raw positional query like: python classifier.py process complaints
        raw_args = " ".join(sys.argv[1:])
        result = route_to_agent(raw_args)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

