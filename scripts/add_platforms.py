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

# Platform definitions based on user's context (MikroTik, Dell, Fortinet, H3C, Ubiquiti, Juniper)
PLATFORMS = [
    # Network OS
    {'name': 'MikroTik RouterOS', 'slug': 'mikrotik-routeros', 'manufacturer_slug': 'mikrotik', 'description': 'MikroTik RouterOS'},
    {'name': 'Cisco IOS', 'slug': 'cisco-ios', 'manufacturer_slug': 'cisco', 'description': 'Cisco IOS'},
    {'name': 'Cisco NX-OS', 'slug': 'cisco-nxos', 'manufacturer_slug': 'cisco', 'description': 'Cisco NX-OS'},
    {'name': 'Juniper Junos', 'slug': 'juniper-junos', 'manufacturer_slug': 'juniper', 'description': 'Juniper Junos'},
    {'name': 'Arista EOS', 'slug': 'arista-eos', 'manufacturer_slug': 'arista', 'description': 'Arista EOS'},
    {'name': 'H3C Comware', 'slug': 'h3c-comware', 'manufacturer_slug': 'h3c', 'description': 'H3C Comware'},
    {'name': 'Huawei VRP', 'slug': 'huawei-vrp', 'manufacturer_slug': 'huawei', 'description': 'Huawei VRP'},
    {'name': 'Fortinet FortiOS', 'slug': 'fortinet-fortios', 'manufacturer_slug': 'fortinet', 'description': 'Fortinet FortiOS'},
    {'name': 'Ubiquiti UniFi', 'slug': 'ubiquiti-unifi', 'manufacturer_slug': 'ubiquiti', 'description': 'Ubiquiti UniFi'},
    
    # Server & Virtualization
    {'name': 'Linux', 'slug': 'linux', 'description': 'Generic Linux'},
    {'name': 'Windows Server', 'slug': 'windows-server', 'description': 'Windows Server'},
    {'name': 'VMware ESXi', 'slug': 'vmware-esxi', 'description': 'VMware ESXi'},
    {'name': 'Proxmox VE', 'slug': 'proxmox-ve', 'description': 'Proxmox VE'},
]

def get_manufacturer_id(slug):
    resp = httpx.get(f"{NETBOX_URL}/api/dcim/manufacturers/", params={"slug": slug}, headers=HEADERS)
    if resp.status_code == 200:
        results = resp.json().get('results', [])
        if results:
            return results[0]['id']
    return None

def create_platform(platform_data):
    # Prepare payload
    payload = {
        "name": platform_data['name'],
        "slug": platform_data['slug'],
        "description": platform_data.get('description', '')
    }
    
    # Try to link to manufacturer if provided
    if 'manufacturer_slug' in platform_data:
        man_id = get_manufacturer_id(platform_data['manufacturer_slug'])
        if man_id:
            payload['manufacturer'] = man_id
        else:
            print(f"Warning: Manufacturer {platform_data['manufacturer_slug']} not found for {platform_data['name']}")

    # Check if exists
    resp = httpx.get(f"{NETBOX_URL}/api/dcim/platforms/", params={"slug": platform_data['slug']}, headers=HEADERS)
    if resp.status_code == 200:
        results = resp.json().get('results', [])
        if results:
            print(f"Skipping {platform_data['name']} (already exists)")
            return

    # Create
    resp = httpx.post(f"{NETBOX_URL}/api/dcim/platforms/", json=payload, headers=HEADERS)
    if resp.status_code == 201:
        print(f"Created {platform_data['name']}")
    else:
        print(f"Failed to create {platform_data['name']}: {resp.text}")

def main():
    print(f"Connecting to NetBox at {NETBOX_URL}")
    for platform in PLATFORMS:
        create_platform(platform)

if __name__ == "__main__":
    main()
