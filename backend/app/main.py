# backend/app/main.py
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.process_csv import process_hackathon_dataset
import os

app = FastAPI(title="SmartPark AI Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_PATH = "/Users/sumitk.gupta/Documents/smartpark-ai/police violation_anonymized791b166.csv"

# --- CACHE DATA IN MEMORY AT STARTUP ---
print("⚙️ Ingesting and clustering data from CSV...")
GLOBAL_DF = process_hackathon_dataset(CSV_PATH)
print("✅ CSV Data Processed and Cached Successfully!")

@app.get("/api/dashboard-summary")
def get_dashboard_summary():
    """
    Returns data from the pre-cached memory dataset instantly.
    """
    # Use global data instead of re-reading the heavy CSV on every call
    df = GLOBAL_DF.copy()
    
    total_violations = len(df)
    unique_hotspots = int(df['hotspot_cluster_id'].nunique() - (1 if -1 in df['hotspot_cluster_id'].values else 0))
    avg_congestion = float(df['congestion_score'].mean())
    
    top_records = df.sort_values(by='priority_score', ascending=False).head(10)
    top_records = top_records.replace({np.nan: None})
    
    recommendations = []
    for _, row in top_records.iterrows():
        score = row['congestion_score']
        status = "Severe" if score > 80 else "High" if score > 50 else "Moderate"
        
        recommendations.append({
            "location": row.get('location_name', 'Unknown Intersect Zone'),
            "congestion_score": round(score, 1),
            "priority_score": round(row['priority_score'], 1),
            "status": status,
            "latitude": row['latitude'],
            "longitude": row['longitude']
        })

    return {
        "metrics": {
            "total_violations": str(total_violations),
            "active_hotspots": str(unique_hotspots),
            "avg_congestion": f"{round(avg_congestion, 1)}/100",
            "enforcement_score": "88/100"
        },
        "recommendations": recommendations
    }

# Add this below your existing get_dashboard_summary() endpoint

@app.get("/api/heatmap-data")
def get_heatmap_data():
    """
    Returns a massive payload of coordinates for the frontend thermal engine.
    """
    df = GLOBAL_DF.dropna(subset=['latitude', 'longitude', 'congestion_score']).copy()
    
    # We sample 5000 points to keep the frontend super snappy during the live demo
    # while still creating a visually dense and stunning heatmap
    sample_size = min(5000, len(df))
    sample_df = df.sample(n=sample_size, random_state=42)
    
    # leaflet.heat requires format: [lat, lng, intensity]
    # We use congestion_score as the intensity weight!
    points = sample_df[['latitude', 'longitude', 'congestion_score']].values.tolist()
    
    return {"points": points}