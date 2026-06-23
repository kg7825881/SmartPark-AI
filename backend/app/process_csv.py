import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
from sklearn.cluster import DBSCAN

def get_violation_severity(violation_str: str) -> float:
    weights = {
        "DOUBLE PARKING": 2.0,
        "PARKING IN A MAIN ROAD": 1.8,
        "PARKING NEAR BUSTOP/SCHOOL/HOSPITAL ETC": 1.7,
        "NO PARKING": 1.3,
        "WRONG PARKING": 1.0
    }
    try:
        if pd.isna(violation_str) or not isinstance(violation_str, str):
            return 1.0
        violations = json.loads(violation_str)
        if not violations:
            return 1.0
        return max([weights.get(v, 1.0) for v in violations])
    except:
        return 1.0

def get_primary_violation(violation_str: str) -> str:
    weights = {
        "DOUBLE PARKING": 2.0,
        "PARKING IN A MAIN ROAD": 1.8,
        "PARKING NEAR BUSTOP/SCHOOL/HOSPITAL ETC": 1.7,
        "NO PARKING": 1.3,
        "WRONG PARKING": 1.0
    }
    try:
        if pd.isna(violation_str) or not isinstance(violation_str, str):
            return "UNKNOWN"
        violations = json.loads(violation_str)
        if not violations:
            return "UNKNOWN"
        # Find the violation with max weight
        max_v = max(violations, key=lambda v: weights.get(v, 1.0))
        return max_v
    except:
        return "UNKNOWN"

def get_vehicle_impact(vehicle_type_str: str) -> float:
    if pd.isna(vehicle_type_str) or not isinstance(vehicle_type_str, str):
        return 1.5
    v_type = vehicle_type_str.upper()
    if 'TANKER' in v_type: return 3.0
    if 'LGV' in v_type: return 2.2
    if 'VAN' in v_type: return 1.8
    if 'CAR' in v_type: return 1.5
    if 'AUTO' in v_type: return 1.2
    if 'SCOOTER' in v_type or 'MOTOR CYCLE' in v_type or 'MOPED' in v_type: return 1.0
    return 1.5

# --- DYNAMIC PATH RESOLUTION FOR PRODUCTION DEPLOYMENT ---
# 1. Get the absolute path of the folder where process_csv.py lives (backend/app)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the 'backend' folder and point to the CSV file
CSV_PATH = os.path.join(CURRENT_DIR, "..", "police violation_anonymized791b166.csv")

