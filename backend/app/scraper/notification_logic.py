import re
from datetime import datetime, timedelta

def parse_time_range(time_str):
    """
    Parses time strings like:
    - "03:30 PM to 07:00 PM"
    - "11:30 AM-01:30 PM"
    - "08:00-14:00"
    Returns (start_time_obj, end_time_obj) as datetime.time objects, or None.
    """
    if not isinstance(time_str, str):
        return None
        
    # Normalize string: remove extra spaces, unify separator
    cleaned = time_str.lower().strip()
    cleaned = cleaned.replace(" to ", "-").replace(" - ", "-").replace(" – ", "-") 
    
    parts = cleaned.split('-')
    if len(parts) != 2:
        return None
        
    start_str, end_str = parts[0].strip(), parts[1].strip()
    
    def parse_single_time(t_str):
        # Try different formats
        formats = ["%I:%M %p", "%I:%M%p", "%H:%M"]
        for fmt in formats:
            try:
                return datetime.strptime(t_str, fmt).time()
            except ValueError:
                continue
        return None

    start_time = parse_single_time(start_str)
    end_time = parse_single_time(end_str)
    
    if start_time and end_time:
        return start_time, end_time
    return None

def check_upcoming_doctors(schedule_data, current_dt=None):
    """
    Checks schedule_data for doctors starting within the next hour.
    schedule_data: List of dicts (rows).
    current_dt: datetime object (defaults to now).
    """
    if current_dt is None:
        current_dt = datetime.now()
        
    upcoming = []
    
    # Simple map for date matching "31/01/2026 SATURDAY" -> boolean
    # Logic: Filter by current date first
    current_date_str = current_dt.strftime("%d/%m/%Y")
    
    for row in schedule_data:
        sheet_name = row.get("Sheet Name", "")
        if current_date_str not in sheet_name:
            continue
            
        # Check Regular Doctors
        # Columns often named "REGULAR DOCTORS/ DENTIST.3" for timing, but exact name varies
        # We need a robust way to find the timing column. 
        # Based on CSV: "REGULAR DOCTORS/ DENTIST.3" is TIMING
        # "VISITING SPECIALISTS DOCTORS.4" is TIMING
        
        # Helper to check a specific doctor entry in the row
        def check_entry(name, timing_str, category):
            if not name or not timing_str:
                return
            
            times = parse_time_range(timing_str)
            if not times:
                return
                
            start, end = times
            
            # Create full datetime for start
            start_dt = datetime.combine(current_dt.date(), start)
            
            # Check if start_time is soon (e.g. within next 60 mins)
            # Or if currently ongoing
            time_diff = start_dt - current_dt
            minutes_until = time_diff.total_seconds() / 60
            
            if 0 <= minutes_until <= 60:
                upcoming.append({
                    "name": name,
                    "category": category,
                    "starts_in_minutes": int(minutes_until),
                    "time_range": timing_str
                })
        
        # Inspect keys to find data columns dynamically or hardcod based on inspection
        # From previous viewing:
        # REGULAR DOCTORS/ DENTIST.1 : Name
        # REGULAR DOCTORS/ DENTIST.3 : Timing
        # VISITING SPECIALISTS DOCTORS.1 : Name
        # VISITING SPECIALISTS DOCTORS.4 : Timing
        
        r_name = row.get("REGULAR DOCTORS/ DENTIST.1")
        r_time = row.get("REGULAR DOCTORS/ DENTIST.3")
        check_entry(r_name, r_time, "Regular")
        
        v_name = row.get("VISITING SPECIALISTS DOCTORS.1")
        v_time = row.get("VISITING SPECIALISTS DOCTORS.4")
        check_entry(v_name, v_time, "Visiting")

    return upcoming
