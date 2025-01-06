from collections import deque
import math
from src.schemas.data_models import FalconConfig, EmpireData, BountyHunter, JourneyLog
from src.schemas.galaxy import Galaxy
from src.parser.parser import parse_falcon_config, parse_empire_data, parse_routes_db


class OddsService:
    """Main service to compute the odds of reaching target planet"""

    def __init__(self):
        self.bounty_hunter_presence: dict[str, set[int]] = {}
        self.empire: EmpireData = None
        self.falcon_config: FalconConfig = None
        self.galaxy: Galaxy = None

    def init_journey(self, config_file_path: str, empire_data_path: str):
        """Load Falcon Config and Empire Data and Galaxy DB routes"""
        self.empire = parse_empire_data(empire_data_path)

        if self.falcon_config is None:
            self.falcon_config = parse_falcon_config(config_file_path)

            self.galaxy = parse_routes_db(self.falcon_config.routes_db_path)

        for bh in self.empire.bounty_hunters:
            if bh.planet not in self.bounty_hunter_presence:
                self.bounty_hunter_presence[bh.planet] = set()
            self.bounty_hunter_presence[bh.planet].add(bh.day)

    def compute_odds(self, config_file_path, empire_data_path):
        """
        Main Function to compute the odds of reaching the target planet
        """
        self.init_journey(config_file_path, empire_data_path)

        successful_journeys = self.get_successful_paths()

        if not len(successful_journeys):
            return 0

        min_hunters = math.inf
        for journey in successful_journeys:
            hunters_encountered = self.number_of_hunters_on_route(journey.route)
            min_hunters = min(min_hunters, hunters_encountered)

        probability_being_captured = 0.0
        for i in range(min_hunters):
            probability_being_captured += (9**i) / (10 ** (i + 1))

        probability_not_captured = 1 - probability_being_captured

        # Return as integer percentage
        return int(probability_not_captured * 100)

    def get_successful_paths(self):
        """
        BFS to find all successful paths
        """
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

                    if next_planet == self.falcon_config.arrival:
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
                q.append(new_journey)
        return successful_journeys

    def number_of_hunters_on_route(self, route: list[str]) -> int:
        """
        Count the number of hunters encountered on the route
        """
        days = 0
        hunters_encountered = 0

        for i in range(len(route) - 1):
            planet = route[i]
            next_planet = route[i + 1]

            if planet == next_planet:
                # Means we spent 1 day refueling
                days += 1
                if (
                    next_planet in self.bounty_hunter_presence
                    and days in self.bounty_hunter_presence[next_planet]
                ):
                    hunters_encountered += 1
            else:
                # Travel from planet to next planet
                travel_time = self.galaxy.edge_value(planet, next_planet)

                days += travel_time

                if (
                    next_planet in self.bounty_hunter_presence
                    and days in self.bounty_hunter_presence[next_planet]
                ):
                    hunters_encountered += 1

        return hunters_encountered
