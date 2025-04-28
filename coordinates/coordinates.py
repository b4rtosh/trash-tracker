from geopy.geocoders import Nominatim

loc = Nominatim(user_agent="Geopy Library")


getLoc = loc.geocode("Wrocław, Drukarska 13")

print(getLoc.address)

print("Latitude = ", getLoc.latitude, "\n")
print("Longitude = ", getLoc.longitude)