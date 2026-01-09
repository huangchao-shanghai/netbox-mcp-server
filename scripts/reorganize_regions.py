import requests
import json
import urllib3

# Configuration
API_URL = "https://nb200.lsn189.cn/api/"
TOKEN = "0123456789abcdef0123456789abcdef01234567"
HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_region_by_slug(slug):
    response = requests.get(f"{API_URL}dcim/regions/?slug={slug}", headers=HEADERS, verify=False)
    if response.status_code == 200 and response.json()["count"] > 0:
        return response.json()["results"][0]
    return None

def create_region(name, slug, description):
    existing = get_region_by_slug(slug)
    if existing:
        print(f"Region '{name}' already exists (ID: {existing['id']})")
        return existing["id"]
    
    payload = {
        "name": name,
        "slug": slug,
        "description": description
    }
    response = requests.post(f"{API_URL}dcim/regions/", headers=HEADERS, json=payload, verify=False)
    if response.status_code == 201:
        data = response.json()
        print(f"Created region '{name}' (ID: {data['id']})")
        return data["id"]
    else:
        print(f"Failed to create region '{name}': {response.text}")
        return None

def update_region_parent(child_slug, parent_id):
    child = get_region_by_slug(child_slug)
    if not child:
        print(f"Child region '{child_slug}' not found")
        return

    # Check if update is needed
    current_parent_id = child["parent"]["id"] if child["parent"] else None
    if current_parent_id == parent_id:
        print(f"Region '{child_slug}' already has correct parent")
        return

    payload = {
        "parent": parent_id
    }
    response = requests.patch(f"{API_URL}dcim/regions/{child['id']}/", headers=HEADERS, json=payload, verify=False)
    if response.status_code == 200:
        print(f"Updated '{child_slug}' parent to ID {parent_id}")
    else:
        print(f"Failed to update '{child_slug}': {response.text}")

def main():
    print("reorganizing regions based on NETBOX_CONCEPTS.md...")

    # 1. Ensure Top-Level Continents exist
    # Based on "Recommended Hierarchy" in NETBOX_CONCEPTS.md
    continents = {
        "asia-pacific": {"name": "Asia Pacific", "desc": "亚太地区"},
        "europe": {"name": "Europe", "desc": "欧洲"},
        "north-america": {"name": "North America", "desc": "北美洲"} # Implied for USA consistency
    }

    continent_ids = {}
    for slug, info in continents.items():
        continent_ids[slug] = create_region(info["name"], slug, info["desc"])

    # 2. Map Countries to Continents
    # Map Schema: Child Region Slug -> Parent Continent Slug
    mapping = {
        "china": "asia-pacific",
        "hongkong": "asia-pacific",
        "japan": "asia-pacific",
        "singapore": "asia-pacific",
        "germany": "europe",
        "usa": "north-america"
    }

    for child_slug, parent_slug in mapping.items():
        parent_id = continent_ids.get(parent_slug)
        if parent_id:
            update_region_parent(child_slug, parent_id)
        else:
            print(f"Skipping {child_slug}: Parent {parent_slug} creation failed")

if __name__ == "__main__":
    main()
