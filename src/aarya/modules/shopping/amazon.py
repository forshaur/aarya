from aarya.shared import utils
from bs4 import BeautifulSoup

async def site(email, client):
    name = "amazon"
    domain = "amazon.com"
    method = "login"
    frequent_rate_limit = False

    headers = {"User-Agent": utils.get_random_user_agent()}
    
    try:
        # Step 1: GET the sign-in page to capture necessary form tokens
        url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F_encoding%3DUTF8%26ref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
        req = await client.get(url, headers=headers, follow_redirects=True)
        
        body = BeautifulSoup(req.text, 'html.parser')
        
        # Step 2: Extract all hidden input fields required for the POST request
        data = dict([(x["name"], x["value"]) for x in body.select('form input') 
                     if ('name' in x.attrs and 'value' in x.attrs)])
        data["email"] = email
        
        req = await client.post('https://www.amazon.com/ap/signin/', data=data, headers=headers)
        body = BeautifulSoup(req.text, 'html.parser')

        if body.find("div", {"id": "auth-password-missing-alert"}):
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None
            }
        else:
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None
            }

    except Exception:
        return {
            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None
        }
