def calculate_congestion_score(traffic_density: float, queue_length: int, lane_blockage_percentage: float) -> float:
    """
    Computes a normalized congestion score between 0 and 100.
    """
    # Normalize components to base metrics if needed, or assume raw scaled inputs
    score = (0.4 * traffic_density) + (0.3 * queue_length) + (0.3 * lane_blockage_percentage)
    return min(100.0, max(0.0, score))

def get_severity_label(score: float) -> str:
    if score <= 30: return "Low"
    if score <= 60: return "Moderate"
    if score <= 85: return "High"
    return "Severe"

def calculate_priority_score(congestion_score: float, violation_freq: int, is_peak_hour: bool) -> float:
    """
    Ranks zones to advise city operators where to deploy traffic officers first.
    """
    peak_impact = 100.0 if is_peak_hour else 20.0
    # Map frequency natively to a 0-100 impact scale
    freq_impact = min(100.0, violation_freq * 5) 
    
    priority = (0.5 * congestion_score) + (0.3 * freq_impact) + (0.2 * peak_impact)
    return round(priority, 1)