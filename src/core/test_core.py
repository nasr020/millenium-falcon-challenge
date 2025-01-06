import pytest
from unittest.mock import MagicMock
from src.core.core import OddsService
from src.schemas.data_models import FalconConfig, EmpireData, BountyHunter, JourneyLog
from src.schemas.galaxy import Galaxy

@pytest.fixture
def mock_falcon_config():
    """A sample FalconConfig for testing."""
    return FalconConfig(
        autonomy=6,
        departure="Tatooine",
        arrival="Endor",
        routes_db_path="universe.db"
    )

@pytest.fixture
def mock_empire_data():
    """A sample EmpireData with minimal content."""
    return EmpireData(
        countdown=9,
        bounty_hunters=[
            BountyHunter(planet="Hoth", day=6),
            BountyHunter(planet="Hoth", day=7)
        ]
    )

@pytest.fixture
def mock_galaxy():
    """A sample Galaxy with a few routes."""
    galaxy = Galaxy()
    # Add some routes for testing
    # Tatooine -> Hoth, Tatooine -> Dagobah, Dagobah -> Endor, Hoth -> Endor
    galaxy.add_route("Tatooine", "Hoth", 4)
    galaxy.add_route("Tatooine", "Dagobah", 4)
    galaxy.add_route("Dagobah", "Endor", 2)
    galaxy.add_route("Hoth", "Endor", 2)
    return galaxy


def test_compute_odds_no_paths(monkeypatch, mock_falcon_config, mock_empire_data):
    """
    If BFS finds no successful paths, odds should be 0.
    """
    service = OddsService()

    def mock_init_journey(cf_path, ef_path):
        service.falcon_config = mock_falcon_config
        service.empire = mock_empire_data
        service.galaxy = Galaxy()  # No routes

    monkeypatch.setattr(service, "init_journey", mock_init_journey)

    odds = service.compute_odds("fake_millennium.json", "fake_empire.json")
    assert odds == 0, f"Expected 0 odds when no BFS paths found, got {odds}"


def test_compute_odds_with_path(monkeypatch, mock_falcon_config, mock_empire_data):
    """
    If BFS finds at least one path, compute odds > 0 (assuming we don't have bounty hunters on the path).
    """
    service = OddsService()

    def mock_init_journey(cf_path, ef_path):
        service.falcon_config = mock_falcon_config
        service.empire = mock_empire_data

        service.galaxy = Galaxy()
        service.galaxy.add_route("Tatooine", "Endor", 5)  # Single direct route


    monkeypatch.setattr(service, "init_journey", mock_init_journey)

    # With no bounty hunters on that path, we expect 100% odds
    odds = service.compute_odds("fake.json", "fake.json")
    assert odds == 100, f"Expected 100% if there's a safe path, got {odds}"


def test_compute_odds_some_bounty_hunters(monkeypatch, mock_falcon_config, mock_empire_data):
    """
    If BFS finds a path but there's 1 or more bounty-hunter encounters, odds is between 0 and 100.
    """
    service = OddsService()

    # Exactly one bounty hunter on the path
    def mock_init_journey(cf_path, ef_path):
        service.falcon_config = mock_falcon_config
        service.empire = mock_empire_data
        service.galaxy = Galaxy()
        service.galaxy.add_route("Tatooine", "Hoth", 5)
        service.galaxy.add_route("Hoth", "Endor", 2)

        for bh in service.empire.bounty_hunters:
            if bh.planet not in service.bounty_hunter_presence:
                service.bounty_hunter_presence[bh.planet] = set()
            service.bounty_hunter_presence[bh.planet].add(bh.day)


    monkeypatch.setattr(service, "init_journey", mock_init_journey)

    odds = service.compute_odds("ignore.json", "ignore.json")
    assert odds == 90, f"Expected 90% odds for a single bounty-hunter encounter, got {odds}"


def test_find_successful_paths_basic(mock_falcon_config, mock_empire_data, mock_galaxy):
    """
    Test BFS using a 'real' Galaxy object, ensuring the BFS logic returns correct paths.
    """
    service = OddsService()
    service.falcon_config = mock_falcon_config
    service.empire = mock_empire_data
    service.galaxy = mock_galaxy

    # BFS
    paths = service.find_successful_paths()
    assert isinstance(paths, list), "BFS did not return a list of journeys"
    for p in paths:
        assert p.current_planet == "Endor", (
            f"All successful journeys must end at Endor; got {p.current_planet}"
        )
