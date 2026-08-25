from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import h3

app = FastAPI(title="Global Climate Risk & Supply Chain API")

class RiskQuery(BaseModel):
    latitude: float
    longitude: float
    resolution: int = 7

@app.get("/")
def read_root():
    return {"status": "Active", "engine": "Global Climate Risk Vector API"}

@app.post("/api/v1/spatial-risk")
def calculate_point_risk(query: RiskQuery):
    try:
        h3_cell = h3.geo_to_h3(query.latitude, query.longitude, query.resolution)
        
        # Mock risk vector response aggregated from Parquet/Graph index
        risk_profile = {
            "h3_index": h3_cell,
            "coordinates": [query.latitude, query.longitude],
            "flood_risk_score": 0.78,
            "extreme_heat_days_projected": 34,
            "supply_chain_cascade_risk": "HIGH",
            "downstream_impacted_ports": ["PORT_SINGAPORE", "PORT_ROTTERDAM"]
        }
        return risk_profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)