import json

def load_room_mappings():
    """Load the room mapping files"""
    try:
        # Load description to code mapping
        with open('data/room_description_to_code_mapping.json', 'r') as f:
            desc_to_code = json.load(f)
        
        # Load code to description mapping
        with open('data/room_code_to_description_mapping.json', 'r') as f:
            code_to_desc = json.load(f)
        
        return desc_to_code, code_to_desc
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run 'create_room_mapping.py' first to generate the mapping files.")
        return None, None

def get_room_code(room_description):
    """Get room code for a given description"""
    desc_to_code, _ = load_room_mappings()
    if desc_to_code:
        return desc_to_code.get(room_description, "Code not found")
    return None

def get_room_descriptions(room_code):
    """Get all descriptions for a given room code"""
    _, code_to_desc = load_room_mappings()
    if code_to_desc:
        return code_to_desc.get(room_code, ["Description not found"])
    return None

def search_rooms_by_keyword(keyword):
    """Search for rooms containing a specific keyword"""
    desc_to_code, _ = load_room_mappings()
    if not desc_to_code:
        return {}
    
    keyword = keyword.upper()
    matches = {}
    
    for description, code in desc_to_code.items():
        if keyword in description.upper():
            matches[description] = code
    
    return matches

def main():
    print("=== ROOM MAPPING USAGE EXAMPLES ===\n")
    
    # Load mappings
    desc_to_code, code_to_desc = load_room_mappings()
    
    if not desc_to_code or not code_to_desc:
        return
    
    print(f"Loaded mappings for {len(desc_to_code)} room descriptions and {len(code_to_desc)} room codes\n")
    
    # Example 1: Get code for a specific description
    print("1. Looking up room code for 'SUNSET WATER BUNGALOW WITH JACUZZI':")
    code = get_room_code("SUNSET WATER BUNGALOW WITH JACUZZI")
    print(f"   Code: {code}\n")
    
    # Example 2: Get descriptions for a specific code
    print("2. Looking up descriptions for room code 'ZJUKI':")
    descriptions = get_room_descriptions("ZJUKI")
    print(f"   Descriptions: {descriptions}\n")
    
    # Example 3: Search for suite rooms
    print("3. Searching for rooms containing 'SUITE':")
    suite_rooms = search_rooms_by_keyword("SUITE")
    for desc, code in list(suite_rooms.items())[:10]:  # Show first 10
        print(f"   {desc} -> {code}")
    if len(suite_rooms) > 10:
        print(f"   ... and {len(suite_rooms) - 10} more suite rooms")
    print()
    
    # Example 4: Search for water bungalows
    print("4. Searching for rooms containing 'WATER':")
    water_rooms = search_rooms_by_keyword("WATER")
    for desc, code in list(water_rooms.items())[:8]:  # Show first 8
        print(f"   {desc} -> {code}")
    if len(water_rooms) > 8:
        print(f"   ... and {len(water_rooms) - 8} more water-related rooms")
    print()
    
    # Example 5: Search for king rooms
    print("5. Searching for rooms containing 'KING':")
    king_rooms = search_rooms_by_keyword("KING")
    print(f"   Found {len(king_rooms)} king rooms")
    for desc, code in list(king_rooms.items())[:5]:  # Show first 5
        print(f"   {desc} -> {code}")
    print()
    
    # Example 6: Check for duplicate codes
    print("6. Room codes with multiple descriptions:")
    multi_desc_codes = {code: descs for code, descs in code_to_desc.items() if len(descs) > 1}
    if multi_desc_codes:
        print(f"   Found {len(multi_desc_codes)} codes with multiple descriptions:")
        for code, descs in list(multi_desc_codes.items())[:3]:
            print(f"   {code}: {descs}")
    else:
        print("   No duplicate codes found - each code maps to exactly one description")

if __name__ == "__main__":
    main()