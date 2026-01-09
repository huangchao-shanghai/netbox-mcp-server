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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Site Group Data
SITE_GROUPS = [
    {
        "name": "Edge Nodes",
        "slug": "edge-nodes",
        "description": "边缘节点"
    },
    {
        "name": "Data Center",
        "slug": "data-center",
        "description": "数据中心"
    }
]

def create_site_group(group_data):
    slug = group_data['slug']
    name = group_data['name']
    
    # Check if exists
    resp = requests.get(f"{API_URL}dcim/site-groups/?slug={slug}", headers=HEADERS, verify=False)
    if resp.json()['count'] > 0:
        print(f"Site Group '{name}' already exists.")
        return resp.json()['results'][0]['id']
    
    # Create
    payload = {
        "name": name,
        "slug": slug,
        "description": group_data['description']
    }
    resp = requests.post(f"{API_URL}dcim/site-groups/", headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"Created Site Group: {name}")
        return resp.json()['id']
    else:
        print(f"Error creating site group {name}: {resp.text}")
        return None

def main():
    print("Importing Site Groups...")
    for group in SITE_GROUPS:
        create_site_group(group)
    print("Site Group import completed.")

if __name__ == "__main__":
    main()
