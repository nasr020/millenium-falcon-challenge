import json
import sqlite3
from src.schemas.data_models import FalconConfig, EmpireData, BountyHunter
from src.schemas.galaxy import Galaxy
import logging

logger = logging.getLogger(__name__)


def parse_falcon_config(config_file_path: str) -> FalconConfig:
    """
    Parse the Falcon Configuration from the file
    Raise keyError if the file is not in the correct format
    """
    logger.info("Parsing Millennium Falcon config from: %s", config_file_path)

    with open(config_file_path, "r") as config_file:
        config = json.load(config_file)
    logger.debug("Raw JSON loaded: %s", config)

    required_keys = ["autonomy", "departure", "arrival", "routes_db"]
    for key in required_keys:
        if key not in config:
            logger.error(
                "Key '%s' is missing in Falcon config file: %s", key, config_file_path
            )
            raise KeyError(f"Missing key: {key} in file: {config_file_path}")

    # Convert the relative path to absolute path
    routes_db_path = config_file_path.replace(
        "millennium-falcon.json", config["routes_db"]
    )

    logger.info(
        "Converted routes_db from '%s' to '%s' based on config_file path replacement.",
        config["routes_db"],
        routes_db_path,
    )

    falcon_config = FalconConfig(
        autonomy=config["autonomy"],
        departure=config["departure"],
        arrival=config["arrival"],
        routes_db_path=routes_db_path,
    )

    logger.info("FalconConfig parsed successfully: %s", falcon_config)

    return falcon_config


def parse_empire_data(empire_data_path: str) -> EmpireData:
    """
    Parse the Empire Data from the file
    Raise keyError if the file is not in the correct format
    """
    logger.info("Parsing Empire data from: %s", empire_data_path)
    with open(empire_data_path, "r") as empire_data_file:
        empire_data = json.load(empire_data_file)
    logger.debug("Raw JSON loaded for empire data: %s", empire_data)

    required_keys = ["countdown", "bounty_hunters"]
    for key in required_keys:
        if key not in empire_data:
            logger.error(
                "Key '%s' is missing in Empire file: %s", key, empire_data_path
            )
            raise KeyError(f"Missing key: {key} in file: {empire_data_path}")

    bounty_hunters = []
    for hunter in empire_data["bounty_hunters"]:
        if "planet" not in hunter or "day" not in hunter:
            logger.error("Bounty hunter entry missing 'planet' or 'day': %s", hunter)
            raise KeyError(
                f"Error in file {empire_data_path}: Each item in 'bounty_hunters' must contain both 'planet' and 'day' keys."
            )
        bounty_hunters.append(BountyHunter(planet=hunter["planet"], day=hunter["day"]))

    empire_data_obj = EmpireData(
        countdown=empire_data["countdown"], bounty_hunters=bounty_hunters
    )
    logger.info("EmpireData parsed successfully: %s", empire_data_obj)
    return empire_data_obj


def parse_routes_db(routes_db_path: str) -> Galaxy:
    """
    Reads routes from the given db file and builds a Galaxy object.
    Expecting a table named ROUTES with columns: ORIGIN, DESTINATION, TRAVEL_TIME
    """
    logger.info("Parsing routes from DB file: %s", routes_db_path)
    galaxy = Galaxy()

    try:
        with sqlite3.connect(routes_db_path) as conn:
            cursor = conn.cursor()
            logger.debug("Connected to SQLite database: %s", routes_db_path)

            cursor.execute("SELECT ORIGIN, DESTINATION, TRAVEL_TIME FROM ROUTES")
            rows = cursor.fetchall()
            logger.debug("Fetched %d rows from ROUTES table.", len(rows))

            for row in rows:
                origin, destination, travel_time = row
                galaxy.add_route(origin, destination, travel_time)

            logger.info("Added %d routes into Galaxy from the database.", len(rows))
    except sqlite3.Error as e:
        logger.error("SQLite error occurred while reading routes: %s", str(e))
        raise
    return galaxy
