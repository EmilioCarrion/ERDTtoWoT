from dataclasses import dataclass

### Value Sets


### Entities


@dataclass
class Truck:
    thing_id: str
    brand: str
    serial_number: str

    @classmethod
    def from_ditto(cls, ditto_entity) -> "Truck":
        return cls(
            thing_id=ditto_entity["thingId"],
            brand=ditto_entity["attributes"]["brand"],
            serial_number=ditto_entity["attributes"]["serialno"],
        )

    def get_brand(self):
        return self.brand
