import json
import pytest
import sqlite3
from src.parser.parser import parse_falcon_config, parse_empire_data, parse_routes_db
from src.schemas.data_models import FalconConfig, EmpireData, BountyHunter
from src.schemas.galaxy import Galaxy


def test_parse_falcon_config_success(tmp_path):

    expected_config_content = {
        "autonomy": 6,
        "departure": "planetA",
        "arrival": "planetB",
        "routes_db": "universe.db",
    }

    temp_config_path = tmp_path / "millennium-falcon.json"
    temp_config_path.write_text(json.dumps(expected_config_content))

    falcon_config = parse_falcon_config(str(temp_config_path))

    assert isinstance(falcon_config, FalconConfig)
    assert falcon_config.autonomy == expected_config_content["autonomy"]
    assert falcon_config.departure == expected_config_content["departure"]
    assert falcon_config.arrival == expected_config_content["arrival"]
    assert falcon_config.routes_db_path == str(temp_config_path).replace(
        "millennium-falcon.json", "universe.db"
    )


def test_parse_falcon_config_missing_key(tmp_path):

    # Missing 'arrival' key
    incomplete_config_content = {
        "autonomy": 6,
        "departure": "planetA",
        "routes_db": "universe.db",
    }

    temp_config_path = tmp_path / "millennium-falcon.json"
    temp_config_path.write_text(json.dumps(incomplete_config_content))

    with pytest.raises(KeyError) as exc_info:
        _ = parse_falcon_config(str(temp_config_path))

    assert "arrival" in str(exc_info.value)


def test_parse_empire_data_success(tmp_path):

    empire_content = {
        "countdown": 10,
        "bounty_hunters": [
            {"planet": "planetA", "day": 4},
            {"planet": "planetB", "day": 5},
        ],
    }
    empire_data_path = tmp_path / "empire.json"
    empire_data_path.write_text(json.dumps(empire_content))

    empire_data = parse_empire_data(str(empire_data_path))

    assert isinstance(empire_data, EmpireData)
    assert empire_data.countdown == 10
    assert len(empire_data.bounty_hunters) == 2
    assert isinstance(empire_data.bounty_hunters[0], BountyHunter)
    assert empire_data.bounty_hunters[0].planet == "planetA"
    assert empire_data.bounty_hunters[0].day == 4


def test_parse_empire_data_missing_key_raises(tmp_path):

    # Missing 'bounty_hunters' key
    empire_content = {"countdown": 7}
    empire_data_path = tmp_path / "empire.json"
    empire_data_path.write_text(json.dumps(empire_content))

    with pytest.raises(KeyError) as exc_info:
        _ = parse_empire_data(str(empire_data_path))
    assert "bounty_hunters" in str(exc_info.value)


def test_parse_empire_data_missing_bounty_hunter_keys_raises(tmp_path):

    # The second bounty hunter is missing 'day'
    empire_content = {
        "countdown": 7,
        "bounty_hunters": [{"planet": "planetA", "day": 4}, {"planet": "planetB"}],
    }
    empire_data_path = tmp_path / "empire.json"
    empire_data_path.write_text(json.dumps(empire_content))

    with pytest.raises(KeyError) as exc_info:
        _ = parse_empire_data(str(empire_data_path))
    assert "planet" in str(exc_info.value) and "day" in str(exc_info.value)


def test_parse_routes_db_success(tmp_path):

    db_path = tmp_path / "universe.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE ROUTES (ORIGIN TEXT, DESTINATION TEXT, TRAVEL_TIME INTEGER)"
    )
    cursor.execute(
        "INSERT INTO ROUTES (ORIGIN, DESTINATION, TRAVEL_TIME) VALUES (?, ?, ?)",
        ("planetA", "planetB", 4),
    )
    cursor.execute(
        "INSERT INTO ROUTES (ORIGIN, DESTINATION, TRAVEL_TIME) VALUES (?, ?, ?)",
        ("planetB", "planetC", 1),
    )
    conn.commit()
    conn.close()

    galaxy = parse_routes_db(str(db_path))
    assert isinstance(galaxy, Galaxy)

    assert "planetA" in galaxy.routes
    assert "planetB" in galaxy.routes["planetA"]
    assert galaxy.routes["planetA"]["planetB"] == 4

    assert "planetB" in galaxy.routes
    assert "planetC" in galaxy.routes["planetB"]
    assert galaxy.routes["planetB"]["planetC"] == 1
