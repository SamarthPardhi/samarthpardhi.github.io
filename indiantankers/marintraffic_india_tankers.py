import requests

def fetch_marinetraffic_data():
    # The URL from your browser's network tab
    url = "https://www.marinetraffic.com/en/reports/?asset_type=vessels&columns=flag,shipname,photo,recognized_next_port,reported_eta,reported_destination,current_port,imo,ship_type,show_on_live_map,time_of_latest_position,lat_of_latest_position,lon_of_latest_position,notes&flag_in=IN&filters_with_name_filtering=yard_number_in"

    # Headers to mimic a real browser and bypass basic bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.marinetraffic.com/en/data/?asset_type=vessels&columns=flag,shipname,photo",
        "X-Requested-With": "XMLHttpRequest", # Common for data-fetching endpoints
        "Connection": "keep-alive"
    }

    try:
        # Make the GET request
        response = requests.get(url, headers=headers, timeout=15)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Request successful! (Status Code 200)\n")
            
            # Try parsing it as JSON first (standard for data endpoints)
            try:
                data = response.json()
                print("Data format: JSON")
                # Print the first 500 characters of the stringified JSON
                print(str(data)[:500] + "...\n") 
                return data
                
            # If it's not JSON, it might just be the raw HTML page
            except requests.exceptions.JSONDecodeError:
                print("Data format: HTML/Text")
                print(response.text[:500] + "...\n")
                return response.text
                
        # If MarineTraffic blocks you, it usually throws a 403 Forbidden
        elif response.status_code == 403:
            print(f"Failed: 403 Forbidden. MarineTraffic blocked the request (likely Cloudflare or bot protection).")
        else:
            print(f"Failed with status code: {response.status_code}")
            print("Response:", response.text[:200])

    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")

# --- Execution ---
if __name__ == "__main__":
    fetch_marinetraffic_data()