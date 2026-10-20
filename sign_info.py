"""
Traffic Sign Knowledge Base (sign_info.py)
Contains sign definitions, risk levels, meanings, and recommended driver actions.
Supports fuzzy label normalization for 36+ traffic sign classes.
"""

import re

# Local dictionary containing traffic sign definitions
SIGN_INFO = {
    # Regulatory Signs - Critical Risk
    "stop": {
        "name": "Stop Sign",
        "meaning": "Mandatory stop required. Vehicles must come to a complete standstill before entering the intersection.",
        "risk": "Critical",
        "action": "Come to a complete stop before the stop line or crosswalk. Look left, right, and proceed only when clear.",
        "category": "Regulatory"
    },
    "do_not_enter": {
        "name": "Do Not Enter",
        "meaning": "Vehicles are strictly prohibited from entering this roadway or traffic lane.",
        "risk": "Critical",
        "action": "Do not proceed forward. Turn around or safely select an alternate route immediately.",
        "category": "Regulatory"
    },
    "no_entry": {
        "name": "No Entry",
        "meaning": "Entry is prohibited for all vehicular traffic.",
        "risk": "Critical",
        "action": "Do not enter. Vehicle entry prohibited.",
        "category": "Regulatory"
    },
    "no_stopping": {
        "name": "No Stopping",
        "meaning": "Stopping or standing vehicle is strictly prohibited at all times.",
        "risk": "High",
        "action": "Maintain vehicle movement. Do not pull over or stop under any circumstance.",
        "category": "Regulatory"
    },

    # Regulatory Signs - High & Medium Risk
    "yield": {
        "name": "Yield Right-of-Way",
        "meaning": "Drivers must yield right-of-way to oncoming traffic and pedestrians on the main road.",
        "risk": "High",
        "action": "Slow down and prepare to stop if necessary. Give priority to intersecting traffic.",
        "category": "Regulatory"
    },
    "no_overtaking": {
        "name": "No Overtaking / No Passing",
        "meaning": "Passing or overtaking other moving vehicles is strictly prohibited due to limited visibility or hazards.",
        "risk": "High",
        "action": "Maintain lane position behind preceding vehicle. Do not attempt to overtake.",
        "category": "Regulatory"
    },
    "no_u_turn": {
        "name": "No U-Turn",
        "meaning": "U-turns are prohibited at this location or intersection.",
        "risk": "High",
        "action": "Do not perform a U-turn. Continue straight and find a safe, legal turning area ahead.",
        "category": "Regulatory"
    },
    "no_parking": {
        "name": "No Parking",
        "meaning": "Parking is prohibited in this designated zone.",
        "risk": "Medium",
        "action": "Do not park or leave your vehicle unattended in this designated zone.",
        "category": "Regulatory"
    },
    "no_left_turn": {
        "name": "No Left Turn",
        "meaning": "Left turns are prohibited at this intersection.",
        "risk": "Medium",
        "action": "Do not turn left. Proceed straight or turn right according to road design.",
        "category": "Regulatory"
    },
    "no_right_turn": {
        "name": "No Right Turn",
        "meaning": "Right turns are prohibited at this intersection.",
        "risk": "Medium",
        "action": "Do not turn right. Proceed straight or adjust navigation accordingly.",
        "category": "Regulatory"
    },

    # Speed Limit Signs
    "speed_limit_20": {
        "name": "Speed Limit 20 km/h",
        "meaning": "Maximum legal driving speed is limited to 20 km/h (Low speed / residential zone).",
        "risk": "Low",
        "action": "Reduce vehicle speed to 20 km/h or below. Stay alert for pedestrians.",
        "category": "Speed Limit"
    },
    "speed_limit_30": {
        "name": "Speed Limit 30 km/h",
        "meaning": "Maximum legal driving speed is limited to 30 km/h.",
        "risk": "Low",
        "action": "Reduce vehicle speed to 30 km/h or below. Maintain safe following distance.",
        "category": "Speed Limit"
    },
    "speed_limit_50": {
        "name": "Speed Limit 50 km/h",
        "meaning": "Maximum legal driving speed is limited to 50 km/h (Standard urban zone).",
        "risk": "Low",
        "action": "Maintain vehicle speed at or below 50 km/h.",
        "category": "Speed Limit"
    },
    "speed_limit_60": {
        "name": "Speed Limit 60 km/h",
        "meaning": "Maximum legal driving speed is limited to 60 km/h.",
        "risk": "Low",
        "action": "Maintain vehicle speed at or below 60 km/h.",
        "category": "Speed Limit"
    },
    "speed_limit_70": {
        "name": "Speed Limit 70 km/h",
        "meaning": "Maximum legal driving speed is limited to 70 km/h.",
        "risk": "Low",
        "action": "Maintain vehicle speed at or below 70 km/h.",
        "category": "Speed Limit"
    },
    "speed_limit_80": {
        "name": "Speed Limit 80 km/h",
        "meaning": "Maximum legal driving speed is limited to 80 km/h.",
        "risk": "Low",
        "action": "Maintain vehicle speed at or below 80 km/h on express roads.",
        "category": "Speed Limit"
    },
    "speed_limit_100": {
        "name": "Speed Limit 100 km/h",
        "meaning": "Maximum legal highway speed is limited to 100 km/h.",
        "risk": "Low",
        "action": "Maintain highway speed up to 100 km/h safely according to traffic flow.",
        "category": "Speed Limit"
    },
    "speed_limit_120": {
        "name": "Speed Limit 120 km/h",
        "meaning": "Maximum legal freeway speed is limited to 120 km/h.",
        "risk": "Low",
        "action": "Maintain speed at or below 120 km/h. Keep safe lane clearance.",
        "category": "Speed Limit"
    },

    # Warning / Hazard Signs
    "pedestrian": {
        "name": "Pedestrian Crossing Ahead",
        "meaning": "Pedestrian crosswalk or frequent pedestrian traffic zone ahead.",
        "risk": "High",
        "action": "Slow down, scan roadside areas, and prepare to yield to pedestrians.",
        "category": "Warning"
    },
    "pedestrian_crossing": {
        "name": "Pedestrian Crosswalk",
        "meaning": "Designated pedestrian crosswalk location.",
        "risk": "High",
        "action": "Yield right-of-way to any pedestrians stepping onto or crossing the street.",
        "category": "Warning"
    },
    "school_zone": {
        "name": "School Zone",
        "meaning": "School area or child crossing zone ahead.",
        "risk": "High",
        "action": "Significantly reduce speed, observe crossing guards, and watch out for children.",
        "category": "Warning"
    },
    "slippery_road": {
        "name": "Slippery Road Hazard",
        "meaning": "Road surface becomes hazardous and slippery when wet or icy.",
        "risk": "High",
        "action": "Eze off accelerator, avoid sudden hard braking, and steer gently.",
        "category": "Warning"
    },
    "road_works": {
        "name": "Road Construction / Maintenance",
        "meaning": "Construction work, workers, or machinery on or near the roadway.",
        "risk": "Medium",
        "action": "Reduce speed, follow detour signs, and stay alert for highway workers.",
        "category": "Warning"
    },
    "traffic_signals": {
        "name": "Traffic Signals Ahead",
        "meaning": "Traffic control signal lights ahead at the next intersection.",
        "risk": "Medium",
        "action": "Prepare to adjust speed for potential red signal or stopping traffic.",
        "category": "Warning"
    },
    "crossroads": {
        "name": "Crossroads Intersection",
        "meaning": "Four-way road intersection ahead.",
        "risk": "Medium",
        "action": "Slow down, check both left and right directions before entering intersection.",
        "category": "Warning"
    },
    "roundabout": {
        "name": "Traffic Roundabout",
        "meaning": "Circular traffic intersection ahead.",
        "risk": "Medium",
        "action": "Slow down, yield to traffic approaching from the right inside the circle.",
        "category": "Warning"
    },
    "bump": {
        "name": "Speed Bump / Hump Ahead",
        "meaning": "Physical road elevation or speed bump ahead.",
        "risk": "Medium",
        "action": "Decelerate smoothly to prevent vehicle suspension shock or loss of control.",
        "category": "Warning"
    },
    "uneven_road": {
        "name": "Uneven Road Surface",
        "meaning": "Rough, potholed, or uneven pavement conditions ahead.",
        "risk": "Medium",
        "action": "Reduce speed to maintain steering stability and vehicle control.",
        "category": "Warning"
    },
    "narrow_road": {
        "name": "Road Narrows",
        "meaning": "Roadway width narrows significantly ahead from both sides or one side.",
        "risk": "Medium",
        "action": "Adjust lane positioning and check for oncoming vehicles.",
        "category": "Warning"
    },
    "bicycles_crossing": {
        "name": "Bicycle Lane / Crossing",
        "meaning": "Bicycle pathway or frequent cyclist crossing zone ahead.",
        "risk": "Medium",
        "action": "Check blind spots and yield to cyclists crossing or riding along the shoulder.",
        "category": "Warning"
    },
    "wild_animals": {
        "name": "Wild Animal Crossing",
        "meaning": "Area prone to sudden animal crossings on the road.",
        "risk": "Medium",
        "action": "Drive cautiously, scan shoulders, and use high beams safely at night.",
        "category": "Warning"
    },
    "steep_ascent": {
        "name": "Steep Uphill Grade",
        "meaning": "Steep upward slope ahead.",
        "risk": "Low",
        "action": "Select appropriate gear to maintain engine momentum while climbing.",
        "category": "Warning"
    },
    "steep_descent": {
        "name": "Steep Downhill Grade",
        "meaning": "Steep downward slope ahead.",
        "risk": "Medium",
        "action": "Use engine braking, lower gear, and avoid continuous brake riding.",
        "category": "Warning"
    },

    # Mandatory / Direction Signs
    "turn_left": {
        "name": "Turn Left Ahead",
        "meaning": "Mandatory direction to turn left.",
        "risk": "Low",
        "action": "Signal left turn early and execute turn safely.",
        "category": "Mandatory"
    },
    "turn_right": {
        "name": "Turn Right Ahead",
        "meaning": "Mandatory direction to turn right.",
        "risk": "Low",
        "action": "Signal right turn early and execute turn safely.",
        "category": "Mandatory"
    },
    "ahead_only": {
        "name": "Straight Ahead Only",
        "meaning": "Traffic must proceed straight ahead only; turning is prohibited.",
        "risk": "Low",
        "action": "Drive straight ahead. Do not turn left or right.",
        "category": "Mandatory"
    },
    "keep_right": {
        "name": "Keep Right",
        "meaning": "Keep vehicle to the right side of traffic divider or island.",
        "risk": "Low",
        "action": "Pass obstacle or island on the right side.",
        "category": "Mandatory"
    },
    "keep_left": {
        "name": "Keep Left",
        "meaning": "Keep vehicle to the left side of traffic divider or island.",
        "risk": "Low",
        "action": "Pass obstacle or island on the left side.",
        "category": "Mandatory"
    },
    "u_turn": {
        "name": "U-Turn Permitted",
        "meaning": "Designated location for making a legal U-turn.",
        "risk": "Medium",
        "action": "Yield to oncoming traffic and perform U-turn when clear.",
        "category": "Mandatory"
    },
    "general_caution": {
        "name": "General Danger / Caution",
        "meaning": "General road hazard or unspecified danger ahead.",
        "risk": "High",
        "action": "Increase alertness, reduce speed, and be prepared for hazards.",
        "category": "Warning"
    },

    # Indian Road Traffic Signs (56 Classes Expansion)
    "all_motor_vehicle_prohibited": {
        "name": "All Motor Vehicles Prohibited",
        "meaning": "Entry is strictly prohibited for all motorized vehicles (cars, motorcycles, trucks, buses).",
        "risk": "High",
        "action": "Do not enter with any motor vehicle. Divert to permitted vehicular routes.",
        "category": "Regulatory"
    },
    "axle_load_limit": {
        "name": "Axle Load Limit",
        "meaning": "Maximum permissible load transmitted to the road by any single vehicle axle.",
        "risk": "High",
        "action": "Heavy vehicles exceeding the indicated axle weight limit must not proceed over this structure.",
        "category": "Regulatory"
    },
    "cross_road": {
        "name": "Cross Road Intersection Ahead",
        "meaning": "Approaching a direct four-way crossroads intersection.",
        "risk": "Medium",
        "action": "Slow down, check left and right directions, and yield according to right-of-way rules.",
        "category": "Warning"
    },
    "dangerous_dip": {
        "name": "Dangerous Dip Ahead",
        "meaning": "Sudden sharp depression or dip in the road elevation ahead.",
        "risk": "High",
        "action": "Decelerate smoothly to avoid vehicle bottoming out or suspension damage.",
        "category": "Warning"
    },
    "falling_rocks": {
        "name": "Falling Rocks Hazard",
        "meaning": "Roadway prone to falling stones or landslides from adjacent slopes/cliffs.",
        "risk": "High",
        "action": "Maintain vigilant driving, scan hillside slopes, and avoid stopping in vulnerable zones.",
        "category": "Warning"
    },
    "gap_in_median": {
        "name": "Gap in Median / Opening Ahead",
        "meaning": "An opening in the central traffic divider allowing turning traffic or U-turns.",
        "risk": "Medium",
        "action": "Stay alert for vehicles slowing down or emerging unexpectedly from the median gap.",
        "category": "Warning"
    },
    "guarded_level_crossing": {
        "name": "Guarded Railway Level Crossing Ahead",
        "meaning": "Approaching a railway track crossing protected by gates or barriers.",
        "risk": "High",
        "action": "Slow down, obey signal lights and barrier positions; stop completely when barriers are closed.",
        "category": "Warning"
    },
    "unguarded_level_crossing": {
        "name": "Unguarded Railway Level Crossing Ahead",
        "meaning": "Approaching an unprotected railway crossing with no gates or watchmen.",
        "risk": "Critical",
        "action": "Mandatory stop before tracks. Look left and right, listen for train horns, proceed only when 100% clear.",
        "category": "Warning"
    },
    "height_limit": {
        "name": "Height Limit",
        "meaning": "Prohibits vehicles exceeding the indicated height (under flyovers, bridges, wires).",
        "risk": "High",
        "action": "Check total vehicle and cargo height. Do not proceed if exceeding the posted clearance limit.",
        "category": "Regulatory"
    },
    "width_limit": {
        "name": "Width Limit",
        "meaning": "Prohibits vehicles exceeding the indicated width on narrow roadways or bridges.",
        "risk": "High",
        "action": "Do not enter narrow corridor if vehicle width exceeds the posted limit.",
        "category": "Regulatory"
    },
    "horn_prohibited": {
        "name": "Horn Prohibited (Silence Zone)",
        "meaning": "Sounding horns or acoustic warning devices is prohibited (near hospitals, schools, courts).",
        "risk": "Medium",
        "action": "Maintain silence. Do not sound vehicle horn in this designated silent zone.",
        "category": "Regulatory"
    },
    "hospital_ahead": {
        "name": "Hospital Ahead",
        "meaning": "Medical facility or hospital located adjacent to roadway.",
        "risk": "Low",
        "action": "Reduce vehicle speed, avoid honking, and yield to ambulances and medical transport.",
        "category": "Informatory"
    },
    "hump_or_rough_road": {
        "name": "Hump or Rough Road Ahead",
        "meaning": "Severe speed breaker, road hump, or degraded pavement surface ahead.",
        "risk": "Medium",
        "action": "Slow down progressively to navigate bump smoothly without vehicle damage.",
        "category": "Warning"
    },
    "loose_gravel": {
        "name": "Loose Gravel on Road",
        "meaning": "Uncompacted stone gravel on road surface, reducing tire grip and traction.",
        "risk": "High",
        "action": "Increase following distance, brake gently, and avoid sudden steering inputs to prevent skids.",
        "category": "Warning"
    },
    "men_at_work": {
        "name": "Men at Work / Road Works",
        "meaning": "Highway maintenance, road workers, or heavy machinery active on or near the road.",
        "risk": "Medium",
        "action": "Reduce driving speed, observe directional signage, and watch out for roadway workers.",
        "category": "Warning"
    },
    "narrow_bridge_ahead": {
        "name": "Narrow Bridge Ahead",
        "meaning": "Bridge structure ahead is significantly narrower than the approaching road width.",
        "risk": "Medium",
        "action": "Reduce speed, yield to oncoming traffic on bridge, and strictly avoid overtaking.",
        "category": "Warning"
    },
    "pass_either_side": {
        "name": "Pass Either Side",
        "meaning": "Traffic may safely pass on either side of the traffic island or road obstruction.",
        "risk": "Low",
        "action": "Choose left or right lane according to your onward route and traffic flow.",
        "category": "Mandatory"
    },
    "petrol_pump_ahead": {
        "name": "Petrol / Fuel Station Ahead",
        "meaning": "Automotive fuel filling station located ahead along the route.",
        "risk": "Low",
        "action": "Prepare to indicate and decelerate safely if refueling is required.",
        "category": "Informatory"
    },
    "quay_side_or_river_bank": {
        "name": "Quayside or River Bank Ahead",
        "meaning": "Roadway leads toward or runs alongside an open body of water or canal bank.",
        "risk": "High",
        "action": "Drive with heightened caution, decelerate, and keep safe distance from water edge.",
        "category": "Warning"
    },
    "restriction_ends": {
        "name": "End of Speed / Traffic Restriction",
        "meaning": "Point at which previously posted speed or passing restrictions cease to apply.",
        "risk": "Low",
        "action": "Resume standard highway driving speed and standard traffic rules.",
        "category": "Regulatory"
    },
    "road_widens_ahead": {
        "name": "Road Widens Ahead",
        "meaning": "Carriageway widens to accommodate additional traffic lanes ahead.",
        "risk": "Low",
        "action": "Align into appropriate lane smoothly according to traffic conditions.",
        "category": "Informatory"
    },
    "staggered_intersection": {
        "name": "Staggered Intersection Ahead",
        "meaning": "Approaching two consecutive side-road junctions offset from one another.",
        "risk": "Medium",
        "action": "Slow down and scan both left and right for merging vehicles.",
        "category": "Warning"
    },
    "straight_prohibited": {
        "name": "Straight Ahead Prohibited / No Direct Entry",
        "meaning": "Vehicles are prohibited from proceeding directly straight ahead.",
        "risk": "High",
        "action": "Do not proceed straight. Turn left or right according to designated lane markings.",
        "category": "Regulatory"
    },
    "t_intersection": {
        "name": "T-Intersection Ahead",
        "meaning": "Approaching a dead end where the road terminates into a cross road forming a T-junction.",
        "risk": "Medium",
        "action": "Slow down, prepare to stop, and yield right-of-way to cross-traffic before turning.",
        "category": "Warning"
    },
    "y_intersection": {
        "name": "Y-Intersection / Fork in Road Ahead",
        "meaning": "Approaching a three-way junction where the road splits in a Y-shaped fork.",
        "risk": "Medium",
        "action": "Choose your lane early, signal your turning direction, and watch for merging vehicles.",
        "category": "Warning"
    },
    "left_turn_prohibited": {
        "name": "Left Turn Prohibited",
        "meaning": "Left turns are prohibited at this intersection or roadway section.",
        "risk": "Medium",
        "action": "Do not turn left. Proceed straight or turn right according to road design.",
        "category": "Regulatory"
    },
    "right_turn_prohibited": {
        "name": "Right Turn Prohibited",
        "meaning": "Right turns are prohibited at this intersection or roadway section.",
        "risk": "Medium",
        "action": "Do not turn right. Proceed straight or follow alternate detour.",
        "category": "Regulatory"
    },
    "u_turn_prohibited": {
        "name": "U-Turn Prohibited",
        "meaning": "U-turns are prohibited at this location, intersection, or divider gap.",
        "risk": "High",
        "action": "Do not perform a U-turn. Continue straight and find an authorized turning location ahead.",
        "category": "Regulatory"
    },
    "no_stopping_or_standing": {
        "name": "No Stopping or Standing",
        "meaning": "Stopping or parking any vehicle is strictly prohibited at all times.",
        "risk": "High",
        "action": "Maintain vehicle movement. Do not pull over, halt, or stand under any circumstance.",
        "category": "Regulatory"
    },
    "overtaking_prohibited": {
        "name": "Overtaking Prohibited",
        "meaning": "Passing or overtaking other moving vehicles is strictly prohibited.",
        "risk": "High",
        "action": "Maintain lane position behind preceding vehicle. Do not attempt to pass.",
        "category": "Regulatory"
    },
    "compulsary_keep_left": {
        "name": "Compulsory Keep Left",
        "meaning": "Vehicles must pass to the left side of the divider, refuge, or island.",
        "risk": "Low",
        "action": "Steer and pass to the left side of the traffic divider or obstacle.",
        "category": "Mandatory"
    },
    "compulsary_keep_right": {
        "name": "Compulsory Keep Right",
        "meaning": "Vehicles must pass to the right side of the divider, refuge, or island.",
        "risk": "Low",
        "action": "Steer and pass to the right side of the traffic divider or obstacle.",
        "category": "Mandatory"
    },
    "compulsary_turn_left_ahead": {
        "name": "Compulsory Turn Left Ahead",
        "meaning": "Mandatory direction to turn left at the upcoming junction.",
        "risk": "Low",
        "action": "Signal left turn early and complete turn into designated lane.",
        "category": "Mandatory"
    },
    "compulsary_turn_right_ahead": {
        "name": "Compulsory Turn Right Ahead",
        "meaning": "Mandatory direction to turn right at the upcoming junction.",
        "risk": "Low",
        "action": "Signal right turn early and complete turn into designated lane.",
        "category": "Mandatory"
    },
    "compulsary_ahead": {
        "name": "Compulsory Ahead Only",
        "meaning": "Traffic must proceed straight ahead only; turning is prohibited.",
        "risk": "Low",
        "action": "Drive straight ahead. Turning left or right is prohibited.",
        "category": "Mandatory"
    },
    "left_hand_curve": {
        "name": "Left Hand Curve Ahead",
        "meaning": "Approaching a sharp or hazardous curve to the left.",
        "risk": "Medium",
        "action": "Reduce speed, maintain lane position, and do not overtake on curve.",
        "category": "Warning"
    },
    "right_hand_curve": {
        "name": "Right Hand Curve Ahead",
        "meaning": "Approaching a sharp or hazardous curve to the right.",
        "risk": "Medium",
        "action": "Reduce speed, maintain lane position, and do not overtake on curve.",
        "category": "Warning"
    },
    "left_reverse_bend": {
        "name": "Left Reverse Bend Ahead",
        "meaning": "Approaching a double curve, first turning left then right.",
        "risk": "Medium",
        "action": "Reduce speed, keep within your lane, and prepare for consecutive directional changes.",
        "category": "Warning"
    },
    "right_reverse_bend": {
        "name": "Right Reverse Bend Ahead",
        "meaning": "Approaching a double curve, first turning right then left.",
        "risk": "Medium",
        "action": "Reduce speed, keep within your lane, and prepare for consecutive directional changes.",
        "category": "Warning"
    },
    "side_road_left": {
        "name": "Side Road Left",
        "meaning": "Secondary side-road connects to the main road from the left.",
        "risk": "Medium",
        "action": "Maintain driving lane, be prepared for vehicles emerging or turning into the side road.",
        "category": "Warning"
    },
    "side_road_right": {
        "name": "Side Road Right",
        "meaning": "Secondary side-road connects to the main road from the right.",
        "risk": "Medium",
        "action": "Maintain driving lane, be prepared for vehicles emerging or turning into the side road.",
        "category": "Warning"
    },
    "narrow_road_ahead": {
        "name": "Narrow Road Ahead",
        "meaning": "Roadway width narrows significantly ahead.",
        "risk": "Medium",
        "action": "Adjust lane positioning and check for oncoming vehicles.",
        "category": "Warning"
    }
}


