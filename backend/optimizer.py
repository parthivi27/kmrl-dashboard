from typing import List, Dict, Tuple
from datetime import datetime

class TrainInductionOptimizer:
    """Optimization engine for train induction scheduling"""

    #Rule-based AI + Scoring Optimization
    
    def __init__(self):
        self.weights = {
            'fitness': 0.30,
            'maintenance': 0.25,
            'mileage': 0.15,
            'branding': 0.15,
            'cleaning': 0.10,
            'stabling': 0.05
        }
    
    def calculate_fitness_score(self, train: Dict) -> float:
        certs = train["fitness_certs"]
        if any(cert == "EXPIRED" for cert in certs.values()):
            return 0.0
        if any(cert == "EXPIRES_24H" for cert in certs.values()):
            return 50.0
        return 100.0
    
    def calculate_maintenance_score(self, train: Dict) -> float:
        jobs = train["job_cards"]
        if jobs["open_critical"] > 0:
            return 0.0
        if jobs["open_minor"] > 2:
            return 60.0
        return 100.0
    
    def calculate_mileage_score(self, train: Dict, fleet_avg: float) -> float:
        train_mileage = train["mileage"]["total_km"]
        deviation = abs(train_mileage - fleet_avg)
        max_acceptable_deviation = 5000
        
        if deviation > max_acceptable_deviation:
            score = max(0, 100 - (deviation / 100))
        else:
            score = 100 - (deviation / max_acceptable_deviation * 30)
        return score
    
    def calculate_branding_score(self, train: Dict) -> float:
        return 100.0 if train["branding"]["has_contract"] else 50.0
    
    def calculate_cleaning_score(self, train: Dict) -> float:
        days = train["cleaning"]["days_since"]
        if days > 25:
            return 30.0
        elif days > 15:
            return 70.0
        return 100.0
    
    def calculate_stabling_score(self, train: Dict) -> float:
        distance = train["stabling"]["distance_to_exit_m"]
        return max(0, 100 - (distance / 5))
    
    def calculate_total_score(self, train: Dict, fleet_avg_mileage: float) -> Tuple[float, Dict]:
        scores = {
            'fitness': self.calculate_fitness_score(train),
            'maintenance': self.calculate_maintenance_score(train),
            'mileage': self.calculate_mileage_score(train, fleet_avg_mileage),
            'branding': self.calculate_branding_score(train),
            'cleaning': self.calculate_cleaning_score(train),
            'stabling': self.calculate_stabling_score(train)
        }
        total = sum(scores[k] * self.weights[k] for k in self.weights)
        return round(total, 2), scores
    
    def check_hard_constraints(self, train: Dict) -> Tuple[bool, List[str]]:
        violations = []
        certs = train["fitness_certs"]
        if any(cert == "EXPIRED" for cert in certs.values()):
            violations.append("CRITICAL: Expired fitness certificate")
        if train["job_cards"]["open_critical"] > 0:
            violations.append("CRITICAL: Open critical job cards")
        return len(violations) == 0, violations
    
    def optimize(self, trains: List[Dict], target_inducted: int = 20) -> Dict:
        fleet_avg_mileage = sum(t["mileage"]["total_km"] for t in trains) / len(trains)
        results = []
        
        for train in trains:
            can_induct, violations = self.check_hard_constraints(train)
            total_score, score_breakdown = self.calculate_total_score(train, fleet_avg_mileage)
            results.append({
                "train_id": train["train_id"],
                "can_induct": can_induct,
                "total_score": total_score,
                "score_breakdown": score_breakdown,
                "violations": violations,
                "train_data": train
            })
        
        results.sort(key=lambda x: x["total_score"], reverse=True)
        inducted, standby, held = [], [], []
        
        for idx, result in enumerate(results):
            result["rank"] = idx + 1
            if not result["can_induct"]:
                result["decision"] = "HELD"
                held.append(result)
            elif len(inducted) < target_inducted:
                result["decision"] = "INDUCTED"
                inducted.append(result)
            else:
                result["decision"] = "STANDBY"
                standby.append(result)
        
        return {
            "inducted": inducted,
            "standby": standby,
            "held": held,
            "all_results": results,
            "metadata": {
                "total_trains": len(trains),
                "target_inducted": target_inducted,
                "fleet_avg_mileage": round(fleet_avg_mileage, 2),
                "timestamp": datetime.now().isoformat()
            }
        }