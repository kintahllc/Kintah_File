import pandas as pd

# Sample data for fleet vehicles
data = {
    'name': ['Vehicle A', 'Vehicle B'],
    'license_plate': ['ABC123', 'DEF456'],
    'vin_sn': ['1HGCM82633A123456', '1HGCM82633A654321'],
    'driver_id': [1, 2],  # Driver ID
    'model_id': [1, 2],  # Model ID
    'odometer': [12000.5, 15000.0],
    'odometer_unit': ['km', 'km'],
    'acquisition_date': ['2022-01-01', '2023-01-01'],
    'car_value': [25000.0, 30000.0],
    'state_id': [1, 2],  # State ID
    'location': ['Garage A', 'Garage B'],
    'color': ['Red', 'Blue'],
    'seats': [5, 4],
    'doors': [4, 4],
    'transmission': ['manual', 'automatic'],
    'fuel_type': ['gasoline', 'diesel'],
    'horsepower': [150, 180],
    'horsepower_tax': [200.0, 250.0],
    'power': [110.0, 130.0],
    'co2': [120.0, 140.0],
    'notes': ['Vehicle in good condition', 'New vehicle'],
    'active': [True, True],
    'company_id': [1, 1],  # Company ID
    'website_id': [1, 1],  # Website ID
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
file_path = '/home/sohel/Downloads/additional ERP configuration automation to add (1)/fleet_data.csv'
df.to_csv(file_path, index=False)

print(f"CSV file saved to {file_path}")
