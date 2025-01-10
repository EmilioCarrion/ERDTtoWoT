from dataclasses import dataclass


@dataclass
class Truck:
    thing_id: str
    """
    Add any additional attributes here.
    """

    @classmethod
    def from_ditto(cls, ditto_entity) -> "Truck":
        return cls(
            thing_id=ditto_entity["thingId"],
            # Add any additional attributes here.
        )

    def is_active(self):
        """
        Implement this method to handle the is_active interface.
        """
        ...

    def get_brand(self):
        return "1"
