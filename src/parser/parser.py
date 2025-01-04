import json
import sqlite3
from src.schemas.data_models import FalconConfig, EmpireData, BountyHunter
from src.schemas.galaxy import Galaxy


def parse_falcon_config(config_file_path: str) -> FalconConfig:
    """
    Parse the Falcon Configuration from the file
    Raise keyError if the file is not in the correct format
    """
    with open(config_file_path, "r") as config_file:
        config = json.load(config_file)

    required_keys = ["autonomy", "departure", "arrival", "routes_db"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing key: {key} in file: {config_file_path}")

    # Convert the relative path to absolute path
    routes_db_path = config_file_path.replace(
        "millennium-falcon.json", config["routes_db"]
    )

    return FalconConfig(
        autonomy=config["autonomy"],
        departure=config["departure"],
        arrival=config["arrival"],
        routes_db_path=routes_db_path,
    )


def parse_empire_data(empire_data_path: str) -> EmpireData:
    """
    Parse the Empire Data from the file
    Raise keyError if the file is not in the correct format
    """
    with open(empire_data_path, "r") as empire_data_file:
        empire_data = json.load(empire_data_file)

    required_keys = ["countdown", "bounty_hunters"]
    for key in required_keys:
        if key not in empire_data:
            raise KeyError(f"Missing key: {key} in file: {empire_data_path}")

    bounty_hunters = []
    for hunter in empire_data["bounty_hunters"]:
        if "planet" not in hunter or "day" not in hunter:
            raise KeyError(
                f"Error in file {empire_data_path}: Each item in 'bounty_hunters' must contain both 'planet' and 'day' keys."
            )
        bounty_hunters.append(BountyHunter(planet=hunter["planet"], day=hunter["day"]))

    return EmpireData(countdown=empire_data["countdown"], bounty_hunters=bounty_hunters)


def parse_routes_db(routes_db_path: str) -> Galaxy:
    """
    Reads routes from the given db file and builds a Galaxy object.
    Expecting a table named ROUTES with columns: ORIGIN, DESTINATION, TRAVEL_TIME
    """
    galaxy = Galaxy()

    with sqlite3.connect(routes_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ORIGIN, DESTINATION, TRAVEL_TIME FROM ROUTES")

        for row in cursor.fetchall():
            origin, destination, travel_time = row
            galaxy.add_route(origin, destination, travel_time)

    return galaxy
