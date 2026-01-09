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

ROLES = [
    # Networking
    {'name': 'Router', 'slug': 'router', 'color': 'ff9800', 'vm_role': False, 'description': '路由器 (广域网/边界)'},
    {'name': 'Firewall', 'slug': 'firewall', 'color': 'f44336', 'vm_role': False, 'description': '防火墙 (安全网关)'},
    {'name': 'Core Switch', 'slug': 'core-switch', 'color': 'd32f2f', 'vm_role': False, 'description': '核心交换机 (Spine/Core)'},
    {'name': 'Distribution Switch', 'slug': 'distribution-switch', 'color': '2196f3', 'vm_role': False, 'description': '汇聚交换机 (Leaf/Distribution)'},
    {'name': 'Access Switch', 'slug': 'access-switch', 'color': '03a9f4', 'vm_role': False, 'description': '接入交换机 (TOR/Access)'},
    {'name': 'Management Switch', 'slug': 'management-switch', 'color': '9c27b0', 'vm_role': False, 'description': '带外管理交换机 (OOB)'},
    {'name': 'Load Balancer', 'slug': 'load-balancer', 'color': '4caf50', 'vm_role': False, 'description': '负载均衡器'},
    
    # Compute
    {'name': 'Server', 'slug': 'server', 'color': '00bcd4', 'vm_role': True, 'description': '物理服务器'},

    # Power
    {'name': 'PDU', 'slug': 'pdu', 'color': '795548', 'vm_role': False, 'description': '配电单元'},
    {'name': 'UPS', 'slug': 'ups', 'color': '5d4037', 'vm_role': False, 'description': '不间断电源'},

    # Wireless
    {'name': 'Wireless Controller', 'slug': 'wireless-controller', 'color': 'ffeb3b', 'vm_role': False, 'description': '无线控制器 (AC)'},
    {'name': 'Access Point', 'slug': 'access-point', 'color': 'fbc02d', 'vm_role': False, 'description': '无线接入点 (AP)'},
]

def create_role(role_data):
    # Check if exists
    resp = httpx.get(f"{NETBOX_URL}/api/dcim/device-roles/", params={"slug": role_data['slug']}, headers=HEADERS)
    if resp.status_code == 200:
        results = resp.json().get('results', [])
        if results:
            print(f"Skipping {role_data['name']} (already exists)")
            return

    # Create
    resp = httpx.post(f"{NETBOX_URL}/api/dcim/device-roles/", json=role_data, headers=HEADERS)
    if resp.status_code == 201:
        print(f"Created {role_data['name']}")
    else:
        print(f"Failed to create {role_data['name']}: {resp.text}")

def main():
    print(f"Connecting to NetBox at {NETBOX_URL}")
    for role in ROLES:
        create_role(role)

if __name__ == "__main__":
    main()
