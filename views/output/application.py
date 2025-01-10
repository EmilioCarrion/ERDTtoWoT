from ditto import DittoClient

from model import Truck


ditto_client = DittoClient()


def get_active_trucks() -> list[Truck]:
    entities = ditto_client.query(Truck)
    matching_entities = []
    for entity in entities:
        if entity.is_active():
            matching_entities.append(entity)
    return matching_entities

def get_trucks_by_brand(brand: str) -> list[Truck]:
    entities = ditto_client.query(Truck)
    matching_entities = []
    for entity in entities:
        if entity.get_brand() == brand:
            matching_entities.append(entity)
    return matching_entities
