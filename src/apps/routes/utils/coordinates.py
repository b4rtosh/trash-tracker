from geopy.geocoders import Nominatim

def get_coordinates(city, street_address):
    loc = Nominatim(user_agent="Geopy Library")
    
    getLoc = loc.geocode(f"{city}, {street_address}")
    print(getLoc.address)
    return {getLoc.latitude, getLoc.longitude}