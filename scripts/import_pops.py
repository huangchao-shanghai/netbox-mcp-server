import requests
import json
import urllib3
import re

# Configuration
API_URL = "https://nb200.lsn189.cn/api/"
TOKEN = "0123456789abcdef0123456789abcdef01234567"
HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default IDs/Slugs (Need to ensure these exist or fetch them dynamically)
# Assumed Structure:
# Site Group: Edge Nodes (slug: edge-nodes) for POPs
# Tenant: Default to Shanghai Wanlian (slug: shanghai-wanlian) if not specified, or leave blank?
# Actually, POPs serve the network, maybe Internal or specific Tenant. 
# Let's map Tenants roughly or use a default one like "Shanghai Wanlian" as the owner/operator.
DEFAULT_TENANT_SLUG = "shanghai-wanlian"
DEFAULT_SITE_GROUP_SLUG = "edge-nodes" 

# Data
POPS = [
    {
        "name": "POP1-SHCEC",
        "slug": "pop1-shcec",
        "region_slug": "shanghai",
        "address": "上海普陀光复西路2739号，会展楼，3A",
        "description": "OneNote M3.2.1 LSN1=跨采@普陀-POP1",
        "locations": [
            {
                "name": "3M-J2",
                "slug": "3m-j2",
                "racks": ["G4", "G9", "G10"]
            }
        ]
    },
    {
        "name": "POP2-SNIEC",
        "slug": "pop2-sniec",
        "region_slug": "shanghai",
        "address": "上海浦东龙阳路2345号，新国际博览中心",
        "description": "OneNote M3.2.2 LSN2新博:POP2",
        "locations": [
            {
                "name": "SNIEC-SE-F5",
                "slug": "sniec-se-f5",
                "description": "南入口厅光端机房",
                "racks": ["RS06"]
            }
        ]
    },
    {
        "name": "POP22-TYOCC1",
        "slug": "pop22-tyocc1",
        "region_slug": "tokyo",
        "address": "〒135-0061 日本東京都江東区豊洲六丁目2番15号",
        "description": "OneNote M3.2.22 LSN22=东京CC1-宋昊合用-Pop22-TYOCC1",
        "locations": [
            {
                "name": "CC1-ServerRoom",
                "slug": "cc1-serverroom",
                "racks": ["R01"]
            }
        ]
    },
    {
        "name": "POP30-R6F-MO",
        "slug": "pop30-r6f-mo",
        "region_slug": "tokyo",
        "address": "日本东京南大冢",
        "description": "OneNote M3.2.30 POP30=R6F-MO@东京",
        "locations": [
            {
                "name": "R6F",
                "slug": "r6f",
                "racks": ["R01"]
            }
        ]
    },
    {
        "name": "POP31-B302.O",
        "slug": "pop31-b302-o",
        "region_slug": "tokyo",
        "address": "〒120-0046 東京都足立区小台一丁目16番12号 B302\nB302, 1-16-12 Odai, Adachi-ku, Tokyo 120-0046, Japan",
        "description": "OneNote M3.2.31 POP31=B302.O@东京",
        "locations": [
            {
                "name": "B302",
                "slug": "b302",
                "racks": ["R01"]
            }
        ]
    }
]

def get_id(endpoint, slug):
    try:
        resp = requests.get(f"{API_URL}{endpoint}/?slug={slug}", headers=HEADERS, verify=False)
        if resp.status_code == 200 and resp.json()['count'] > 0:
            return resp.json()['results'][0]['id']
    except Exception as e:
        print(f"Error fetching {slug} from {endpoint}: {e}")
    return None

def create_site(pop_data, tenant_id, site_group_id):
    region_id = get_id("dcim/regions", pop_data['region_slug'])
    if not region_id:
        print(f"Region {pop_data['region_slug']} not found. Skipping {pop_data['name']}")
        return None

    site_id = get_id("dcim/sites", pop_data['slug'])
    if site_id:
        print(f"Site {pop_data['name']} already exists.")
        return site_id

    payload = {
        "name": pop_data['name'],
        "slug": pop_data['slug'],
        "region": region_id,
        "group": site_group_id,
        "tenant": tenant_id,
        "status": "active",
        "physical_address": pop_data['address'],
        "description": pop_data['description']
    }
    
    resp = requests.post(f"{API_URL}dcim/sites/", headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"Created Site: {pop_data['name']}")
        return resp.json()['id']
    else:
        print(f"Failed to create Site {pop_data['name']}: {resp.text}")
        return None

def create_location(site_id, loc_data):
    # Location slugs must be unique per site? No, unique per parent usually, but API requires unique slug globally or per site?
    # NetBox 3.x+ : Slugs are unique per Site.
    
    # Check existence - Need detailed filter
    resp = requests.get(f"{API_URL}dcim/locations/?site_id={site_id}&slug={loc_data['slug']}", headers=HEADERS, verify=False)
    if resp.json()['count'] > 0:
        return resp.json()['results'][0]['id']

    payload = {
        "name": loc_data['name'],
        "slug": loc_data['slug'],
        "site": site_id,
        "description": loc_data.get('description', '')
    }
    
    resp = requests.post(f"{API_URL}dcim/locations/", headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"  Created Location: {loc_data['name']}")
        return resp.json()['id']
    else:
        print(f"  Failed to create Location {loc_data['name']}: {resp.text}")
        return None

def create_rack(site_id, location_id, rack_name):
    # Racks are unique by name per Site.
    resp = requests.get(f"{API_URL}dcim/racks/?site_id={site_id}&name={rack_name}", headers=HEADERS, verify=False)
    if resp.json()['count'] > 0:
        return resp.json()['results'][0]['id']

    payload = {
        "name": rack_name,
        "site": site_id,
        "location": location_id,
        "status": "active",
        "width": 19,
        "u_height": 42 # Default standard
    }
    
    resp = requests.post(f"{API_URL}dcim/racks/", headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"    Created Rack: {rack_name}")
        return resp.json()['id']
    else:
        print(f"    Failed to create Rack {rack_name}: {resp.text}")
        return None

def main():
    print("Importing POPs...")
    
    tenant_id = get_id("tenancy/tenants", DEFAULT_TENANT_SLUG)
    site_group_id = get_id("dcim/site-groups", DEFAULT_SITE_GROUP_SLUG)
    
    if not tenant_id:
        print(f"Default tenant {DEFAULT_TENANT_SLUG} not found.")
        return
    if not site_group_id:
        print(f"Default site group {DEFAULT_SITE_GROUP_SLUG} not found.")
        return

    for pop in POPS:
        site_id = create_site(pop, tenant_id, site_group_id)
        if site_id:
            for loc in pop['locations']:
                loc_id = create_location(site_id, loc)
                if loc_id:
                    for rack_name in loc['racks']:
                        create_rack(site_id, loc_id, rack_name)
    
    print("POP import completed.")

if __name__ == "__main__":
    main()
