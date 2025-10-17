import json
import sys

def load_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        if "tshock" not in config or "startup_parameters" not in config:
            print("Error: config.json is missing required sections ('tshock', 'startup_parameters').", file=sys.stderr)
            sys.exit(1)
            
        return config
    except FileNotFoundError:
        print("Error: config.json not found. Please create it.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode config.json. Please check for syntax errors.", file=sys.stderr)
        sys.exit(1)
