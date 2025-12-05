import asyncio
import httpx
import random
from aarya.shared import utils

async def site(email, client):
    name = "instagram"
    domain = "instagram.com"
    method = "recovery"
    frequent_rate_limit = True

    headers = {
        'User-Agent': utils.get_random_user_agent(),
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.6',
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-IG-App-ID': '936619743392459',
        'X-ASBD-ID': '359341',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Instagram-Ajax': '1', 
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/accounts/password/reset/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=1, i',
    }

    try:
        # 2. GET CSRF Token from the Password Reset page
        # This is necessary because we need a valid session/csrf cookie to send the POST
        freq = await client.get("https://www.instagram.com/accounts/password/reset/", headers=headers)
        
        if freq.status_code == 429:
             return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "others": "Initial 429 Block"}

        token = freq.cookies.get("csrftoken")
        
        if not token:
            # Fallback extraction if cookie is missing (Regex/Split)
            try:
                # Attempt to find csrf_token in the HTML window._sharedData or embedded script
                token = freq.text.split('csrf_token":"')[1].split('"')[0]
            except:
                return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True, "exists": False, "others": "CSRF Token Missing"}

    except Exception as e:
        return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True, "exists": False, "others": f"Init Error: {str(e)}"}

    # 3. POST to Recovery Endpoint
    # We update headers with the token we just grabbed
    headers["X-CSRFToken"] = token
    
    data = {
        'email_or_username': email,
        # 'recaptcha_challenge_field': '' # Only needed if IG triggers a captcha challenge
    }

    try:
        check_req = await client.post(
            "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
            data=data,
            headers=headers,
            cookies=freq.cookies # Crucial: Pass the session cookies from the initial GET
        )
        
        if check_req.status_code == 429:
             return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "others": "429 Rate Limit"}

        try:
            check = check_req.json()
        except:
             return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "others": "Invalid JSON Response"}
        
        # --- ANALYSIS LOGIC ---
        
        # Case 1: Account Does NOT Exist
        # Response: {"message":"No users found","status":"fail"}
        if check.get("status") == "fail" and "No users found" in check.get("message", ""):
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None
            }

        # Case 2: Account Exists (Email Sent)
        # Response: {"title": "Email sent", "status":"ok", ...}
        if check.get("status") == "ok":
            # Optional: Extract partial email from response if available
            # recovery_email = check.get("contact_point", None) 
             return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None
            }
            
        # Case 3: Rate Limit / Soft Block
        msg = check.get("message", "").lower()
        if "wait" in msg or "spam" in msg or "limit" in msg:
             return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True, "exists": False, "others": "Soft Block"
            }

        # Case 4: Other Failures
        return {
            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True, "exists": False, "others": f"API Fail: {check.get('message')}"
        }

    except Exception as e:
        return {
            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True, "exists": False, "others": str(e)
        }