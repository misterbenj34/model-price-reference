import json
import glob
import sys
import os

def validate_json(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        required_keys = ['provider', 'models']
        for key in required_keys:
            if key not in data:
                print(f"Error: Missing key '{key}' in {filepath}")
                return False
        
        if not isinstance(data['models'], list):
            print(f"Error: 'models' must be a list in {filepath}")
            return False
            
        return True
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return False

files = glob.glob('*.json')
all_valid = True
for f in files:
    if not validate_json(f):
        all_valid = False

if not all_valid:
    sys.exit(1)
print("All JSON files validated successfully.")