def process_hackathon_dataset(file_path: str = CSV_PATH):
    # Read the dataset using the dynamic path instead of the hardcoded local path
    df = pd.read_csv(file_path, nrows=40000)
    
    # Parse created_datetime
    if 'created_datetime' in df.columns:
        dt_col = pd.to_datetime(df['created_datetime'], errors='coerce')
        df['hour_of_day'] = dt_col.dt.hour.fillna(-1).astype(int)
        df['day_of_week'] = dt_col.dt.dayofweek.fillna(-1).astype(int)
    else:
        df['hour_of_day'] = -1
        df['day_of_week'] = -1
    
    df['location_name'] = df['location'].fillna('Unknown Intersection').astype(str)
    df['vehicle_type'] = df['vehicle_type'].fillna('vehicle').astype(str)
    if 'violation_type' not in df.columns:
        df['violation_type'] = '[]'
        
    df['violation_severity_score'] = df['violation_type'].apply(get_violation_severity)
    df['vehicle_impact_score'] = df['vehicle_type'].apply(get_vehicle_impact)
    df['primary_violation'] = df['violation_type'].apply(get_primary_violation)
    
    # --- STEP 1: FEATURE ENGINEERING CONGESTION METRICS ---
    # Derive 'Violation Frequency' (Count of incidents per specific location point)
    location_counts = df['location_name'].value_counts().to_dict()
    df['violation_frequency'] = df['location_name'].map(location_counts)
    
    # Map a dynamic synthetic traffic density factor based on geographic occurrence frequencies
    # High recurring violations indicate severe curb-side lanes blockage
    df['traffic_density_vpm'] = (df['violation_frequency'] * 1.5).clip(15, 95)
    df['queue_length_meters'] = (df['violation_frequency'] * 4.2).clip(10, 250)
    df['lane_blockage_percent'] = np.where(df['vehicle_type'].str.lower().isin(['bus', 'truck']), 65.0, 35.0)

    # --- STEP 2: CALCULATE PHASE 3 CONGESTION SCORE ---
    # Formula matching pitch layout: 0.4*Density + 0.3*Queue + 0.3*Blockage
    df['base_congestion_score'] = (0.4 * df['traffic_density_vpm']) + \
                             (0.3 * (df['queue_length_meters'] * 0.2)) + \
                             (0.3 * df['lane_blockage_percent'])
    df['congestion_score'] = df['base_congestion_score'].clip(0, 100).round(1)

    # --- ENHANCED CONGESTION FORMULA ---
    df['enhanced_congestion_score'] = (0.7 * df['base_congestion_score']) + \
                                      (15 * df['violation_severity_score']) + \
                                      (5 * df['vehicle_impact_score'])
    df['enhanced_congestion_score'] = df['enhanced_congestion_score'].clip(0, 100).round(1)

    # --- STEP 3: SPATIAL HOTSPOT IDENTIFICATION (PHASE 4 DBSCAN) ---
    # EPS = ~300m radius cluster bounds for localized street blocks.
    # Haversine metric requires epsilon in radians (distance in km / Earth radius in km)
    coords = df[['latitude', 'longitude']].dropna().values
    if len(coords) > 0:
        coords_radians = np.radians(coords)
        eps_radians = 0.3 / 6371.0
        db = DBSCAN(eps=eps_radians, min_samples=3, metric='haversine', algorithm='ball_tree').fit(coords_radians)
        # Assign clusters mapping safely back onto matching index frames
        df.loc[df[['latitude', 'longitude']].dropna().index, 'hotspot_cluster_id'] = db.labels_
    else:
        df['hotspot_cluster_id'] = -1
    df['hotspot_cluster_id'] = df['hotspot_cluster_id'].fillna(-1).astype(int)

    # --- STEP 4: PHASE 6 ENFORCEMENT PRIORITY ENGINE ---
    # Score combines spatial congestion impact with local infraction frequency weight
    # Uses enhanced_congestion_score instead of basic congestion_score
    df['priority_score'] = (0.6 * df['enhanced_congestion_score']) + (0.4 * df['violation_frequency'].clip(0, 100))
    df['priority_score'] = df['priority_score'].round(1)
    
    return df

def calculate_junction_risks(df: pd.DataFrame):
    # 1. Remove invalid junctions
    invalid = [None, "", "No Junction", "Unknown", "NaN", "nan"]
    if 'location_name' not in df.columns:
        return []
        
    mask = df['location_name'].isna() | df['location_name'].isin(invalid) | (df['location_name'].str.strip() == "")
    jdf = df[~mask].copy()
    if jdf.empty: return []

    if 'validation_status' not in jdf.columns:
        jdf['validation_status'] = np.nan

    jdf['is_approved'] = (jdf['validation_status'] == 'approved').astype(int)
    jdf['is_rejected'] = (jdf['validation_status'] == 'rejected').astype(int)

    # 2. Group by junction_name
    grouped = jdf.groupby('location_name').agg(
        total_violations=('id', 'count') if 'id' in jdf.columns else ('location_name', 'size'),
        avg_enhanced_congestion=('enhanced_congestion_score', 'mean'),
        approved_count=('is_approved', 'sum'),
        rejected_count=('is_rejected', 'sum')
    ).reset_index()

    # 3. Calculate approval rate
    def calc_approval(row):
        total_validations = row['approved_count'] + row['rejected_count']
        if total_validations == 0:
            return 1.0
        return row['approved_count'] / total_validations

    grouped['approval_rate'] = grouped.apply(calc_approval, axis=1)

    # 4. Calculate risk score
    grouped['risk_score'] = grouped['avg_enhanced_congestion'] * np.log1p(grouped['total_violations']) * grouped['approval_rate']

    # 5. Sort descending
    grouped = grouped.sort_values(by='risk_score', ascending=False)

    # 6. Assign risk tiers
    if len(grouped) > 0:
        p90 = grouped['risk_score'].quantile(0.90)
        p75 = grouped['risk_score'].quantile(0.75)
        p50 = grouped['risk_score'].quantile(0.50)
    else:
        p90 = p75 = p50 = 0

    def get_tier(score):
        if score >= p90: return 'Critical'
        if score >= p75: return 'High'
        if score >= p50: return 'Medium'
        return 'Low'

    grouped['risk_tier'] = grouped['risk_score'].apply(get_tier)

    # 7. Generate recommended actions
    actions = {
        'Critical': 'Immediate Enforcement',
        'High': 'Increased Patrol',
        'Medium': 'Monitoring',
        'Low': 'Routine Observation'
    }
    grouped['recommended_action'] = grouped['risk_tier'].map(actions)

    # Format output
    top_20 = grouped.copy()
    
    result = []
    for _, row in top_20.iterrows():
        result.append({
            "junction_name": row['location_name'],
            "total_violations": int(row['total_violations']),
            "avg_congestion": round(float(row['avg_enhanced_congestion']), 1),
            "approval_rate": round(float(row['approval_rate']), 2),
            "risk_score": round(float(row['risk_score']), 1),
            "risk_tier": row['risk_tier'],
            "recommended_action": row['recommended_action']
        })
    
    return result

