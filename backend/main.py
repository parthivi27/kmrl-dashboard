from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

from mock_data import create_conflict_scenario
from optimizer import TrainInductionOptimizer
from explainer import generate_explanation

app = FastAPI(
    title="KMRL Train Induction API",
    description="AI-Driven Train Scheduling for Kochi Metro",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

optimizer = TrainInductionOptimizer()

@app.get("/")
def root():
    return {
        "message": "KMRL Train Induction API",
        "status": "operational",
        "endpoints": ["/api/optimize", "/api/trains", "/api/simulate"]
    }

@app.get("/api/trains")
def get_all_trains():
    trains = create_conflict_scenario()
    return {"trains": trains, "count": len(trains)}

@app.post("/api/optimize")
def run_optimization(target_inducted: int = 20):
    trains = create_conflict_scenario()
    results = optimizer.optimize(trains, target_inducted)
    
    explanations = []
    for train_result in results["all_results"]:
        explanation = generate_explanation(train_result, results["all_results"])
        explanations.append(explanation)
    
    return {
        "success": True,
        "results": results,
        "explanations": explanations,
        "kpis": calculate_kpis(results)
    }

class SimulationRequest(BaseModel):
    unavailable_trains: List[str]
    target_inducted: int = 20

@app.post("/api/simulate")
def run_simulation(request: SimulationRequest):
    trains = create_conflict_scenario()
    available_trains = [
        t for t in trains 
        if t["train_id"] not in request.unavailable_trains
    ]
    
    results = optimizer.optimize(available_trains, request.target_inducted)
    explanations = []
    for train_result in results["all_results"]:
        explanation = generate_explanation(train_result, results["all_results"])
        explanations.append(explanation)
    
    return {
        "success": True,
        "scenario": {
            "removed_trains": request.unavailable_trains,
            "available_count": len(available_trains)
        },
        "results": results,
        "explanations": explanations,
        "kpis": calculate_kpis(results)
    }

def calculate_kpis(results: dict) -> dict:
    inducted = results["inducted"]
    mileages = [t["train_data"]["mileage"]["total_km"] for t in inducted]
    avg_mileage = sum(mileages) / len(mileages)
    variance = sum((m - avg_mileage) ** 2 for m in mileages) / len(mileages)
    std_dev = variance ** 0.5
    mileage_imbalance = (std_dev / avg_mileage) * 100
    
    branding_trains = sum(
        1 for t in inducted 
        if t["train_data"]["branding"]["has_contract"]
    )
    safety_violations = len(results["held"])
    
    return {
        "inducted_count": len(inducted),
        "standby_count": len(results["standby"]),
        "held_count": len(results["held"]),
        "mileage_imbalance_pct": round(mileage_imbalance, 2),
        "branding_trains_inducted": branding_trains,
        "safety_compliance_pct": round((1 - safety_violations / 25) * 100, 1),
        "avg_score": round(sum(t["total_score"] for t in inducted) / len(inducted), 1)
    }

if __name__ == "__main__":
    print("🚆 Starting KMRL Train Induction API...")
    print("📡 Backend: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)