def normalize_sign_label(raw_label: str) -> str:
    """
    Normalizes arbitrary YOLO detection label into standard database key format.
    Example: 'Speed limit (50km/h)' -> 'speed_limit_50'
             'Stop sign' -> 'stop'
    """
    if not raw_label:
        return "general_caution"

    cleaned = str(raw_label).lower().strip()

    # Direct match check
    if cleaned in SIGN_INFO:
        return cleaned

    # Replace dashes, spaces, and special characters with underscores
    cleaned = re.sub(r'[^a-z0-9]+', '_', cleaned).strip('_')

    if cleaned in SIGN_INFO:
        return cleaned

    # Pattern checks for speed limits
    speed_match = re.search(r'speed[_\s]*limit[_\s]*(\d+)', raw_label, re.IGNORECASE) or re.search(r'(\d+)', raw_label)
    if "speed" in raw_label.lower() or "limit" in raw_label.lower():
        if speed_match:
            num = speed_match.group(1)
            key = f"speed_limit_{num}"
            if key in SIGN_INFO:
                return key

    # Keywords fallback
    keyword_map = {
        "stop": "stop",
        "yield": "yield",
        "give_way": "yield",
        "enter": "do_not_enter",
        "parking": "no_parking",
        "stopping": "no_stopping",
        "overtaking": "no_overtaking",
        "pedestrian": "pedestrian",
        "crosswalk": "pedestrian_crossing",
        "school": "school_zone",
        "signal": "traffic_signals",
        "light": "traffic_signals",
        "bump": "bump",
        "slippery": "slippery_road",
        "construction": "road_works",
        "works": "road_works",
        "roundabout": "roundabout",
        "narrow": "narrow_road",
        "animal": "wild_animals",
        "bike": "bicycles_crossing",
        "cycle": "bicycles_crossing",
        "u_turn": "u_turn",
        "left": "turn_left",
        "right": "turn_right",
        "ahead": "ahead_only",
        "horn": "horn_prohibited",
        "axle": "axle_load_limit",
        "height": "height_limit",
        "width": "width_limit",
        "hospital": "hospital_ahead",
        "hump": "hump_or_rough_road",
        "rough": "hump_or_rough_road",
        "median": "gap_in_median",
        "dip": "dangerous_dip",
        "rock": "falling_rocks",
        "gravel": "loose_gravel",
        "unguarded": "unguarded_level_crossing",
        "guarded": "guarded_level_crossing",
        "quay": "quay_side_or_river_bank",
        "river": "quay_side_or_river_bank",
        "restriction": "restriction_ends",
        "widen": "road_widens_ahead",
        "staggered": "staggered_intersection",
        "either": "pass_either_side",
        "motor_vehicle": "all_motor_vehicle_prohibited",
    }

    for kw, target_key in keyword_map.items():
        if kw in cleaned:
            return target_key

    return cleaned


def get_sign_info(raw_label: str) -> dict:
    """
    Retrieves full sign metadata dictionary for a given label string.
    If label is not in database, returns fallback formatted sign information.
    """
    key = normalize_sign_label(raw_label)

    if key in SIGN_INFO:
        info = SIGN_INFO[key].copy()
        info["key"] = key
        return info

    # Intelligent fallback for unknown / unmapped labels
    display_title = raw_label.replace("_", " ").replace("-", " ").title()
    return {
        "key": key,
        "name": display_title,
        "meaning": f"Detected traffic sign identified as '{display_title}'. Drive with appropriate caution.",
        "risk": "Medium",
        "action": f"Observe '{display_title}' regulations, slow down, and monitor road conditions.",
        "category": "Traffic Sign"
    }
