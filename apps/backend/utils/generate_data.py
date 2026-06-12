import csv
import random
import os

TYPES = ["TRUCK", "DRONE", "GENERATOR", "RADIO", "VEHICLE", "MEDEVAC", "FORKLIFT", "TRAILER"]
LOCATIONS = ["BASE_ALPHA", "BASE_BRAVO", "BASE_CHARLIE", "BASE_DELTA"]
STATUSES = ["ACTIVE", "ACTIVE", "ACTIVE", "STANDBY", "MAINTENANCE"]  # Weighted

def generate_row(index):
    asset_type = random.choice(TYPES)
    asset_id = f"{asset_type}{index:03d}"
    
    # Generate somewhat correlated stats based on type
    if asset_type in ["DRONE", "RADIO"]:
        inventory = random.randint(50, 500)
    else:
        inventory = random.randint(5, 150)
        
    usage_rate = random.randint(5, 100)
    service_days = random.randint(10, 300)
    
    # Higher service days -> higher chance of more repairs and higher temp
    base_repairs = service_days // 50
    repairs = max(0, base_repairs + random.randint(-1, 3))
    
    temperature = random.randint(30, 70) + (repairs * 2)
    
    location = random.choice(LOCATIONS)
    status = random.choice(STATUSES)
    
    # Force maintenance if repairs are very high or temperature is very high
    if repairs > 8 or temperature > 85:
        status = "MAINTENANCE"
        
    return [
        asset_id,
        asset_type,
        inventory,
        usage_rate,
        service_days,
        temperature,
        repairs,
        location,
        status
    ]

def main():
    # Go up to the project root and into data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../../.."))
    data_dir = os.path.join(project_root, "data")
    
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "assets.csv")
    
    headers = [
        "asset_id", "type", "inventory", "usage_rate", 
        "service_days", "temperature", "repairs", "location", "status"
    ]
    
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(1, 501):
            writer.writerow(generate_row(i))
            
    print(f"Successfully generated 500 rows at {output_path}")

if __name__ == "__main__":
    main()
