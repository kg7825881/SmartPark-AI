import os
filepath = r'c:\Users\ojhav\OneDrive\Desktop\Hackathon\SmartPark-AI-main\backend\app\process_csv.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("df['junction_name']", "df['location_name']")
content = content.replace("jdf['junction_name']", "jdf['location_name']")
content = content.replace("'junction_name' not in df.columns", "'location_name' not in df.columns")
content = content.replace("groupby('junction_name')", "groupby('location_name')")
content = content.replace("('junction_name', 'size')", "('location_name', 'size')")
content = content.replace("row['junction_name']", "row['location_name']")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
