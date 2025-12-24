import requests

SITEMAP_URL = "https://rag-book-cwq3n6mkx-sajida-haiders-projects.vercel.app/sitemap.xml"

print("Testing sitemap access with Python requests...")
response = requests.get(SITEMAP_URL)

print(f"Status Code: {response.status_code}")
print(f"Response Length: {len(response.text)}")
print(f"First 500 chars: {response.text[:500]!r}")
print(f"Last 500 chars: {response.text[-500:]!r}")

# Check for authentication indicators
if "Authentication Required" in response.text:
    print("Found 'Authentication Required' in response")
if "auth" in response.text.lower():
    print("Found 'auth' in response (case-insensitive)")

print("\nResponse headers:")
for key, value in response.headers.items():
    print(f"{key}: {value}")