def calculate_forecasted_hotspots(df: pd.DataFrame, hours_ahead: int):
    # 1. Calculate target time
    now = datetime.now()
    target_time = now + timedelta(hours=hours_ahead)
    target_hour = target_time.hour
    target_day = target_time.weekday()

    # 2. Filter invalid junctions
    invalid = [None, "", "No Junction", "Unknown", "NaN", "nan"]
    if 'location_name' not in df.columns or 'hour_of_day' not in df.columns: return []
    mask = df['location_name'].isna() | df['location_name'].isin(invalid) | (df['location_name'].str.strip() == "")
    jdf = df[~mask].copy()
    if jdf.empty: return []

    # 3. Filter for historical target day and hour
    target_df = jdf[(jdf['day_of_week'] == target_day) & (jdf['hour_of_day'] == target_hour)]
    
    # Group by junction
    grouped = target_df.groupby('location_name').agg(
        total_violations_historical=('id', 'count') if 'id' in target_df.columns else ('location_name', 'size'),
        avg_congestion=('enhanced_congestion_score', 'mean')
    ).reset_index()

    if grouped.empty:
        return []

    # Number of unique dates for this day_of_week to calculate hourly average
    if 'created_datetime' in jdf.columns:
        dt_col = pd.to_datetime(jdf['created_datetime'], errors='coerce')
        unique_dates = dt_col[jdf['day_of_week'] == target_day].dt.date.nunique()
    else:
        unique_dates = 1
        
    unique_dates = max(1, unique_dates)

    grouped['expected_violation_volume'] = grouped['total_violations_historical'] / unique_dates
    grouped['expected_congestion'] = grouped['avg_congestion'].fillna(0)

    # Normalize volume to 0-100 for score calculation
    max_vol = grouped['expected_violation_volume'].max()
    if max_vol > 0:
        vol_normalized = (grouped['expected_violation_volume'] / max_vol) * 100
    else:
        vol_normalized = 0

    # 4. Forecast Score
    grouped['forecast_score'] = (vol_normalized * 0.5) + (grouped['expected_congestion'] * 0.5)
    grouped['forecast_score'] = grouped['forecast_score'].clip(0, 100)

    # 5. Confidence Score
    grouped['confidence_score'] = (grouped['total_violations_historical'] * 5).clip(0, 100)

    # Sort
    grouped = grouped.sort_values(by='forecast_score', ascending=False)

    # 6. Risk Tiers
    if len(grouped) > 0:
        p90 = grouped['forecast_score'].quantile(0.90)
        p75 = grouped['forecast_score'].quantile(0.75)
        p50 = grouped['forecast_score'].quantile(0.50)
    else:
        p90 = p75 = p50 = 0

    def get_tier(score):
        if score >= p90: return 'Critical'
        if score >= p75: return 'High'
        if score >= p50: return 'Medium'
        return 'Low'

    grouped['predicted_risk_tier'] = grouped['forecast_score'].apply(get_tier)

    # Format return
    top_20 = grouped.copy()
    result = []
    for _, row in top_20.iterrows():
        result.append({
            "junction_name": row['location_name'],
            "forecast_score": round(float(row['forecast_score']), 1),
            "confidence_score": round(float(row['confidence_score']), 1),
            "expected_congestion": round(float(row['expected_congestion']), 1),
            "expected_violation_volume": round(float(row['expected_violation_volume']), 1),
            "predicted_risk_tier": row['predicted_risk_tier']
        })
    return result

