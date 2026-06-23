import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.process_csv import process_hackathon_dataset, calculate_junction_risks, calculate_forecasted_hotspots, calculate_hotspot_lifecycle, generate_enforcement_recommendations
from app.video_stream import generate_camera_frames, LIVE_ALERTS
from fastapi.responses import StreamingResponse
import os

app = FastAPI(title="SmartPark AI Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CACHE DATA IN MEMORY AT STARTUP ---
print("[*] Ingesting and clustering data from CSV...")
GLOBAL_DF = process_hackathon_dataset()
print("[SUCCESS] CSV Data Processed and Cached Successfully!")

@app.get("/api/dashboard-summary")
def get_dashboard_summary():
    """
    Returns data from the pre-cached memory dataset instantly.
    """
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

    # Calculate hourly congestion trend
    hourly_trend = []
    if 'hour_of_day' in df.columns:
        counts = df[df['hour_of_day'] >= 0].groupby('hour_of_day').size().to_dict()
        for hour_val in range(24):
            hourly_trend.append({
                "hour": f"{hour_val:02d}:00",
                "violations": int(counts.get(hour_val, 0))
            })

    return {
        "metrics": {
            "total_violations": str(total_violations),
            "active_hotspots": str(unique_hotspots),
            "avg_congestion": f"{round(avg_congestion, 1)}/100",
            "enforcement_score": "88/100"
        },
        "recommendations": recommendations,
        "hourly_trend": hourly_trend
    }


@app.get("/api/heatmap-data")
def get_heatmap_data(hours_ahead: int = 0):
    """
    Returns coordinate payload for thermal heatmap engine.
    """
    df = GLOBAL_DF.dropna(subset=['latitude', 'longitude', 'congestion_score']).copy()
    
    if hours_ahead > 0:
        from datetime import datetime, timedelta
        target_time = datetime.now() + timedelta(hours=hours_ahead)
        df = df[(df['day_of_week'] == target_time.weekday()) & (df['hour_of_day'] == target_time.hour)]

    sample_size = min(5000, len(df))
    if sample_size == 0:
        return {"points": []}
    sample_df = df.sample(n=sample_size, random_state=42)
    
    points = sample_df[['latitude', 'longitude', 'congestion_score']].values.tolist()
    return {"points": points}

@app.get("/api/junctions")
def get_junction_risks():
    """
    Returns the top 20 high-risk junctions.
    """
    df = GLOBAL_DF.copy()
    junctions = calculate_junction_risks(df)
    return junctions[:20]

@app.get("/api/forecast")
def get_forecast(hours_ahead: int = 1):
    """
    Returns the predicted hotspots.
    """
    df = GLOBAL_DF.copy()
    forecasts = calculate_forecasted_hotspots(df, hours_ahead)
    return forecasts[:20]

@app.get("/api/lifecycle")
def get_lifecycle():
    """
    Returns top lifecycle-ranked junctions.
    """
    df = GLOBAL_DF.copy()
    lifecycles = calculate_hotspot_lifecycle(df)
    return lifecycles[:20]

@app.get("/api/enforcement")
def get_enforcement():
    """
    Returns actionable prioritized enforcement action recommendations.
    """
    df = GLOBAL_DF.copy()
    recommendations = generate_enforcement_recommendations(df)
    return recommendations[:20]

@app.get("/api/spatial-clusters")
def get_spatial_clusters():
    """
    Returns the DBSCAN cluster centers and metrics.
    """
    df = GLOBAL_DF.copy()
    if 'hotspot_cluster_id' not in df.columns or df.empty:
        return []
        
    cluster_groups = df[df['hotspot_cluster_id'] != -1].groupby('hotspot_cluster_id')
    
    clusters = []
    for cid, group in cluster_groups:
        group_valid = group.dropna(subset=['latitude', 'longitude'])
        if group_valid.empty:
            continue
            
        lat_mean = float(group_valid['latitude'].mean())
        lng_mean = float(group_valid['longitude'].mean())
        size = int(len(group_valid))
        avg_congestion = float(group_valid['congestion_score'].mean())
        avg_priority = float(group_valid['priority_score'].mean())
        
        top_locations = group_valid['location_name'].value_counts().index[:2].tolist()
        location_desc = " & ".join(top_locations) if top_locations else "Unknown Location"
        
        clusters.append({
            "cluster_id": int(cid),
            "latitude": lat_mean,
            "longitude": lng_mean,
            "size": size,
            "avg_congestion": round(avg_congestion, 1),
            "avg_priority": round(avg_priority, 1),
            "location": location_desc
        })
        
    clusters = sorted(clusters, key=lambda x: x['size'], reverse=True)
    return clusters

@app.get("/api/video-feed/{cam_id}")
def get_video_feed(cam_id: int):
    """
    Streaming video feed endpoint. Returns live frames from processed MP4 video or synthetic traffic cam.
    """
    if cam_id not in [1, 2, 3, 4]:
        cam_id = 1
    return StreamingResponse(
        generate_camera_frames(cam_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/api/live-alerts")
def get_live_alerts():
    """
    Returns the latest live violations detected from the running video streams.
    """
    return {"logs": LIVE_ALERTS}