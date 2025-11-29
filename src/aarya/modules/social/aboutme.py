import re
from shared import utils

async def site(email, client):
    name = "aboutme"
    domain = "about.me"
    method = "register"
    frequent_rate_limit = False
    
    useragent = utils.get_random_user_agent()
    
    # 1. Get Auth Token
    try:
        reqToken = await client.get("https://about.me/signup", headers={'User-Agent': useragent})
        
        if reqToken.status_code == 403:
             return {"name": name, "domain": domain, "exists": False, "rateLimit": True, "others": "Cloudflare Block (403)"}

        # [fix]: Use regex to find token safely
        match = re.search(r'"AUTH_TOKEN":"(.*?)"', reqToken.text)
        if match:
            auth_token = match.group(1)
        else:
            return {"name": name, "domain": domain, "exists": False, "rateLimit": False, "others": "Could not find AUTH_TOKEN"}

    except Exception as e:
        return {"name": name, "domain": domain, "exists": False, "rateLimit": False, "others": f"Init Error: {str(e)}"}

    headers = {
        'User-Agent': useragent,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Auth-Token': auth_token,
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://about.me',
        'Referer': 'https://about.me/signup',
    }

    # [fix]: Payload as dictionary
    payload = {
        "user_name": "",
        "first_name": "",
        "last_name": "",
        "email_address": email,
        "signup": {"id": "signup", "step": "email", "method": "email"}
    }

    try:
        response = await client.post('https://about.me/n/signup', headers=headers, json=payload)
        
        # 409 usually means Conflict (User exists)
        if response.status_code == 409:
            return {"name": name, "domain": domain, "exists": True, "rateLimit": False, "others": None}
        
        elif response.status_code == 200:
            return {"name": name, "domain": domain, "exists": False, "rateLimit": False, "others": None}
        
        elif response.status_code == 429:
             return {"name": name, "domain": domain, "exists": False, "rateLimit": True, "others": "Too Many Requests"}
             
        else:
            # Check JSON for specific error messages even if status isn't 409
            try:
                data = response.json()
                if "taken" in str(data) or "exists" in str(data):
                     return {"name": name, "domain": domain, "exists": True, "rateLimit": False, "others": None}
            except:
                pass
                
            return {"name": name, "domain": domain, "exists": False, "rateLimit": True, "others": f"Status {response.status_code}"}

    except Exception as e:
        return {"name": name, "domain": domain, "exists": False, "rateLimit": False, "others": str(e)}