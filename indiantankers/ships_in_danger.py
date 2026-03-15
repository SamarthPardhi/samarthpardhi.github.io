import json
from shapely.geometry import Point, Polygon
from danger_area import quad_coords

# The danger zone encompassing the strait of Hormouz


def extract_ships_in_quadrilateral(input_json_path, output_txt_path):
    quad_polygon = Polygon(quad_coords)
    ships_inside = []

    # Read the JSON data
    with open(input_json_path, 'r') as file:
        json_data = json.load(file)

    # Iterate through the array of ship data
    for ship in json_data.get('data', []):
        try:
            # Extract and convert coordinates to floats
            lon = float(ship['LON'])
            lat = float(ship['LAT'])
            ship_id = ship['SHIP_ID']
            
            # Create a point (Longitude, Latitude)
            point = Point(lon, lat)
            
            # Check if the point is inside the quadrilateral
            if quad_polygon.contains(point):
                ships_inside.append(ship_id)
                
        except (ValueError, KeyError, TypeError):
            # Skip this entry if LON/LAT are missing, null, or invalid
            continue

    # Save the filtered SHIP_IDs to an output text file
    with open(output_txt_path, 'w') as file:
        for sid in ships_inside:
            file.write(f"{sid}\n")

    print(f"Process complete. Found {len(ships_inside)} ships inside the quadrilateral.")
    print(f"The list of Ship IDs has been saved to: {output_txt_path}")

# --- Execution ---
# Replace 'ships_data.json' with your actual input file name
# Replace 'filtered_ships.txt' with your desired output file name
if __name__ == "__main__":
    extract_ships_in_quadrilateral('tankers_india.json', 'filtered_ships_ids.txt')