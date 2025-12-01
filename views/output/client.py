from typing import Type, TypeVar
import requests

T = TypeVar("T")


class DittoClient:
    def query(self, return_type: Type[T]) -> list[T]:
        response = requests.get(
            "http://localhost:8080/api/2/search/things",
            headers={
                "accept": "application/json",
                "Authorization": "Basic ZGl0dG86MTIzNDU2Nzg=",
            },
        )
        return [return_type.from_ditto(item) for item in response.json()["items"]]