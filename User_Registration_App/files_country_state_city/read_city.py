

import os

def read_state_file(state_id):
    # Get the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the folder path
    folder_name = "all_cities_file_separate_with_state_id"
    folder_path = os.path.join(current_directory, folder_name)

    # Construct the file path
    file_name = f"state_id_{state_id}.py"
    file_path = os.path.join(folder_path, file_name)

    # Check if the file exists
    if not os.path.exists(file_path):
        return None

    # Read and execute the file
    with open(file_path, 'r') as f:
        file_contents = f.read()

    # Execute the file contents
    globals_dict = {}
    exec(file_contents, globals_dict)

    # Access the 'all' variable which contains the city data
    cities = globals_dict.get('all', [])

    # Extract names from city dictionaries
    city_names = [city.get('name') for city in cities]
    print(city_names)

    return city_names

# print("a")
# read_state_file(1)


def get_city_name(city_id, state_id):
    # Get the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the folder path
    folder_name = "all_cities_file_separate_with_state_id"
    folder_path = os.path.join(current_directory, folder_name)

    # Construct the file path
    file_name = f"state_id_{state_id}.py"
    file_path = os.path.join(folder_path, file_name)

    # Check if the file exists
    if not os.path.exists(file_path):
        return None

    # Read and execute the file
    with open(file_path, 'r') as f:
        file_contents = f.read()

    # Execute the file contents
    globals_dict = {}
    exec(file_contents, globals_dict)

    # Access the 'all' variable which contains the city data
    cities = globals_dict.get('all', [])

    # Search for the city with the given ID and return its name
    for city in cities:
        if str(city.get('id')) == city_id:
            k=9
            return city.get('name')
    e=3
    return None
