# %%
from geopy.geocoders import Nominatim
import folium
import json
import re

current_season = '2025_winter'

json_file_path = f"{current_season}_all_restaurants.json"

# Load dictionary from file or create an empty one
def load_dict(file_path = json_file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

geolocator = Nominatim(user_agent="geo_mapper")

# %%
ordinal_map = {
    "First": "1st", "Second": "2nd", "Third": "3rd", "Fourth": "4th",
    "Fifth": "5th", "Sixth": "6th", "Seventh": "7th", "Eighth": "8th",
    "Ninth": "9th", "Tenth": "10th", "Eleventh": "11th", "Twelfth": "12th",
    "Thirteenth": "13th", "Fourteenth": "14th", "Fifteenth": "15th",
    "Sixteenth": "16th", "Seventeenth": "17th", "Eighteenth": "18th",
    "Nineteenth": "19th", "Twentieth": "20th",  # Add more as needed
}

def convert_word_to_number(address):
    # Convert word-based ordinals to digits
    for word, number in ordinal_map.items():
        address = re.sub(r'\b' + re.escape(word) + r'\b', number, address, flags=re.IGNORECASE)
    return address

def clean_address(address):
    # Regex to remove floor information
    address = re.sub(r'(?<=\s)\d+(?:st|nd|rd|th)?\s*fl\.?', '', address, flags=re.IGNORECASE)
    # Clean up extra spaces
    return (convert_word_to_number(re.sub(r'\s+', ' ', address).strip()))

def create_restaurant_week_map(locations, save_location):
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)  # Center on NYC by default

    # Add markers for each address
    for lat, lon, restaurant in locations:
        popup_deals = '</li><li>'.join(restaurant['deals'])
        popup_content = f"""
        <div style="font-family: Arial, sans-serif;">
            <h4 style="margin: 0;">
                <a href="{restaurant['restaurant_url']}" target="_blank" style="text-decoration: none; color: #007BFF;">
                    <b>{restaurant['restaurant_name']}</b>
                </a>
            </h4>
            <p style="margin-top: 5px; margin-bottom: 5px;">
                {restaurant['restaurant_description']}
            </p>
            <ul>
                <li>
                    <a href="{restaurant['restaurant_week_url']}" target="_blank" style="text-decoration: none; color: #007BFF;">{popup_deals}</a>
                </li>
            </ul>
        </div>
        """
        tooltip_content = f"{restaurant['restaurant_name']}"
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_content, max_width=300),  # Custom popup
            tooltip=tooltip_content  # Custom tooltip
        ).add_to(m)

    # Save the map as an HTML file
    m.save(save_location)

    print(f"Map created and saved as '{save_location}'")
# %%
all_restaurants = []
cant_find = []

total_restaurants = len(load_dict().keys())
num = 0

for restaurant in load_dict():
    num += 1
    t_rest = load_dict()[restaurant]
    try:
        t_cord = geolocator.geocode(
            clean_address(
                t_rest['restaurant_address']
            )
        )
        all_restaurants.append(
            [
                t_cord.latitude,
                t_cord.longitude,
                t_rest
            ]
        )
        print(f"{num}/{total_restaurants}\tFound:\t'{restaurant}'")
    except:
        print(f"{num}/{total_restaurants}\tError:\t'{restaurant}'")
        cant_find.append(t_rest)

# %%
# Create an interactive map of all restaurants
create_restaurant_week_map(
    all_restaurants,
    "maps/all_restaurants_map.html"
)

# %%
# Create a map of 30$ Dinners only
dinner_30 = []
for restaurant in all_restaurants:
    if ('$ 30 Dinner' in restaurant[2]['deals']) or ('$ 30 Sunday Dinner' in restaurant[2]['deals']) or ('$ 45 Dinner' in restaurant[2]['deals']):
        dinner_30.append(restaurant)

create_restaurant_week_map(
    dinner_30,
    "maps/all_cheap_dinners.html"
)

#  %%
# Create a map of 30$ Dinners only
steaks = []
for restaurant in all_restaurants:
    if 'steak' in restaurant[2]['restaurant_description'].casefold():
        steaks.append(restaurant)

create_restaurant_week_map(
    steaks,
    "maps/all_steaks.html"
)

# %%
deals = []
for e in all_restaurants:
    deals += e[2]['deals']
set(deals)
# %%
