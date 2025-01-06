import logging

logger = logging.getLogger(__name__)

class Galaxy:
    """
    Stores the Galaxy as an adjacency list:
    galaxy[planetA][planetB] = travel_time
    """

    def __init__(self):
        self.routes: dict[str, dict[str, int]] = {}

    def add_route(self, origin: str, destination: str, travel_time: int):
        logger.info(f"Adding route from {origin} to {destination} in {travel_time} days")
        # Add forward path
        if origin not in self.routes:
            self.routes[origin] = {}
        self.routes[origin][destination] = travel_time

        # Add reverse path (undirected graph)
        if destination not in self.routes:
            self.routes[destination] = {}
        self.routes[destination][origin] = travel_time
        logger.info("Current routes[%s]: %s", origin, self.routes[origin])
        logger.info("Current routes[%s]: %s", destination, self.routes[destination])

    def successors(self, planet: str) -> dict[str, int]:
        """All planets reachable from planet"""
        return self.routes.get(planet, {}).keys()

    def edge_value(self, origin: str, destination: str) -> int:
        """Travel time from origin to destination or None if not possible directly"""
        return self.routes.get(origin, {}).get(destination, None)
