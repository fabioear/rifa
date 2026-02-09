
import httpx
import base64
import asyncio
import os
from dotenv import load_dotenv

# Load env from current directory
load_dotenv()

CLIENT_ID = os.getenv("PIXUP_CLIENT_ID")
CLIENT_SECRET = os.getenv("PIXUP_CLIENT_SECRET")
API_URL = os.getenv("PIXUP_API_URL", "https://api.pixupbr.com")

print(f"Testing Pixup Auth...")
print(f"URL: {API_URL}")
print(f"Client ID: {CLIENT_ID}")
# Show first/last few chars of secret to verify without exposing full log if user shares screen
if CLIENT_SECRET:
    print(f"Client Secret: {CLIENT_SECRET[:4]}...{CLIENT_SECRET[-4:]} (Length: {len(CLIENT_SECRET)})")
else:
    print("Client Secret: NOT FOUND")

async def test_auth():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Missing credentials in .env")
        return

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials"
    }

    print("\nSending request...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/v2/oauth/token",
                headers=headers,
                data=data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("\nSUCCESS! Token retrieved.")
            else:
                print("\nFAILED. Check credentials.")
                
    except Exception as e:
        print(f"\nException: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_auth())
