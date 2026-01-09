import httpx
import os

# Configuration
NETBOX_URL = os.getenv("NETBOX_URL", "http://netbox:8080")
NETBOX_TOKEN = os.getenv("NETBOX_TOKEN", "0123456789abcdef0123456789abcdef01234567")

HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# 1. Define Manufacturers to ensure exist
MANUFACTURERS = [
    {'name': 'Cisco', 'slug': 'cisco'},
    {'name': 'Arista', 'slug': 'arista'},
    {'name': 'Huawei', 'slug': 'huawei'},
    {'name': 'Juniper', 'slug': 'juniper'},
    {'name': 'H3C', 'slug': 'h3c'},
    {'name': 'Fortinet', 'slug': 'fortinet'},
    {'name': 'Ubiquiti', 'slug': 'ubiquiti'},
    {'name': 'MikroTik', 'slug': 'mikrotik'},
    {'name': 'VMware', 'slug': 'vmware'},
]

# 2. Define Mapping: Platform Slug -> Manufacturer Slug
PLATFORM_MAPPINGS = {
    'cisco-ios': 'cisco',
    'cisco-nxos': 'cisco',
    'arista-eos': 'arista',
    'huawei-vrp': 'huawei',
    'juniper-junos': 'juniper',
    'h3c-comware': 'h3c',
    'fortinet-fortios': 'fortinet',
    'ubiquiti-unifi': 'ubiquiti',
    'mikrotik-routeros': 'mikrotik',
    'vmware-esxi': 'vmware'
}

def get_or_create_manufacturer(data):
    # Check if exists
    resp = httpx.get(f"{NETBOX_URL}/api/dcim/manufacturers/", params={"slug": data['slug']}, headers=HEADERS)
    if resp.status_code == 200 and resp.json()['count'] > 0:
        man = resp.json()['results'][0]
        print(f"Manufacturer {data['name']} exists (ID: {man['id']})")
        return man['id']
    
    # Create
    resp = httpx.post(f"{NETBOX_URL}/api/dcim/manufacturers/", json=data, headers=HEADERS)
    if resp.status_code == 201:
        man = resp.json()
        print(f"Created Manufacturer {data['name']} (ID: {man['id']})")
        return man['id']
    else:
        print(f"Error creating manufacturer {data['name']}: {resp.text}")
        return None

def update_platform_manufacturer(platform_slug, manufacturer_id):
    # Get Platform
    resp = httpx.get(f"{NETBOX_URL}/api/dcim/platforms/", params={"slug": platform_slug}, headers=HEADERS)
    if resp.status_code != 200 or resp.json()['count'] == 0:
        print(f"Platform {platform_slug} not found - cannot link.")
        return

    platform = resp.json()['results'][0]
    
    # Check if already linked correctly
    if platform['manufacturer'] and platform['manufacturer']['id'] == manufacturer_id:
        print(f"Platform {platform_slug} is already linked to Manufacturer ID {manufacturer_id}")
        return

    # Patch
    resp = httpx.patch(f"{NETBOX_URL}/api/dcim/platforms/{platform['id']}/", json={'manufacturer': manufacturer_id}, headers=HEADERS)
    if resp.status_code == 200:
        print(f"Updated Platform {platform_slug} -> Linked to Manufacturer ID {manufacturer_id}")
    else:
        print(f"Error updating platform {platform_slug}: {resp.text}")

def main():
    print(f"Connecting to {NETBOX_URL}")
    
    # 1. Ensure Manufacturers
    man_ids = {}
    for m in MANUFACTURERS:
        mid = get_or_create_manufacturer(m)
        if mid:
            man_ids[m['slug']] = mid

    # 2. Link Platforms
    for p_slug, m_slug in PLATFORM_MAPPINGS.items():
        if m_slug in man_ids:
            update_platform_manufacturer(p_slug, man_ids[m_slug])
        else:
            print(f"Skipping update for {p_slug}: Manufacturer {m_slug} ID not found.")

if __name__ == "__main__":
    main()
