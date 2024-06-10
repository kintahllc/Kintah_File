import os

# Load the city data
from cities_1 import all as cities_data

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Create a dictionary to store cities by state_id
cities_by_state = {}

# Group cities by state_id
for city in cities_data:
    state_id = city['state_id']
    if state_id not in cities_by_state:
        cities_by_state[state_id] = []
    cities_by_state[state_id].append(city)

# Create separate files for each state_id
for state_id, cities in cities_by_state.items():
    file_name = f"state_id_{state_id}.py"
    file_path = os.path.join(current_directory, file_name)
    with open(file_path, 'w') as f:
        f.write("all = [\n")
        for city in cities:
            f.write(f"{city},\n")
        f.write("]\n")

    print(f"Created file: {file_name} in folder: {current_directory}")

