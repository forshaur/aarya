import json
from aarya.shared import utils

async def site(email, client):
    name = "wattpad"
    domain = "wattpad.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        'User-Agent': utils.get_random_user_agent(),
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.wattpad.com',
        'Referer': 'https://www.wattpad.com/signup',
    }

    try:        
        params = {'email': email}
        url = 'https://www.wattpad.com/api/v3/users/validate'
        
        req = await client.get(url, headers=headers, params=params)
        
        # print(f"Wattpad returned: {req.status_code} - {req.text}")

        # Case 1: Account Exists
        if req.status_code == 409:
            return {
                "name": name, "domain": domain, "exists": True, "rateLimit": False,
                "others": "Status 409 (Conflict)"
            }

        # Case 2: Check JSON Content (Works for 200 or 400)
        if req.status_code in [200, 400]:
            data = req.json()
            
            # If api returns specific conflict message (Language agnostic check)
            # API usually returns: {"code":1002, "message":"User already exists"}
            if data.get('code') == 1002 or "already" in str(data).lower() or "exists" in str(data).lower():
                 return {
                    "name": name, "domain": domain, "exists": True, "rateLimit": False,
                    "others": None
                }
            
            # If success (meaning email is available/valid, so user DOES NOT exist)
            if data.get('message') == "OK" or data.get('code') == 200:
                return {
                    "name": name, "domain": domain, "exists": False, "rateLimit": False,
                    "others": None
                }

        # Case 3: Rate Limits or Blocks
        if req.status_code in [403, 429]:
             return {
                "name": name, "domain": domain, "exists": False, "rateLimit": True,
                "others": f"Blocked {req.status_code}"
            }

        # Case 4: Unexpected status
        return {
            "name": name, "domain": domain, "exists": False, "rateLimit": True,
            "others": f"Unexpected Status {req.status_code}"
        }

    except Exception as e:
        return {
            "name": name, "domain": domain, "exists": False, "rateLimit": False,
            "others": str(e)
        }