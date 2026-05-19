import argparse
import json
from src.orchestrator import Orchestrator

if __name__ == "__main__":
    """
    Default command
        (venv)$ python main.py --json_input input.dev.json
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_input", required=True)
    args = parser.parse_args()
    with open(args.json_input, "r", encoding="utf-8") as file:
        input_list = json.load(file)
    orchestrator = Orchestrator(input_list)
    orchestrator.main()
