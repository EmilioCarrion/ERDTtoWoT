from dataclasses import dataclass
from fastapi import FastAPI, Request, HTTPException

from application import get_all_trucks_inside_zone

from application import get_all_trucks_near_place

from application import get_all_trucks_with_license_plate_ending


from model import Truck


from model import Coordinate, Polygon, String

from security import has_permission

app = FastAPI()


@app.post("/get_all_trucks_inside_zone")
async def get_all_trucks_inside_zone_view(request: Request, zone: Polygon) -> list[Truck]:
    
    if not has_permission(request.client.host, "Truck::Get Location"):
        raise HTTPException(status_code=403, detail="Permission denied")
    

    entities = get_all_trucks_inside_zone(zone)
    return entities

@app.post("/get_all_trucks_near_place")
async def get_all_trucks_near_place_view(request: Request, place: Coordinate) -> list[Truck]:
    
    if not has_permission(request.client.host, "Truck::Get Location"):
        raise HTTPException(status_code=403, detail="Permission denied")
    

    entities = get_all_trucks_near_place(place)
    return entities

@app.post("/get_all_trucks_with_license_plate_ending")
async def get_all_trucks_with_license_plate_ending_view(request: Request, ending: String) -> list[Truck]:
    
    if not has_permission(request.client.host, "Truck::Get License Plate"):
        raise HTTPException(status_code=403, detail="Permission denied")
    

    entities = get_all_trucks_with_license_plate_ending(ending)
    return entities
