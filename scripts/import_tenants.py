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

# Company Data Definition - Tenants only
TENANTS = [
    {
        "name": "上海万联信息科技有限公司",
        "slug": "shanghai-wanlian",
        "description": "Floor 24, No. 59, Lane 380, Tianyaoqiao Road, Xuhui District, Shanghai"
    },
    {
        "name": "上海元协力营人工智能科技有限公司",
        "slug": "shanghai-yuanxielying",
        "description": "上海市普陀区云岭西路600弄5号3层"
    },
    {
        "name": "Allied Business Cloud Limited",
        "slug": "allied-business-cloud",
        "description": "萬聯商用雲服務有限公司 - Flat A, 3/F., JCG Building, 16 Mongkok Road, Kowloon, Hong Kong"
    },
    {
        "name": "AlliedBusiness Co., Ltd.",
        "slug": "alliedbusiness-jp",
        "description": "アライドビジネス株式会社 - Ginza 1-12-4 NE BLD 7F, Chiyoda, Tokyo"
    },
    {
        "name": "TeraTeams Inc.",
        "slug": "terateams-inc",
        "description": "2048 E Villa ST APT 11, Pasadena, CA 91107"
    }
]

def create_tenant(tenant_data):
    slug = tenant_data['slug']
    name = tenant_data['name']
    
    # Check if tenant exists
    resp = requests.get(f"{API_URL}tenancy/tenants/?slug={slug}", headers=HEADERS, verify=False)
    if resp.json()['count'] > 0:
        print(f"Tenant '{name}' already exists.")
        return resp.json()['results'][0]['id']
    
    # Create tenant
    payload = {
        "name": name,
        "slug": slug,
        "description": tenant_data.get('description', '')
    }
    resp = requests.post(f"{API_URL}tenancy/tenants/", headers=HEADERS, json=payload, verify=False)
    if resp.status_code == 201:
        print(f"Created Tenant: {name}")
        return resp.json()['id']
    else:
        print(f"Error creating tenant {name}: {resp.text}")
        return None

def main():
    print("Importing tenants...")
    for tenant in TENANTS:
        create_tenant(tenant)
    print("Tenant import completed.")

if __name__ == "__main__":
    main()
