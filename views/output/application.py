from client import DittoClient

from model import Truck


from model import Coordinate, Polygon, String

ditto_client = DittoClient()


def get_all_trucks_inside_zone(zone: Polygon) -> list[Truck]:
    entities = ditto_client.query(Truck)
    matching_entities = []
    for entity in entities:
        if entity.get_location().within(zone):
            matching_entities.append(entity)
    return matching_entities

def get_all_trucks_near_place(place: Coordinate) -> list[Truck]:
    entities = ditto_client.query(Truck)
    matching_entities = []
    for entity in entities:
        if entity.get_location().withinDistance(200, place):
            matching_entities.append(entity)
    return matching_entities

def get_all_trucks_with_license_plate_ending(ending: String) -> list[Truck]:
    entities = ditto_client.query(Truck)
    matching_entities = []
    for entity in entities:
        if entity.get_license_plate().endsWith(ending):
            matching_entities.append(entity)
    return matching_entities
