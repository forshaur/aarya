from aarya.shared import utils
import re
import asyncio

def generate_flipkart_headers(user_agent: str) -> dict:    
    headers = {
        'User-Agent': user_agent,
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'Origin': 'https://www.flipkart.com',
        'Referer': 'https://www.flipkart.com/',
        'X-User-Agent': user_agent + ' FKUA/website/42/website/Desktop',
        # Removed complex sec-ch-ua headers as they often trigger WAFs 
        # if they don't match the TLS handshake perfectly.
    }
    return headers

async def site(email: str, client):
    name = "flipkart"
    domain = "flipkart.com"
    method = "login"
    frequent_rate_limit = True  

    headers = generate_flipkart_headers(utils.get_random_user_agent())
    
    # API endpoint
    base_api_url = "https://{dc_id}.rome.api.flipkart.com/api/6/user/signup/status"
    payload = {"loginId": [email], "supportAllStates": True}
    
    try:
        # 1. Get the main page to set cookies (CSRF etc.)
        await client.get("https://www.flipkart.com/", headers=headers, timeout=10)
        
        # 2. Slight human-like pause
        await asyncio.sleep(1.5)

        # 3. Hit the API
        url_to_try = base_api_url.format(dc_id='1')
        response = await client.post(url_to_try, json=payload, headers=headers, timeout=10)

        # Handle the specific "DC Change" error (Data Center redirect)
        if response.status_code == 406:
            url_to_try = base_api_url.format(dc_id='2')
            response = await client.post(url_to_try, json=payload, headers=headers, timeout=10)

        
        if response.status_code == 200:
            data = response.json()
            user_details = data.get('RESPONSE', {}).get('userDetails', {})
            # Flipkart returns the status keyed by the email address
            status = user_details.get(email, 'NOT_FOUND_IN_JSON')
            
            if status == "VERIFIED":
                return {
                    "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None
                }
            else:
                return {
                    "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None
                }
        
        # Explicit Rate Limit Handling
        elif response.status_code == 429:
             return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, 
                "others": "Too Many Requests (429)"
            }
            
        # Any other error (403, 500, etc.)
        else:
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None,
                "others": f"Block/Error [{response.status_code}]"
            }

    except Exception as e:
        return {
            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None,
            "others": str(e)
        }