def calculate_hotspot_lifecycle(df: pd.DataFrame):
    invalid = [None, "", "No Junction", "Unknown", "NaN", "nan"]
    if 'location_name' not in df.columns or 'created_datetime' not in df.columns: return []
    mask = df['location_name'].isna() | df['location_name'].isin(invalid) | (df['location_name'].str.strip() == "")
    jdf = df[~mask].copy()
    if jdf.empty: return []

    jdf['dt'] = pd.to_datetime(jdf['created_datetime'], errors='coerce')
    jdf = jdf.dropna(subset=['dt'])
    if jdf.empty: return []
    
    # Split dataset temporally to find recent vs older trends
    max_date = jdf['dt'].max()
    mid_date = max_date - pd.Timedelta(days=30) # compare last 30 days vs before
    
    jdf['is_recent'] = jdf['dt'] >= mid_date
    jdf['year_week'] = jdf['dt'].dt.strftime('%Y-%U')

    grouped = jdf.groupby('location_name').agg(
        total_violations=('id', 'count') if 'id' in jdf.columns else ('location_name', 'size'),
        avg_congestion=('enhanced_congestion_score', 'mean'),
        active_weeks=('year_week', 'nunique'),
        recent_violations=('is_recent', 'sum')
    ).reset_index()

    grouped['old_violations'] = grouped['total_violations'] - grouped['recent_violations']
    
    # Deterministic trend direction
    def get_trend(row):
        if row['recent_violations'] > row['old_violations'] * 0.4:
            return 'Increasing'
        elif row['recent_violations'] < row['old_violations'] * 0.1:
            return 'Decreasing'
        return 'Stable'
    
    grouped['trend_direction'] = grouped.apply(get_trend, axis=1)

    # Deterministic explainable risk score
    grouped['risk_score'] = grouped['avg_congestion'] * np.log1p(grouped['total_violations'])
    
    # Lifecycle Classification
    p90 = grouped['risk_score'].quantile(0.90) if len(grouped) > 0 else 0
    
    def get_stage(row):
        if row['risk_score'] >= p90:
            return 'Critical'
        if row['trend_direction'] == 'Increasing':
            if row['active_weeks'] <= 4:
                return 'Emerging'
            return 'Growing'
        return 'Persistent'
        
    grouped['lifecycle_stage'] = grouped.apply(get_stage, axis=1)
    
    grouped = grouped.sort_values(by='risk_score', ascending=False)
    
    top_20 = grouped.copy()
    result = []
    for _, row in top_20.iterrows():
        result.append({
            "junction_name": row['location_name'],
            "lifecycle_stage": row['lifecycle_stage'],
            "risk_score": int(row['risk_score']),
            "trend_direction": row['trend_direction'],
            "total_violations": int(row['total_violations']),
            "active_weeks": int(row['active_weeks'])
        })
        
    return result

# Helper to calculate modeled violation duration (in minutes)
def calculate_modeled_duration(vehicle_type: str, violation_type: str) -> float:
    veh = str(vehicle_type).upper()
    viol = str(violation_type).upper()
    
    # Base duration by vehicle size
    if 'TRUCK' in veh or 'BUS' in veh:
        base = 60.0
    elif 'CAR' in veh or 'VAN' in veh:
        base = 30.0
    else: # AUTO, SCOOTER
        base = 12.0
        
    # Multiplier by violation severity
    if 'MAIN ROAD' in viol or 'DOUBLE' in viol:
        mult = 1.5
    elif 'BUSOP' in viol or 'SCHOOL' in viol or 'HOSPITAL' in viol:
        mult = 1.3
    elif 'NO PARKING' in viol:
        mult = 1.1
    else:
        mult = 1.0
        
    return base * mult

# Helper to get time-of-day weight
def calculate_tod_weight(hour: int) -> float:
    if hour < 0:
        return 1.0
    # Peak congestion hours: 8-10 AM, 5-7 PM (17:00-19:00)
    if (8 <= hour <= 10) or (17 <= hour <= 19):
        return 1.5
    elif (10 < hour < 17):
        return 1.2
    elif (19 < hour <= 22):
        return 0.9
    else:
        return 0.6

