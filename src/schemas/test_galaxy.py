from src.schemas.galaxy import Galaxy


def test_add_route_and_retrieve():
    galaxy = Galaxy()
    galaxy.add_route("planetA", "planetB", 4)

    # Check adjacency for forward direction
    assert "planetB" in galaxy.routes["planetA"]
    assert galaxy.routes["planetA"]["planetB"] == 4

    # Check adjacency for reverse direction
    assert "planetA" in galaxy.routes["planetB"]
    assert galaxy.routes["planetB"]["planetA"] == 4


def test_successors():
    galaxy = Galaxy()
    galaxy.add_route("planetA", "planetB", 4)
    galaxy.add_route("planetA", "planetC", 6)

    successors = galaxy.successors("planetA")
    assert set(successors) == {"planetB", "planetC"}

    # Planet with no routes
    assert set(galaxy.successors("planetD")) == set()


def test_edge_value():
    galaxy = Galaxy()
    galaxy.add_route("planetA", "planetB", 4)

    # Edge exists
    assert galaxy.edge_value("planetA", "planetB") == 4
    assert galaxy.edge_value("planetB", "planetA") == 4

    # Edge doesn't exist
    assert galaxy.edge_value("planetA", "planetC") is None
    assert galaxy.edge_value("planetC", "planetA") is None


def test_add_route_existing_planet():
    galaxy = Galaxy()
    galaxy.add_route("planetA", "planetB", 2)

    # Add another route from the same planet
    galaxy.add_route("planetA", "planetC", 5)

    assert set(galaxy.routes["planetA"].keys()) == {"planetB", "planetC"}
    assert galaxy.routes["planetA"]["planetB"] == 2
    assert galaxy.routes["planetA"]["planetC"] == 5
