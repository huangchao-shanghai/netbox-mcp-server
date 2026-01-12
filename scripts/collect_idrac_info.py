import requests
import json
import urllib3
import argparse
from getpass import getpass

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IDRACCollector:
    def __init__(self, ip, username, password):
        self.base_url = f"https://{ip}/redfish/v1"
        self.auth = (username, password)
        self.headers = {'Content-Type': 'application/json'}
        self.system_id = "System.Embedded.1"  # Default for Dell

    def get(self, endpoint):
        """通用 GET 请求"""
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                auth=self.auth,
                headers=self.headers,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            return {}

    def collect_system_info(self):
        """获取系统基础信息"""
        data = self.get(f"/Systems/{self.system_id}")
        print("\n--- 1. 基础信息 ---")
        print(f"Hostname:     {data.get('HostName', 'N/A')}")
        print(f"Model:        {data.get('Model', 'N/A')}")
        print(f"Serial (ST):  {data.get('SKU', 'N/A')}") # Dell usually puts ST in SKU or SerialNumber
        if data.get('SerialNumber'):
             print(f"Serial No:    {data.get('SerialNumber')}")
        print(f"Power State:  {data.get('PowerState', 'N/A')}")
        print(f"Bios Version: {data.get('BiosVersion', 'N/A')}")

    def collect_processors(self):
        """获取 CPU 信息"""
        data = self.get(f"/Systems/{self.system_id}/Processors")
        members = data.get("Members", [])
        print("\n--- 2. CPU 信息 ---")
        for member in members:
            # Need to fetch details for each member
            detail = self.get(member['@odata.id'].replace('/redfish/v1', ''))
            print(f"CPU: {detail.get('Model', 'Unknown')} | Cores: {detail.get('TotalCores', 'N/A')} | Socket: {detail.get('Socket', 'N/A')}")

    def collect_memory(self):
        """获取内存信息"""
        data = self.get(f"/Systems/{self.system_id}/Memory")
        members = data.get("Members", [])
        total_gib = 0
        count = 0
        dimm_size = 0
        
        for member in members:
            # Details require individual fetches usually, but sometimes summary is enough.
            # Dell usually lists all DIMMs.
            detail = self.get(member['@odata.id'].replace('/redfish/v1', ''))
            capacity_mib = detail.get('CapacityMiB', 0)
            if capacity_mib and capacity_mib > 0:
                count += 1
                total_gib += capacity_mib / 1024
                dimm_size = capacity_mib / 1024 # Assuming standard uniform DIMMs

        print("\n--- 3. 内存信息 ---")
        print(f"Total Memory: {int(total_gib)} GB")
        print(f"DIMM Count:   {count} x {int(dimm_size)} GB")

    def collect_storage(self):
        """获取物理磁盘信息 (Dell 特有扩展或标准 Storage)"""
        # Dell often uses /Systems/System.Embedded.1/Storage/Drives or similar
        # A clearer view on Dell is often via the SimpleStorage or Storage collections
        data = self.get(f"/Systems/{self.system_id}/Storage")
        members = data.get("Members", [])
        
        print("\n--- 4. 磁盘信息 ---")
        for member in members:
            storage_detail = self.get(member['@odata.id'].replace('/redfish/v1', ''))
            drives = storage_detail.get('Drives', [])
            for drive_link in drives:
                drive = self.get(drive_link['@odata.id'].replace('/redfish/v1', ''))
                size_bytes = drive.get('CapacityBytes', 0)
                size_gb = size_bytes / (1024**3)
                print(f"Disk: {drive.get('Model', 'Unknown')} | {size_gb:.2f} GB | Type: {drive.get('MediaType', 'N/A')} | Protocol: {drive.get('Protocol', 'N/A')}")

    def collect_network(self):
        """获取网卡 MAC 地址"""
        data = self.get(f"/Systems/{self.system_id}/EthernetInterfaces")
        members = data.get("Members", [])
        
        print("\n--- 5. 网络接口 ---")
        for member in members:
            nic = self.get(member['@odata.id'].replace('/redfish/v1', ''))
            print(f"Interface: {nic.get('Id', 'N/A')} ({nic.get('Name', 'N/A')})")
            print(f"  MAC Address: {nic.get('MACAddress', 'N/A')}")
            print(f"  Speed:       {nic.get('SpeedMbps', 'N/A')} Mbps")
            print(f"  Status:      {nic.get('Status', {}).get('State', 'N/A')}")

def main():
    parser = argparse.ArgumentParser(description="Collect Hardware Info from Dell iDRAC via Redfish")
    parser.add_argument("ip", help="iDRAC IP Address")
    parser.add_argument("-u", "--username", default="root", help="iDRAC Username (default: root)")
    args = parser.parse_args()

    password = getpass(f"Enter password for {args.username}@{args.ip}: ")

    collector = IDRACCollector(args.ip, args.username, password)
    
    print(f"Connecting to {args.ip}...")
    collector.collect_system_info()
    collector.collect_processors()
    collector.collect_memory()
    collector.collect_storage()
    collector.collect_network()

if __name__ == "__main__":
    main()
