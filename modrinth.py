import httpx

# Replace 'YOUR_PAT_HERE' with your actual personal access token
token = 'mrp_QzOKsziGrTaVFuMjH3uYugmanE0ROWs3mukYYCJVfzApWUHbNj4tHdz6rW3l'
url = 'https://api.modrinth.com/api/v2'

headers = {
    'Authorization': f'mrp {token}',
}

try:
    # Make a GET request to the Modrinth API to fetch mods
    with httpx.Client() as client:
        response = client.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        mods = response.json()
        print("List of Mods:")
        for mod in mods:
            print(f"- {mod['title']} ({mod['id']})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"An error occurred: {e}")
