import urllib.request
import json
import ssl

def test_login():
    url = "http://localhost:8000/api/auth/login"
    payload = {
        "username": "admin", # Default user from seed.py
        "password": "admin123" # Default password from seed.py
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        print(f"Testing Login API: {url}")
        print(f"Payload: {payload}")
        
        # Create context that ignores SSL verification if needed (localhost usually fine)
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, context=context) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            
            print(f"Status Code: {status_code}")
            print(f"Response: {response_body}")
            
            if status_code == 200:
                print("LOGIN SUCCESSFUL!")
            else:
                print("LOGIN FAILED (Unexpected Status)")

    except urllib.request.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}")
    except urllib.request.URLError as e:
        print(f"URL Error: {e.reason}")
        print("Is the server running on localhost:8000?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
