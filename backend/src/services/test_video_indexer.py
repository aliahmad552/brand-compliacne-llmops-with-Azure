import os
import requests
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

def test_environment():
    print("🔎 Checking ENV Variables...")
    required = [
        "AZURE_VI_NAME",
        "AZURE_VI_LOCATION",
        "AZURE_VI_ACCOUNT_ID",
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_RESOURCE_GROUP"
    ]
    
    for var in required:
        value = os.getenv(var)
        print(f"{var}: {'✅ OK' if value else '❌ MISSING'}")


def test_arm_token():
    print("\n🔐 Testing ARM Token...")
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default")
    print("✅ ARM Token acquired")


def test_vi_account_token():
    print("\n🎥 Testing Video Indexer Account Token...")
    
    credential = DefaultAzureCredential()
    arm_token = credential.get_token("https://management.azure.com/.default").token
    
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    vi_name = os.getenv("AZURE_VI_NAME")

    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.VideoIndexer/accounts/{vi_name}"
        f"/generateAccessToken?api-version=2024-01-01"
    )

    headers = {"Authorization": f"Bearer {arm_token}"}
    payload = {"permissionType": "Contributor", "scope": "Account"}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("✅ Video Indexer Account Token Generated")
    else:
        print("❌ FAILED")
        print(response.text)


def test_vi_account_access():
    print("\n🌍 Testing VI API Access...")
    
    credential = DefaultAzureCredential()
    arm_token = credential.get_token("https://management.azure.com/.default").token

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    vi_name = os.getenv("AZURE_VI_NAME")
    location = os.getenv("AZURE_VI_LOCATION")
    account_id = os.getenv("AZURE_VI_ACCOUNT_ID")

    # Generate account token
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}"
        f"/providers/Microsoft.VideoIndexer/accounts/{vi_name}"
        f"/generateAccessToken?api-version=2024-01-01"
    )

    headers = {"Authorization": f"Bearer {arm_token}"}
    payload = {"permissionType": "Contributor", "scope": "Account"}

    response = requests.post(url, headers=headers, json=payload)
    vi_token = response.json().get("accessToken")

    # Test API call
    api_url = f"https://api.videoindexer.ai/{location}/Accounts/{account_id}"
    headers = {"Authorization": f"Bearer {vi_token}"}

    r = requests.get(api_url, headers=headers)

    print("Status Code:", r.status_code)
    print("Response:", r.text[:300])


print("VI Location:", self.location)
print("VI Account ID:", self.account_id)
print("Tenant ID:", self.tenant_id)

if __name__ == "__main__":
    test_environment()
    test_arm_token()
    test_vi_account_token()
    test_vi_account_access()

