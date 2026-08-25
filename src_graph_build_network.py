import h3
import pandas as pd
import networkx as nx
from fastapi import FastAPI
import uvicorn

# 1. Initialize FastAPI Engine
app = FastAPI(title="Global Multi-Hazard Climate Risk & Supply Chain Engine")

# 2. Build Supply Chain Dependency Graph
graph = nx.DiGraph()

# Sample Nodes (Ports & Industrial Hubs)
nodes_data = [
    {"id": "PORT_SINGAPORE", "name": "Port of Singapore", "lat": 1.290270, "lon": 103.851959, "type": "Port"},
    {"id": "PORT_ROTTERDAM", "name": "Port of Rotterdam", "lat": 51.956400, "lon": 4.103200, "type": "Port"},
    {"id": "FAC_TAIWAN_CHIP", "name": "Taiwan Fab Hub", "lat": 24.773600, "lon": 121.003900, "type": "Factory"},
    {"id": "HUB_SHANGHAI", "name": "Shanghai Logistics Central", "lat": 31.230400, "lon": 121.473700, "type": "Warehouse"}
]

# Add nodes with Uber H3 Indexing (Res 7 ~5km²) using v4 syntax (latlng_to_cell)
for node in nodes_data:
    h3_hex = h3.latlng_to_cell(node['lat'], node['lon'], 7)
    graph.add_node(node['id'], name=node['name'], h3_index=h3_hex, type=node['type'])

# Add supply dependencies (Edges)
graph.add_edge("FAC_TAIWAN_CHIP", "PORT_SINGAPORE", lead_time_days=3)
graph.add_edge("PORT_SINGAPORE", "PORT_ROTTERDAM", lead_time_days=20)
graph.add_edge("HUB_SHANGHAI", "PORT_SINGAPORE", lead_time_days=4)


@app.get("/")
def home():
    return {
        "status": "Online",
        "engine": "H3 Geospatial Risk Analytics Engine",
        "indexed_nodes": len(graph.nodes)
    }

@app.get("/api/v1/risk-analysis")
def get_risk(lat: float, lon: float):
    # Convert incoming coordinates to H3 Cell using v4 syntax
    query_h3 = h3.latlng_to_cell(lat, lon, 7)
    
    impacted_nodes = []
    for node_id, data in graph.nodes(data=True):
        if data['h3_index'] == query_h3:
            impacted_nodes.append(data['name'])
            
    return {
        "query_h3_index": query_h3,
        "coordinates": [lat, lon],
        "climate_hazard_score": 0.84,
        "sea_level_risk_category": "CRITICAL",
        "impacted_supply_nodes": impacted_nodes if impacted_nodes else ["No direct node match, regional transit route affected"]
    }

if __name__ == "__main__":
    print("Starting Low-Latency Analytics Server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)