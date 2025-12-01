from dataclasses import dataclass
from shapely.geometry import Point, Polygon as ShapelyPolygon

### Value Sets


@dataclass
class Coordinate:
    latitude: float
    longitude: float

    def within(self, polygon: "Polygon") -> bool:
        point = Point(self.longitude, self.latitude)
        return point.within(
            ShapelyPolygon([(c.longitude, c.latitude) for c in polygon.coordinates])
        )

    def withinDistance(self, distance: float, other: "Coordinate") -> bool:
        point1 = Point(self.longitude, self.latitude)
        point2 = Point(other.longitude, other.latitude)
        return point1.distance(point2) <= distance


@dataclass
class Polygon:
    coordinates: list[Coordinate]


@dataclass
class String:
    value: str

    def endsWith(self, ending: str) -> bool:
        return self.value.endswith(ending)


### Entities


@dataclass
class Truck:
    thing_id: str
    location: Coordinate
    license_plate: String

    @classmethod
    def from_ditto(cls, ditto_entity) -> "Truck":
        return Truck(
            thing_id=ditto_entity["thingId"],
            location=Coordinate(
                latitude=ditto_entity["thingId"]["attributes"]["Location"]["latitude"],
                longitude=ditto_entity["thingId"]["attributes"]["Location"]["latitude"],
            ),
            license_plate=ditto_entity["thingId"]["attributes"]["License Plate"],
        )

    def get_location(self):
        return self.location

    def get_license_plate(self):
        return self.license_plate
