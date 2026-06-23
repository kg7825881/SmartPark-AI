import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

n = 5000
np.random.seed(42)

lats = 12.9716 + np.random.randn(n) * 0.05
lons = 77.5946 + np.random.randn(n) * 0.05
locations = [f"Intersection {i%100}" for i in range(n)]
vehicle_types = np.random.choice(['CAR', 'BUS', 'TRUCK', 'SCOOTER', 'AUTO'], n)

violations = ["DOUBLE PARKING", "PARKING IN A MAIN ROAD", "NO PARKING", "WRONG PARKING"]
violation_types = [json.dumps([np.random.choice(violations)]) for _ in range(n)]

dates = [datetime.now() - timedelta(days=np.random.randint(0, 30), hours=np.random.randint(0, 24)) for _ in range(n)]
dates_str = [d.strftime('%Y-%m-%d %H:%M:%S') for d in dates]

df = pd.DataFrame({
    'created_datetime': dates_str,
    'location': locations,
    'vehicle_type': vehicle_types,
    'violation_type': violation_types,
    'latitude': lats,
    'longitude': lons,
    'id': range(n)
})

df.to_csv('police violation_anonymized791b166.csv', index=False)
print("Mock CSV generated successfully.")
