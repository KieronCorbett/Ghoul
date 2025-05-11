import json
import os

XP_FILE = 'xp_profiles.json'

def load_profiles():
    if not os.path.exists(XP_FILE):
        with open(XP_FILE, 'w') as f:
            json.dump({}, f)
    with open(XP_FILE, 'r') as f:
        return json.load(f)

def save_profiles(data):
    with open(XP_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_profile(profiles, user_id):
    user_id = str(user_id)
    if user_id not in profiles:
        profiles[user_id] = {
            "xp": 0,
            "level": 1,
            "bio": "No bio set.",
            "color": "#00ff00",  # Default color
            "custom_name": "No Name Set"  # Added custom_name field
        }
    return profiles[user_id]

# Helper function to update a user's profile (e.g., bio, custom name, or color)
def update_user_profile(profiles, user_id, field, value):
    user_id = str(user_id)
    if user_id in profiles:
        profiles[user_id][field] = value
        save_profiles(profiles)