from dataclasses import dataclass


@dataclass
class FalconConfig:
    """
    Millenium Falcon Configuration
    """

    autonomy: int
    departure: str
    arrival: str
    routes_db_path: str


@dataclass
class BountyHunter:
    """
    One Data Point of Bounty Hunter Presence
    """

    planet: str
    day: int


@dataclass
class EmpireData:
    """
    Stores the Empire Data
    """

    countdown: int
    bounty_hunters: list[BountyHunter]


@dataclass
class JourneyLog:
    """
    Represents one possible Journey (Path)
    """

    current_planet: str
    travel_days: int
    autonomy_left: int
    route: list[str]
