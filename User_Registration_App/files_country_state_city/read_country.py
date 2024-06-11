from . country import country_all

def search_countries_by_character(starting_char):
    # Convert the starting character to lowercase for case-insensitive search
    starting_char_lower = starting_char.lower()

    # Filter countries whose names start with the given character
    matching_countries = [{'id': country.get('id'), 'name': country.get('name')} 
                          for country in country_all 
                          if country.get('name', '').lower().startswith(starting_char_lower)]

    print(matching_countries)
    return matching_countries
    
# search_countries_by_character("a")

def get_country_name(country_id):

    for country in country_all:
        if str(country.get('id')) == country_id:

            return country.get('name')

    return None

def get_country_id_from_name(country_name):

    for country in country_all:
        if str(country.get('name')) == country_name:

            return country.get('id')

    return None
