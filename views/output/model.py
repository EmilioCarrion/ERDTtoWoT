from dataclasses import dataclass

### Value Sets


@dataclass
class Polygon:
    """
    Add attributes here.
    """

    pass


@dataclass
class Location:
    latitude: float
    longitude: float

    pass


### Entities


@dataclass
class Truck:
    thing_id: str
    location: Location

    def get_location(self):
        return self.location