def generate_enforcement_recommendations(df: pd.DataFrame):
    grouped = df.groupby('location_name')
    raw_recommendations = []
    current_hour = datetime.now().hour
    tod_weight = calculate_tod_weight(current_hour)
    
    for loc_name, group in grouped:
        if not loc_name or loc_name in ["", "No Junction", "Unknown", "NaN", "nan"]:
            continue
            
        # 1. Congestion Impact: Average enhanced congestion score
        congestion_impact = float(group['enhanced_congestion_score'].mean())
        
        # 2. Violation Duration: Modeled average duration
        group_durations = group.apply(lambda r: calculate_modeled_duration(r['vehicle_type'], r['violation_type']), axis=1)
        avg_duration = float(group_durations.mean())
        
        # 3. Recurrence Frequency: Count of violations at this location
        recurrence_frequency = int(len(group))
        
        # Calculate raw score
        raw_score = congestion_impact * avg_duration * recurrence_frequency * tod_weight
        
        # Determine the historical peak hour for proactive patrol prediction
        if 'hour_of_day' in group.columns:
            hour_counts = group[group['hour_of_day'] >= 0]['hour_of_day'].value_counts()
            if not hour_counts.empty:
                peak_hour = int(hour_counts.index[0])
            else:
                peak_hour = 17 # default to evening rush hour
        else:
            peak_hour = 17
            
        # Proactive patrol dispatch time (15 mins before peak hour)
        patrol_time_hour = peak_hour - 1 if peak_hour > 0 else 23
        patrol_time = f"{patrol_time_hour:02d}:45"
        proactive_patrol_str = f"Deploy patrol at {patrol_time} today (expected reactivation at {peak_hour:02d}:00)."
        
        raw_recommendations.append({
            "junction_name": loc_name,
            "congestion_impact": round(congestion_impact, 1),
            "avg_duration_mins": round(avg_duration, 1),
            "recurrence_frequency": recurrence_frequency,
            "tod_weight": tod_weight,
            "raw_score": raw_score,
            "peak_hour": peak_hour,
            "proactive_patrol": proactive_patrol_str
        })
        
    if not raw_recommendations:
        return []
        
    # Normalize raw score to 0-100 range
    max_raw_score = max(r['raw_score'] for r in raw_recommendations)
    if max_raw_score == 0:
        max_raw_score = 1.0
        
    recommendations = []
    for r in raw_recommendations:
        priority_val = int(round((r['raw_score'] / max_raw_score) * 100))
        
        # Determine priority levels (1 to 4)
        if priority_val >= 80:
            action = "Proactive Towing & Fine"
            priority_level = 1
            risk_tier = "Critical"
        elif priority_val >= 50:
            action = "Proactive Patrol Dispatch"
            priority_level = 2
            risk_tier = "High"
        elif priority_val >= 25:
            action = "Scheduled Patrol Check"
            priority_level = 3
            risk_tier = "Medium"
        else:
            action = "Routine Video Monitoring"
            priority_level = 4
            risk_tier = "Low"
            
        # Build explainable reasoning string detailing the formula components
        reason = (
            f"Score components: Congestion Impact ({r['congestion_impact']}) × Duration ({r['avg_duration_mins']}m) "
            f"× Freq ({r['recurrence_frequency']}) × TOD wt ({r['tod_weight']}). {r['proactive_patrol']}"
        )
        
        recommendations.append({
            "junction_name": r['junction_name'],
            "risk_tier": risk_tier,
            "forecast_score": priority_val,
            "lifecycle_stage": "Active" if priority_level <= 2 else "Stable",
            "recommended_action": action,
            "priority_level": priority_level,
            "reason": reason
        })
        
    # Sort recommendations by priority score (forecast_score) descending
    recommendations = sorted(recommendations, key=lambda x: x['forecast_score'], reverse=True)
    
    # Re-map priority_level from 1 to N based on ranked order
    for idx, rec in enumerate(recommendations):
        # Top 3 are level 1, next 3 are level 2, etc., or keep priority levels based on score thresholds
        pass
        
    return recommendations