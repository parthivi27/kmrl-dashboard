# Here is the data of the 25 trains in the KMRL fleet, with a mix of good and problematic cases to test the optimization logic effectively. This data can be used to simulate the inducting process and evaluate the scoring and constraint-checking mechanisms.

import random
from datetime import datetime, timedelta

def generate_train_data(num_trains=25):
    """Generate mock train data for KMRL fleet"""
    trains = []
    
    brand_advertisers = [
        "Coca-Cola", "Pepsi", "Amazon", "Flipkart", 
        "HDFC Bank", "Samsung", "Nike", "McDonald's"
    ]
    
    for i in range(1, num_trains + 1):
        train_id = f"KMRL-{i:03d}"
        
        certs_status = random.choices(
            ["VALID", "EXPIRES_24H", "EXPIRED"], 
            weights=[0.85, 0.10, 0.05]
        )[0]
        
        has_open_jobs = random.random() < 0.20
        base_mileage = 50000
        mileage_variation = random.randint(-10000, 15000)
        total_mileage = base_mileage + mileage_variation
        days_since_cleaning = random.randint(1, 30)
        has_branding = random.random() < 0.30
        brand_name = random.choice(brand_advertisers) if has_branding else None
        bay_positions = ["IBL-01", "IBL-02", "STABLE-A1", "STABLE-A2", "STABLE-B1"]
        bay_position = random.choice(bay_positions)
        
        train = {
            "train_id": train_id,
            "fitness_certs": {
                "rolling_stock": certs_status,
                "signalling": certs_status,
                "telecom": random.choice(["VALID", "EXPIRES_24H", "EXPIRED"])
            },
            "job_cards": {
                "open_critical": 1 if has_open_jobs else 0,
                "open_minor": random.randint(0, 3),
                "closed_today": random.randint(0, 5)
            },
            "mileage": {
                "total_km": total_mileage,
                "daily_avg": round(total_mileage / 365, 2),
                "last_reset": "2024-01-01"
            },
            "cleaning": {
                "last_cleaned": (datetime.now() - timedelta(days=days_since_cleaning)).isoformat(),
                "days_since": days_since_cleaning,
                "status": "OVERDUE" if days_since_cleaning > 20 else "OK"
            },
            "branding": {
                "has_contract": has_branding,
                "advertiser": brand_name,
                "min_exposure_hours": 18 if has_branding else 0,
                "contract_value_inr": 500000 if has_branding else 0
            },
            "stabling": {
                "current_bay": bay_position,
                "distance_to_exit_m": random.randint(50, 500),
                "shunting_required": random.choice([True, False])
            }
        }
        trains.append(train)
    
    return trains

def create_conflict_scenario():
    """Create a scenario with some problematic trains"""
    trains = generate_train_data(25)
    
    if len(trains) > 6:
        trains[6]["fitness_certs"]["telecom"] = "EXPIRES_24H"
        trains[6]["train_id"] = "KMRL-007"
    
    if len(trains) > 11:
        trains[11]["branding"]["has_contract"] = True
        trains[11]["branding"]["advertiser"] = "Coca-Cola"
        trains[11]["train_id"] = "KMRL-012"
    
    if len(trains) > 18:
        trains[18]["job_cards"]["open_critical"] = 2
        trains[18]["train_id"] = "KMRL-019"
    
    return trains