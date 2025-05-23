import json
from pathlib import Path
import os

# Load tariff rules from JSON file
RULES = json.loads(Path(__file__).parent.joinpath("rules.json").read_text())

# Gemini API configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash-preview-05-20"