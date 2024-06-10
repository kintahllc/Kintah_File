from . states import states_all

def find_states_by_country_id(country_id):
    # Filter states by the given country_id
    matching_states = [{'id': state.get('id'), 'name': state.get('name')} 
                       for state in states_all 
                       if state.get('country_id') == country_id]
    
    return matching_states

# print(find_states_by_country_id(1))

def get_state_name(state_id):
    for state in states_all:
        if str(state.get('id')) == state_id:
            return state.get('name')
    return None

def get_state_id(state_name):
    for state in states_all:
        if state.get('name') == state_name:
            return state.get('id')
    return None