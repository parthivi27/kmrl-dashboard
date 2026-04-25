def generate_explanation(train_result: dict, all_results: list) -> dict:
    """Generate human-readable explanation"""
    train_id = train_result["train_id"]
    decision = train_result["decision"]
    score = train_result["total_score"]
    rank = train_result["rank"]
    breakdown = train_result["score_breakdown"]
    
    explanation = {
        "train_id": train_id,
        "decision": decision,
        "rank": rank,
        "score": score,
        "confidence": calculate_confidence(train_result),
        "summary": "",
        "reasoning": []
    }
    
    if decision == "INDUCTED":
        explanation["summary"] = f"Train {train_id} selected for morning service"
        explanation["reasoning"] = [
            f"Ranked #{rank} out of {len(all_results)} trains",
            f"Total Score: {score:.1f}/100",
            "All safety checks passed"
        ]
        if breakdown["fitness"] == 100:
            explanation["reasoning"].append("All fitness certificates valid")
        if breakdown["branding"] == 100:
            advertiser = train_result["train_data"]["branding"]["advertiser"]
            explanation["reasoning"].append(f"Priority: {advertiser} branding contract")
        if breakdown["cleaning"] > 90:
            explanation["reasoning"].append("Recently cleaned, passenger-ready")
    
    elif decision == "HELD":
        explanation["summary"] = f"Train {train_id} cannot be inducted"
        explanation["reasoning"] = [
            "Failed safety/maintenance checks",
            f"Score: {score:.1f}/100 (below safety threshold)"
        ]
        for violation in train_result["violations"]:
            explanation["reasoning"].append(violation)
        explanation["reasoning"].append("Recommend: Move to maintenance bay")
    
    else:
        explanation["summary"] = f"Train {train_id} on standby"
        explanation["reasoning"] = [
            f"Ranked #{rank}, below top 20 cutoff",
            f"Score: {score:.1f}/100",
            "Available if inducted train fails"
        ]
        if len(all_results) > 19:
            cutoff_score = all_results[19]["total_score"]
            gap = cutoff_score - score
            explanation["reasoning"].append(f"Needs +{gap:.1f} points to qualify")
    
    return explanation

def calculate_confidence(train_result: dict) -> float:
    score = train_result["total_score"]
    decision = train_result["decision"]
    if decision == "HELD":
        return 100.0
    if decision == "INDUCTED":
        if score > 85:
            return 95.0
        elif score > 70:
            return 80.0
        return 65.0
    return 70.0