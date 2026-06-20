import os
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

# --- DYNAMIC PATH RESOLUTION FOR PRODUCTION DEPLOYMENT ---
# 1. Get the absolute path of the folder where process_csv.py lives (backend/app)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the 'backend' folder and point to the CSV file
CSV_PATH = os.path.join(CURRENT_DIR, "..", "police violation_anonymized791b166.csv")

def process_hackathon_dataset(file_path: str = CSV_PATH):
    # Read the dataset using the dynamic path instead of the hardcoded local path
    df = pd.read_csv(file_path, nrows=40000)
    
    # Clean string columns for safety
    df['location_name'] = df['location'].fillna('Unknown Intersection').astype(str)
    df['vehicle_type'] = df['vehicle_type'].fillna('vehicle').astype(str)
    
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
    df['congestion_score'] = (0.4 * df['traffic_density_vpm']) + \
                             (0.3 * (df['queue_length_meters'] * 0.2)) + \
                             (0.3 * df['lane_blockage_percent'])
    df['congestion_score'] = df['congestion_score'].clip(0, 100).round(1)

    # --- STEP 3: SPATIAL HOTSPOT IDENTIFICATION (PHASE 4 DBSCAN) ---
    # EPS = 0.003 (~300m radius cluster bounds for localized street blocks)
    coords = df[['latitude', 'longitude']].dropna().values
    if len(coords) > 0:
        db = DBSCAN(eps=0.003, min_samples=3, metric='euclidean').fit(coords)
        # Assign clusters mapping safely back onto matching index frames
        df.loc[df[['latitude', 'longitude']].dropna().index, 'hotspot_cluster_id'] = db.labels_
    else:
        df['hotspot_cluster_id'] = -1
    df['hotspot_cluster_id'] = df['hotspot_cluster_id'].fillna(-1).astype(int)

    # --- STEP 4: PHASE 6 ENFORCEMENT PRIORITY ENGINE ---
    # Score combines spatial congestion impact with local infraction frequency weight
    df['priority_score'] = (0.6 * df['congestion_score']) + (0.4 * df['violation_frequency'].clip(0, 100))
    df['priority_score'] = df['priority_score'].round(1)
    
    return df