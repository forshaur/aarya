from aarya.shared import utils
from bs4 import BeautifulSoup

async def site(email, client):
    name = "amazon"
    domain = "amazon.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": utils.get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # 1. Get the Login Page to fetch CSRF tokens/hidden inputs
        url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F_encoding%3DUTF8%26ref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
        
        req = await client.get(url, headers=headers, follow_redirects=True)
        
        # Early Captcha Check on GET
        if "captcha" in req.text.lower() or "enter the characters" in req.text.lower():
             return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None,
                "others": "Captcha on GET"
            }

        body = BeautifulSoup(req.text, 'html.parser')
        
        # Parse all form inputs (appActionToken, etc.)
        data = dict([(x["name"], x["value"]) for x in body.select('form input') if ('name' in x.attrs and 'value' in x.attrs)])
        data["email"] = email
        
        # 2. Post the Email
        req = await client.post('https://www.amazon.com/ap/signin/', data=data, headers=headers)
        body = BeautifulSoup(req.text, 'html.parser')

        
        # CASE 1: Account Exists (Password Missing Alert)
        if body.find("div", {"id": "auth-password-missing-alert"}):
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None
            }
        
        # CASE 2: Account Does NOT Exist (Invalid Email Alert)
        # We explicitly check for the error message div
        elif body.find("div", {"id": "auth-email-invalid-claim-alert"}):
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None
            }

        # CASE 3: Captcha or WAF (Neither alert found)
        # If we are here, Amazon served us a page that isn't the standard login flow (likely a Captcha)
        else:
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, 
                "others": "Captcha/Layout Change Detected"
            }

    except Exception as e:
        return {
            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None,
            "others": str(e)
        }