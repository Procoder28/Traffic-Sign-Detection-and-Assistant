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
