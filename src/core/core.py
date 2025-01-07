from collections import deque
import math
from src.schemas.data_models import FalconConfig, EmpireData, BountyHunter, JourneyLog
from src.schemas.galaxy import Galaxy
from src.parser.parser import parse_falcon_config, parse_empire_data, parse_routes_db
import logging

logger = logging.getLogger(__name__)


class OddsService:
    """Main service to compute the odds of reaching target planet"""

    def __init__(self):
        self.bounty_hunter_presence: dict[str, set[int]] = {}
        self.empire: EmpireData = None
        self.falcon_config: FalconConfig = None
        self.galaxy: Galaxy = None

    def init_journey(self, config_file_path: str, empire_data_path: str):
        """Load Falcon Config and Empire Data and Galaxy DB routes"""
        logger.info(
            "Initializing journey with Falcon: %s and Empire: %s",
            config_file_path,
            empire_data_path,
        )
        self.empire = parse_empire_data(empire_data_path)

        if self.falcon_config is None:
            logger.debug(
                "Falcon config not yet loaded, parsing from %s", config_file_path
            )
            self.falcon_config = parse_falcon_config(config_file_path)
            logger.debug("Falcon config loaded: %s", self.falcon_config)

            self.galaxy = parse_routes_db(self.falcon_config.routes_db_path)
            logger.debug("Galaxy built from DB: %s", self.falcon_config.routes_db_path)

        for bh in self.empire.bounty_hunters:
            if bh.planet not in self.bounty_hunter_presence:
                self.bounty_hunter_presence[bh.planet] = set()
            self.bounty_hunter_presence[bh.planet].add(bh.day)

        logger.info("Bounty hunter presence updated: %s", self.bounty_hunter_presence)

    def compute_odds(self, config_file_path, empire_data_path):
        """
        Main Function to compute the odds of reaching the target planet
        """
        logger.info(
            "Computing odds with Falcon config: %s, Empire data: %s",
            config_file_path,
            empire_data_path,
        )
        self.init_journey(config_file_path, empire_data_path)

        successful_journeys = self.find_successful_paths()
        logger.info("Found %d successful journeys.", len(successful_journeys))

        if not len(successful_journeys):
            logger.info("No successful journeys found. Odds = 0%")
            return 0

        min_hunters = math.inf
        for journey in successful_journeys:
            hunters_encountered = self.number_of_hunters_on_route(journey.route)
            min_hunters = min(min_hunters, hunters_encountered)

        probability_being_captured = 0.0
        for i in range(min_hunters):
            probability_being_captured += (9**i) / (10 ** (i + 1))

        probability_not_captured = 1 - probability_being_captured
        odds_percent = int(probability_not_captured * 100)

        logger.info("Computed odds = %d%% (min_hunters=%d)", odds_percent, min_hunters)
        return odds_percent

    def find_successful_paths(self):
        """
        BFS to find all successful paths
        """
        logger.debug("Beginning BFS to find successful paths.")
        q = deque()

        successful_journeys = []

        initial_journey = JourneyLog(
            current_planet=self.falcon_config.departure,
            travel_days=0,
            autonomy_left=self.falcon_config.autonomy,
            route=[],
        )

        q.append(initial_journey)

        while q:
            journey_log = q.popleft()
            logger.debug(
                "Exploring from planet=%s, travel_days=%d, autonomy_left=%d",
                journey_log.current_planet,
                journey_log.travel_days,
                journey_log.autonomy_left,
            )

            # Explore all adjacent planets
            for next_planet in self.galaxy.successors(journey_log.current_planet):
                days_to_next_planet = self.galaxy.edge_value(
                    journey_log.current_planet, next_planet
                )
                if days_to_next_planet is None:
                    continue

                # Check if we have enough fuel and if we can still arrive before end of countdown
                if (
                    days_to_next_planet <= journey_log.autonomy_left
                    and journey_log.travel_days + days_to_next_planet
                    <= self.empire.countdown
                ):

                    new_journey = JourneyLog(
                        current_planet=next_planet,
                        travel_days=journey_log.travel_days + days_to_next_planet,
                        autonomy_left=journey_log.autonomy_left - days_to_next_planet,
                        route=journey_log.route + [journey_log.current_planet],
                    )
                    logger.debug(
                        "Possible move to %s, total_days=%d, autonomy_left=%d",
                        next_planet,
                        new_journey.travel_days,
                        new_journey.autonomy_left,
                    )

                    if next_planet == self.falcon_config.arrival:
                        logger.debug(
                            "Found successful path to arrival planet: %s", next_planet
                        )
                        successful_journeys.append(new_journey)
                    else:
                        q.append(new_journey)

            # Consider refueling at current planet
            if journey_log.travel_days + 1 <= self.empire.countdown:
                new_journey = JourneyLog(
                    current_planet=journey_log.current_planet,
                    travel_days=journey_log.travel_days + 1,
                    autonomy_left=self.falcon_config.autonomy,
                    route=journey_log.route + [journey_log.current_planet],
                )
                logger.debug(
                    "Refueling at %s => total_days=%d",
                    journey_log.current_planet,
                    new_journey.travel_days,
                )
                q.append(new_journey)

            # Consider waiting at current planet
            i = 2
            while journey_log.travel_days + i <= self.empire.countdown:
                new_journey = JourneyLog(
                    current_planet=journey_log.current_planet,
                    travel_days=journey_log.travel_days + i,
                    autonomy_left=journey_log.autonomy_left - i,
                    route=journey_log.route + [journey_log.current_planet],
                )
                logger.debug(
                    "Waiting %d days at %s => total_days=%d, autonomy_left=%d",
                    i,
                    journey_log.current_planet,
                    new_journey.travel_days,
                    new_journey.autonomy_left,
                )
                q.append(new_journey)
                i += 1

        logger.debug(
            "BFS complete. Found %d total successful journeys.",
            len(successful_journeys),
        )
        return successful_journeys

    def number_of_hunters_on_route(self, route: list[str]) -> int:
        """
        Count the number of hunters encountered on the route
        """
        logger.debug("Calculating bounty hunter encounters for route: %s", route)
        days = 0
        hunters_encountered = 0

        for i in range(len(route) - 1):
            planet = route[i]
            next_planet = route[i + 1]

            if planet == next_planet:
                # Means we spent 1 day refueling or waiting
                logger.debug("Refueling/waiting at %s => day=%d", next_planet, days)
                days += 1
                if (
                    next_planet in self.bounty_hunter_presence
                    and days in self.bounty_hunter_presence[next_planet]
                ):
                    hunters_encountered += 1
                    logger.debug(
                        "Encountered hunters at %s on day=%d", next_planet, days
                    )
            else:
                # Travel from planet to next planet
                travel_time = self.galaxy.edge_value(planet, next_planet)

                days += travel_time

                logger.debug("Traveling %s->%s => day=%d", planet, next_planet, days)

                if (
                    next_planet in self.bounty_hunter_presence
                    and days in self.bounty_hunter_presence[next_planet]
                ):
                    hunters_encountered += 1
                    logger.debug(
                        "Encountered hunters at %s on day=%d", next_planet, days
                    )

        logger.debug("Total bounty hunter encounters: %d", hunters_encountered)
        return hunters_encountered
