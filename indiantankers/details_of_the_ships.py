import json
import csv

def process_ship_attributes(json_filepath, ids_filepath, output_csv, attributes):
    """
    Reads target SHIP_IDs, extracts specified attributes from the JSON,
    saves them to a CSV, and pretty-prints them to the terminal.
    """
    # 1. Read the target SHIP_IDs from the text file into a set for fast lookup
    try:
        with open(ids_filepath, 'r') as f:
            target_ids = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        print(f"Error: Could not find the ID file '{ids_filepath}'.")
        return

    # 2. Read the JSON data
    try:
        with open(json_filepath, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find the JSON file '{json_filepath}'.")
        return

    # 3. Extract the requested attributes for the matching ships
    extracted_data = []
    for ship in json_data.get('data', []):
        if ship.get('SHIP_ID') in target_ids:
            # Build a dictionary for this ship, defaulting to "N/A" if an attribute is missing
            ship_row = {attr: str(ship.get(attr) or "N/A") for attr in attributes}
            extracted_data.append(ship_row)

    if not extracted_data:
        print("No matching ships found for the provided IDs.")
        return

    # 4. Write the extracted data to a CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=attributes)
        writer.writeheader()
        writer.writerows(extracted_data)

    # 5. Pretty Print to the Terminal
    # Calculate the maximum width for each column to align the text properly
    col_widths = {
        attr: max(len(attr), max((len(row[attr]) for row in extracted_data), default=0)) 
        for attr in attributes
    }
    
    # Create a dynamic formatting string (e.g., "{:<15} | {:<20} | {:<10}")
    format_str = " | ".join([f"{{:<{col_widths[attr]}}}" for attr in attributes])
    separator_length = sum(col_widths.values()) + (len(attributes) - 1) * 3
    
    # Print the table
    print("\n" + "=" * separator_length)
    print(format_str.format(*attributes))
    print("-" * separator_length)
    
    for row in extracted_data:
        print(format_str.format(*[row[attr] for attr in attributes]))
    
    print("=" * separator_length)
    print(f"\nSuccess! Saved {len(extracted_data)} records to '{output_csv}'.")

# --- Execution ---
if __name__ == "__main__":
    # Define the files
    input_json = 'tankers_india.json'
    input_ids = 'filtered_ships_ids.txt'
    output_csv = 'ship_details.csv'
    
    # Define the exact attributes you want to pull from the JSON
    # You can add or remove attributes in this list as needed
    desired_attributes = [
        'SHIP_ID',
        'SHIPNAME',
        'COUNTRY', 
        'COUNT_PHOTOS', 
        'DESTINATION', 
        'LAST_POS',
        'TIMEZONE',
        'LON',
        'LAT',
        'SPEED',
    ]
    
    process_ship_attributes(input_json, input_ids, output_csv, desired_attributes)