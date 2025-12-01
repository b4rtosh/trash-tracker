from geopy.geocoders import Nominatim


def get_coordinates(city, street_address):
    loc = Nominatim(user_agent="Geopy Library")
    try:
        getLoc = loc.geocode(f"{city}, {street_address}")
        print(getLoc.address)
        return {
            "latitude": round(getLoc.latitude, 6),
            "longitude": round(getLoc.longitude, 6),
        }
    except Exception as e:
        print(f"Error: {e}")
        return None
