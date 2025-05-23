import json
import os
import re
from datetime import datetime
import google.generativeai as genai
from .config import GOOGLE_API_KEY, MODEL_NAME, RULES

# Configure Google Generative AI SDK
genai.configure(api_key=GOOGLE_API_KEY)

PORT_NAMES = [
    "Durban", "Cape_Town", "Richards_Bay", "Ngqura",
    "Port_Elizabeth", "Saldanha", "East_London", "Mossel_Bay"
]

def parse_nl_to_request(query: str) -> dict:
    """Parse natural language query to structured request using Gemini"""
    prompt = f"""Extract port tariff calculation parameters from this vessel information:

{query}

Return JSON with these EXACT keys:
- port: Must be one of {PORT_NAMES} (use underscores, no spaces/apostrophes)
- gt: Gross tonnage as float (extract from 'GT / NT' or 'GT' fields)
- loa: Length overall in meters as float
- days_alongside: Days alongside as float
- arrival: ISO 8601 datetime (convert from formats like '15 Nov 2024 10:12')
- departure: ISO 8601 datetime
- operations: Number of operations as integer

Example JSON output:
{{
  "port": "Durban",
  "gt": 51300.0,
  "loa": 229.2,
  "days_alongside": 3.39,
  "arrival": "2024-11-15T10:12:00",
  "departure": "2024-11-22T13:00:00",
  "operations": 2
}}"""

    try:
        if not GOOGLE_API_KEY:
            return fallback_data()

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        content = clean_json_response(response.text)
        
        data = json.loads(content)
        return validate_and_format(data)
    
    except Exception as e:
        print(f"LLM Parsing Error: {str(e)}")
        return fallback_data()

def clean_json_response(text: str) -> str:
    """Extract JSON from possible markdown formatting"""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1]
    return text.strip()

def validate_and_format(data: dict) -> dict:
    """Validate and format parsed data"""
    # Convert port name format
    data["port"] = data["port"].replace(" ", "_").replace("'", "")
    if data["port"] not in PORT_NAMES:
        data["port"] = "Durban"
    
    # Convert date formats
    for field in ["arrival", "departure"]:
        if isinstance(data[field], str):
            try:
                data[field] = datetime.fromisoformat(data[field]).isoformat()
            except:
                data[field] = datetime.now().isoformat()
    
    # Ensure numeric types
    for field in ["gt", "loa", "days_alongside"]:
        data[field] = float(data[field])
    
    data["operations"] = int(data["operations"])
    
    return data

def fallback_data() -> dict:
    """Fallback data for demo/error cases"""
    return {
        "port": "Durban",
        "gt": 51300.0,
        "loa": 229.2,
        "days_alongside": 3.39,
        "arrival": "2024-11-15T10:12:00",
        "departure": "2024-11-22T13:00:00",
        "operations": 2
    }

def generate_explanation(input_data: dict, results: dict) -> str:
    """
    Generate explanation of tariff calculations using Gemini
    
    Args:
        input_data: Dictionary with vessel parameters
        results: Dictionary with calculation results
        
    Returns:
        String explanation
    """
    # Ensure all datetime values are converted to ISO strings for serialization
    serializable_input = {}
    for k, v in input_data.items():
        if isinstance(v, datetime):
            serializable_input[k] = v.isoformat()
        else:
            serializable_input[k] = v
    
    # Include official tariff calculation rules from rules.json
    snippet_keys = [
        "light_dues", "port_dues", "vts_dues",
        "pilotage_dues", "towage_dues", "running_of_vessel_lines_dues"
    ]
    rule_snippets = {k: RULES["tariffs"][k]["calculation"] for k in snippet_keys}
    prompt = (
        "Here are the official tariff calculation rules (calculation sections):\n"
        f"{json.dumps(rule_snippets, indent=2)}\n\n"
        f"Given vessel input: {json.dumps(serializable_input)} and computed results: {json.dumps(results)}, "
        "explain each tariff step-by-step referencing the above rules."
    )
    
    # Safety check for API key
    if not GOOGLE_API_KEY:
        return "Explanation not available without API key."
    
    # Generate response using Gemini
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    
    return response.text