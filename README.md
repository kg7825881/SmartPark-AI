# 🚦 SmartPark AI | Gridlock Hackathon 2.0

![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-DBSCAN-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

**SmartPark AI** is a geospatial intelligence platform built to eliminate urban gridlock caused by illegal curb-side parking. By ingesting massive datasets of anonymized police traffic violations, the system uses machine learning (DBSCAN clustering) to identify severe congestion hotspots and dispatches targeted enforcement recommendations in real-time.



## 🌟 Core Features

1. **📊 Operational Dashboard**
   - Real-time time-series analysis of congestion spikes.
   - Calculates dynamic `Congestion Scores` based on traffic density, estimated queue lengths, and lane blockage percentages.
   - Outputs a prioritized hit-list of intersections for immediate tow-truck dispatch.

2. **📹 Simulated Edge-Inference (Live Monitoring)**
   - A "Control Room" interface that simulates edge-node processing.
   - Streams live, synthetic AI confidence logs identifying specific vehicle types and violation classes (e.g., *Extended Idling*, *Lane Blockage*) in real-time.

3. **🔥 Geospatial Thermal Heatmap**
   - Renders massive datasets onto a dark-mode interactive map using WebGL thermal rendering.
   - Highlights spatial clusters of illegal parking, allowing urban planners to see macro-level city density patterns at a glance.



## 🛠️ Tech Stack & Architecture

### **Frontend (Vercel)**
- **Framework:** Next.js 14 (React 18)
- **Styling:** Tailwind CSS (Custom dark-mode UI)
- **Maps:** React-Leaflet (`leaflet.heat` for thermal rendering)
- **Data Visualization:** Recharts (Time-series area graphs)

### **Backend (Render)**
- **Framework:** FastAPI (High-performance async API)
- **Data Engine:** Pandas & NumPy
- **Machine Learning:** Scikit-Learn (Unsupervised spatial clustering via DBSCAN)
- **Runtime:** Python 3.11



## 🧠 The ML Pipeline (Feature Engineering)

To transform raw CSV strings into actionable intelligence, the backend executes a 4-phase data pipeline:

1. **Frequency Mapping:** Counts recurring violations per geographic coordinate.
2. **Synthetic Feature Engineering:** Derives hidden metrics like `traffic_density_vpm` and `queue_length_meters` based on violation frequency and vehicle type (buses vs. cars).
3. **Spatial Hotspot Clustering (Phase 4):** Uses **DBSCAN** (`eps=0.003`, `min_samples=3`) to cluster localized street blocks and group scattered violations into cohesive "Hotzones."
4. **Enforcement Priority Engine:** Mathematically weights the congestion score against local infraction frequency to tell authorities exactly where to deploy units first.

*(Note: The dataset is sampled to 40,000 rows in production to safely operate within free-tier cloud memory constraints while maintaining visual density).*



## 💻 Local Setup & Development

Want to run the command center locally? 

### 1. Backend Setup
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Navigate to http://localhost:3000 to access the dashboard.

## 🚀 Live Deployment

* Frontend Dashboard: 

* Backend API Docs: 