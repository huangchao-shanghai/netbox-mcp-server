import requests
import json
import os

# Configuration
API_URL = "https://nb200.lsn189.cn/api/"
TOKEN = "0123456789abcdef0123456789abcdef01234567"

# Data to import
# Name, Description, ID (ignored for creation), Parent, Slug
REGIONS_DATA = [
    {"name": "China", "description": "中国", "slug": "china", "parent": None},
    {"name": "Beijing", "description": "中国-北京", "slug": "beijing", "parent": "China"},
    {"name": "Shanghai", "description": "中国-上海", "slug": "shanghai", "parent": "China"},
    {"name": "Shenzhen", "description": "中国-深圳", "slug": "shenzhen", "parent": "China"},
    {"name": "Germany", "description": "德国", "slug": "germany", "parent": None},
    {"name": "Frankfurt", "description": "德国-法兰克福", "slug": "frankfurt", "parent": "Germany"},
    {"name": "HongKong", "description": "香港", "slug": "hongkong", "parent": None},
    {"name": "Japan", "description": "日本", "slug": "japan", "parent": None},
    {"name": "Tokyo", "description": "日本-东京", "slug": "tokyo", "parent": "Japan"},
    {"name": "Singapore", "description": "新加坡", "slug": "singapore", "parent": None},
    {"name": "USA", "description": "美国", "slug": "usa", "parent": None},
    {"name": "San Diego", "description": "美国-圣地亚哥", "slug": "san-diego", "parent": "USA"},
    {"name": "Seattle", "description": "美国-西雅图", "slug": "seattle", "parent": "USA"},
]

HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def get_region_id(slug):
    """Retrieve ID for a region by slug."""
    url = f"{API_URL}dcim/regions/?slug={slug}"
    try:
        response = requests.get(url, headers=HEADERS, verify=False) # Disable verify for self-signed or internal
        if response.status_code == 200:
            data = response.json()
            if data["count"] > 0:
                return data["results"][0]["id"]
    except Exception as e:
        print(f"Error fetching region {slug}: {e}")
    return None

def create_region(region_data):
    """Create a region if it doesn't exist."""
    
    # Check if parent exists and get ID if parent is specified
    parent_id = None
    if region_data["parent"]:
        parent_slug = REGIONS_DATA
        # Find parent slug from name in our data set, or assume parent name converted to slug?
        # The data has parent name. Let's look up the parent item in our list to find its slug.
        parent_item = next((item for item in REGIONS_DATA if item["name"] == region_data["parent"]), None)
        if parent_item:
            parent_id = get_region_id(parent_item["slug"])
            if not parent_id:
                print(f"Parent '{region_data['parent']}' not found in NetBox for '{region_data['name']}'. Skipping child.")
                return False
        else:
            print(f"Parent '{region_data['parent']}' definition not found in script data for '{region_data['name']}'.")
            return False

    # Check if region already exists
    existing_id = get_region_id(region_data["slug"])
    if existing_id:
        print(f"Region '{region_data['name']}' ({region_data['slug']}) already exists. Skipping.")
        return True

    # Construct payload
    payload = {
        "name": region_data["name"],
        "slug": region_data["slug"],
        "description": region_data["description"]
    }
    if parent_id:
        payload["parent"] = parent_id

    # Create
    url = f"{API_URL}dcim/regions/"
    response = requests.post(url, headers=HEADERS, json=payload, verify=False)
    
    if response.status_code == 201:
        print(f"Successfully created: {region_data['name']}")
        return True
    else:
        print(f"Failed to create {region_data['name']}: {response.status_code} - {response.text}")
        return False

def main():
    # Sort data: items with no parent first
    # This ensures parents are created before children
    # We can multiple passes or valid topological sort.
    # Simple approach: Create roots, then children.
    
    # 1. Parents (None)
    roots = [r for r in REGIONS_DATA if r["parent"] is None]
    
    # 2. Children (simplification: only 1 level of nesting in provided data)
    children = [r for r in REGIONS_DATA if r["parent"] is not None]

    print(f"Processing {len(roots)} root regions...")
    for region in roots:
        create_region(region)
        
    print(f"Processing {len(children)} child regions...")
    for region in children:
        create_region(region)

if __name__ == "__main__":
    # Suppress InsecureRequestWarning
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
