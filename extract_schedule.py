import requests
from bs4 import BeautifulSoup
import pandas as pd
import html
import re
from io import StringIO
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json

def extract_schedule():
    url = "https://iitj.ac.in/health-center/en/doctors-schedule"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Find the iframe containing the schedule
    iframe = soup.find('iframe')
    if not iframe:
        print("No iframe found on the page.")
        return

    src = iframe.get('src')
    if not src:
        print("Iframe has no src attribute.")
        return

    # 2. Clean up the iframe URL
    clean_src = html.unescape(src)
    
    # Parse URL to rebuild it cleanly
    parsed = urlparse(clean_src)
    qs = parse_qs(parsed.query)
    
    # Keep only gid if present, as it identifies the spreadsheet/sheet
    clean_qs = {}
    if 'gid' in qs:
        clean_qs['gid'] = qs['gid'][0]
    
    new_query = urlencode(clean_qs)
    clean_src = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    
    print(f"Found Iframe source: {clean_src}")

    # 3. Fetch the iframe content (Google Sheets published HTML)
    try:
        iframe_resp = requests.get(clean_src)
        iframe_resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching iframe: {e}")
        return

    # 4. Extract individual sheet URLs from the JavaScript logic in the page
    # The page uses a JS router to switch sheets. We extract the URLs directly.
    print("Parsing JS to find sheet URLs...")
    pattern = r'items\.push\(\{name: "(.*?)", pageUrl: "(.*?)", gid: "(.*?)"'
    matches = re.findall(pattern, iframe_resp.text)
    
    if not matches:
        print("No sheet items found in the JS. The format might have changed.")
        return

    all_schedules = []

    for name, page_url, gid in matches:
        # Clean up the extracted strings (JS escaping)
        name = name.replace(r'\/', '/')
        page_url = page_url.replace(r'\/', '/')
        page_url = page_url.replace(r'\x3d', '=')
        
        print(f"Fetching sheet: {name}")
        
        try:
            sheet_resp = requests.get(page_url)
            sheet_resp.raise_for_status()
            
            # Parse the table in the sheet
            # header=1 usually effectively captures the column names in these sheets
            sheet_dfs = pd.read_html(StringIO(sheet_resp.text), header=1)
            
            if sheet_dfs:
                df = sheet_dfs[0]
                df['Sheet Name'] = name # Add Date/Sheet name as a column
                all_schedules.append(df)
                print(f"  -> Extracted {len(df)} rows")
            else:
                print("  -> No table found in this sheet")
                
        except Exception as e:
            print(f"  -> Failed to fetch/parse: {e}")

    # 5. Combine and Save
    # 5. Combine and Save
    if all_schedules:
        final_df = pd.concat(all_schedules, ignore_index=True)
        
        # Clean up empty rows if any
        final_df.dropna(how='all', inplace=True)

        print(f"\nExtracted {len(final_df)} total records.")
        
        # Determine output file path
        outfile_csv = "doctors_schedule.csv"
        outfile_json = "schedule.json"
        
        # Save CSV for legacy/debugging
        final_df.to_csv(outfile_csv, index=False)
        print(f"Saved schedule to {outfile_csv}")
        
        # Replace NaN with None for valid JSON
        import numpy as np
        final_df = final_df.replace({np.nan: None})
        
        # Transform into a clean list for the App
        records = final_df.to_dict(orient='records')
        clean_records = []
        for row in records:
            sheet_name = row.get("Sheet Name")
            if not sheet_name:
                continue
                
            # Helper to extract and clean doctor info
            def add_doctor(name_key, time_key, category):
                name = row.get(name_key)
                timing = row.get(time_key)
                
                # Filter out header rows or empty rows that pandas might have caught as partials
                if not name or not isinstance(name, str) or name.upper() in ["DOCTOR'S NAME", "S.NO"]:
                    return
                if not timing or not isinstance(timing, str) or timing.upper() == "TIMING":
                    return
                    
                clean_records.append({
                    "date": sheet_name,
                    "name": name,
                    "timing": timing,
                    "category": category,
                    "room": row.get(name_key.replace(".1", ".2"), ""), # Best guess mapping
                    # Add raw timestamp for sorting if needed, but string date is okay for now
                })

            # Map the columns correctly based on inspection
            # REGULAR DOCTORS/ DENTIST.1 -> Name
            # REGULAR DOCTORS/ DENTIST.3 -> Timing
            add_doctor("REGULAR DOCTORS/ DENTIST.1", "REGULAR DOCTORS/ DENTIST.3", "Regular/Dentist")
            
            # VISITING SPECIALISTS DOCTORS.1 -> Name
            # VISITING SPECIALISTS DOCTORS.4 -> Timing
            add_doctor("VISITING SPECIALISTS DOCTORS.1", "VISITING SPECIALISTS DOCTORS.4", "Visiting Specialist")

        # Save Clean JSON for Web App
        with open(outfile_json, 'w') as f:
            json.dump(clean_records, f, indent=2)
        print(f"Saved clean schedule to {outfile_json} ({len(clean_records)} doctors)")

        return clean_records
    else:
        print("No schedule data extracted.")
        return []

if __name__ == "__main__":
    extract_schedule()
