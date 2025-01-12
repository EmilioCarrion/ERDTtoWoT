from dataclasses import dataclass
from fastapi import FastAPI, Request, HTTPException

from application import get_trucks_by_brand


from model import Truck



from security import has_permission

app = FastAPI()


@app.get("/get_trucks_by_brand")
async def get_trucks_by_brand_view(request: Request, brand: str) -> list[Truck]:
    
    if not has_permission(request.client.host, "Truck::get_brand"):
        raise HTTPException(status_code=403, detail="Permission denied")
    

    entities = get_trucks_by_brand(brand)
    return entities
