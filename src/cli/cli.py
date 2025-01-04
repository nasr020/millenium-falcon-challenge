import argparse
import sys
from src.core.core import OddsService

def main():
    parser = argparse.ArgumentParser(description="Compute the odds that the Millennium Falcon reaches Endor in time.")

    parser.add_argument("falcon_config", type=str, help="Path to the millennium-falcon.json file.")

    parser.add_argument("empire_config", type=str, help="Path to the empire.json file.")

    args = parser.parse_args()

    service = OddsService()

    try:
        odds = service.compute_odds(args.falcon_config, args.empire_config)
        print(odds)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()