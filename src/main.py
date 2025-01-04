import sys
from src.core.core import OddsService
from src.parser.parser import parse_empire_data


def main():
    if len(sys.argv) != 3:
        print("Usage: give-me-the-odds <millennium-falcon.json> <empire.json>")
        sys.exit(1)

    falcon_config_path = sys.argv[1]
    empire_config_path = sys.argv[2]

    service = OddsService()
    odds = service.compute_odds(falcon_config_path, empire_config_path)
    print(odds)


if __name__ == "__main__":
    main()
