import asyncio
import httpx
import random
import string
from shared import utils

async def site(email, client):
    name = "instagram"
    domain = "instagram.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        'User-Agent': utils.get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # GET TOKEN 
        freq = await client.get("https://www.instagram.com/accounts/emailsignup/", headers=headers)

        # 429 CHECK FOR GET REQUEST 
        if freq.status_code == 429:
            wait_seconds = int(freq.headers.get("Retry-After", 60)) 
            print(f"[!] 429 on GET request. Waiting for {wait_seconds} seconds...")
            await asyncio.sleep(wait_seconds)
            # Retry the request once
            freq = await client.get("https://www.instagram.com/accounts/emailsignup/", headers=headers)
        
        # If it still fails, raise an error
        if freq.status_code != 200:
            raise httpx.HTTPStatusError(f"Failed to get page: {freq.status_code}", request=freq.request, response=freq)

        token = freq.cookies.get("csrftoken")
        if not token:
            raise Exception("Could not find CSRF token in cookies. Page is likely a login/CAPTCHA.")

    except Exception as e:
        return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": True, "exists": False, "emailrecovery": None,
                    "phoneNumber": None, "others": f"Token Error: {str(e)}"}

    # POST DATA 
    data = {
        'email': email,
        'username': ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(random.randint(6, 30))),
        'first_name': '',
        'opt_into_one_tap': 'false'
    }
    
    headers['X-CSRFToken'] = token
    headers['Referer'] = 'https://www.instagram.com/accounts/emailsignup/'
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['X-Requested-With'] = 'XMLHttpRequest'

    try:
        check_req = await client.post(
            "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/",
            data=data, headers=headers
        )

        # 429 CHECK FOR POST REQUEST 
        if check_req.status_code == 429:
            wait_seconds = int(check_req.headers.get("Retry-After", 60))
            print(f"[!] 429 on POST request. Waiting for {wait_seconds} seconds...")
            await asyncio.sleep(wait_seconds)
            # Retry the request once
            check_req = await client.post(
                "https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/",
                data=data, headers=headers
            )
        
        # If it's still 429, fail gracefully
        if check_req.status_code == 429:
             return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": True, "exists": False, "emailrecovery": None,
                    "phoneNumber": None, "others": "429: Still rate limited after waiting."}

        check = check_req.json()
        
        # ANALYZE RESPONSE 
        if check.get("status") != "fail":
            if 'errors' in check and 'email' in check["errors"]:
                error_code = check["errors"]["email"][0]["code"]
                if error_code == "email_is_taken":
                     return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                            "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None}
            
            if "email_sharing_limit" in str(check.get("errors", "")):
                 return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                            "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None}
            
            return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None}
        else:
            return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": "API Status Fail"}

    except Exception as e:
        return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": str(e)}

