import csv
import os

def create_showcase_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../.."))
    data_dir = os.path.join(project_root, "data")
    
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "t3_usecase_demo.csv")
    
    headers = [
        "asset_id", "type", "inventory", "usage_rate", 
        "service_days", "temperature", "repairs", "location", "status"
    ]
    
    # We craft highly specific rows that trigger the ML Agents to take drastic actions,
    # showcasing Terminal3's ability to authorize high-stakes autonomous AI decisions.
    rows = [
        # 1. THE ANOMALY (Risk Agent -> Freeze -> Terminal 3 Auth)
        # A DRONE with extremely abnormal stats: low service days, but massive usage and insane temperature.
        # This will trigger the Isolation Forest Risk Model.
        ["DRONE_X99_ANOMALY", "DRONE", 450, 100, 2, 120, 0, "BASE_ALPHA", "ACTIVE"],
        
        # 2. THE CRITICAL FAILURE (Maintenance Agent -> Schedule Maintenance -> Terminal 3 Auth)
        # A GENERATOR that is basically melting down. High repairs, huge temp.
        # This will trigger the XGBoost Maintenance Model.
        ["GEN_FAIL_CRITICAL", "GENERATOR", 20, 95, 400, 98, 12, "BASE_DELTA", "MAINTENANCE"],
        
        # 3. THE DEPLETED CRITICAL ASSET (Inventory Agent -> Restock -> Terminal 3 Auth)
        # A MEDEVAC unit that is out of critical inventory but has very high usage.
        # This triggers the LightGBM Inventory Model.
        ["MEDEVAC_EMPTY", "MEDEVAC", 0, 90, 50, 45, 1, "BASE_CHARLIE", "ACTIVE"],
        
        # 4. NORMAL ASSETS (No Action Needed)
        # To show contrast, regular assets that the AI will leave alone.
        ["TRUCK_NORMAL_01", "TRUCK", 85, 30, 100, 50, 2, "BASE_BRAVO", "ACTIVE"],
        ["RADIO_NORMAL_02", "RADIO", 300, 15, 200, 40, 0, "BASE_ALPHA", "STANDBY"],
        ["FORKLIFT_NORM_03", "FORKLIFT", 40, 50, 80, 55, 1, "BASE_DELTA", "ACTIVE"],
        
        # 5. ANOTHER RISK CASE
        # A VEHICLE with negative correlations (high repairs but brand new).
        ["VEHICLE_RISK_88", "VEHICLE", 100, 85, 5, 88, 8, "BASE_CHARLIE", "ACTIVE"],
    ]
    
    # Add some filler data so the UI doesn't look empty
    import random
    types = ["TRUCK", "TRAILER", "VEHICLE"]
    locs = ["BASE_ALPHA", "BASE_BRAVO"]
    for i in range(10, 50):
        rows.append([
            f"ASSET_FILLER_{i}",
            random.choice(types),
            random.randint(50, 100),
            random.randint(10, 40),
            random.randint(50, 150),
            random.randint(30, 60),
            random.randint(0, 3),
            random.choice(locs),
            "ACTIVE"
        ])
    
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
            
    print(f"Created Terminal 3 Showcase Data at: {output_path}")

if __name__ == "__main__":
    create_showcase_data()
