from aarya.shared import utils
import random
import re

def generate_flipkart_headers(user_agent_list:list)->dict:    
    user_agent = random.choice(user_agent_list)
    print(user_agent)
    platform = '"Unknown"'#Parse the user-agent to generate consistent headers
    is_mobile = "?0"
    sec_ch_ua = None 

    # --- Find Platform ---
    if "Windows NT" in user_agent:
        platform = '"Windows"'
    elif "Macintosh" in user_agent or "Mac OS X" in user_agent:
        platform = '"macOS"'
    elif "Linux" in user_agent and "Android" not in user_agent:
        platform = '"Linux"'
    elif "iPhone" in user_agent:
        platform = '"iOS"'
        is_mobile = "?1"
    elif "Android" in user_agent:
        platform = '"Android"'
        is_mobile = "?1"
    
    # Catch any other "Mobile" string
    if "Mobile" in user_agent and is_mobile == "?0":
        is_mobile = "?1"

    # --- Find Browser/Brand for sec-ch-ua (Client Hints) ---
    crios_match = re.search(r'CriOS/(\d+)', user_agent)
    chrome_match = re.search(r'Chrome/(\d+)', user_agent)
    firefox_match = re.search(r'Firefox/(\d+)', user_agent)
    
    if crios_match:
        ver = crios_match.group(1)
        sec_ch_ua = f'"Chromium";v="{ver}", "Google Chrome";v="{ver}", "Not_A Brand";v="99"'
    elif chrome_match:
        ver = chrome_match.group(1)
        sec_ch_ua = f'"Chromium";v="{ver}", "Google Chrome";v="{ver}", "Not_A Brand";v="99"'
    elif firefox_match:
        pass
    else:
        pass

    headers = {
        'user-agent': user_agent,
        'x-user-agent': user_agent + ' FKUA/website/42/website/Desktop',
        'sec-ch-ua-mobile': is_mobile,
        'sec-ch-ua-platform': platform,
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.flipkart.com',
        'referer': 'https://www.flipkart.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'priority': 'u=1, i',
    }
    
    if sec_ch_ua:
        headers['sec-ch-ua'] = sec_ch_ua
    return headers


async def site(email: str, client):
    name="flipkart"
    domain="flipkart.com"
    method="login"
    frequent_rate_limit=False


    headers = generate_flipkart_headers(utils.get_random_user_agent())
    base_api_url = "https://{dc_id}.rome.api.flipkart.com/api/6/user/signup/status"
    payload = {"loginId": [email], "supportAllStates": True}
    try:
        await client.get("https://www.flipkart.com/", headers=headers,timeout=10)
        url_to_try = base_api_url.format(dc_id='1')
        response = await client.post(url_to_try, json=payload, headers=headers,timeout=10)

        if response.status_code == 406 and 'DC Change' in response.text:
            url_to_try = base_api_url.format(dc_id='2')
            response = await client.post(url_to_try, json=payload, headers=headers,timeout=10)

        if response.status_code == 200:
            user_details = response.json().get('RESPONSE', {}).get('userDetails', {})
            status = user_details.get(email, 'NOT_FOUND_IN_JSON') # Get status for the specific email
            if status=="VERIFIED":
                return {"name":name,"domain":domain,"method":method,"frquent_rate_limit":frequent_rate_limit,
                "status_code": response.status_code,
                "exists":True,
                "rateLimit":False,
                "emailrecovery":None,
                "phoneNumber":None,
                "others":None}
            else:
                return {"name":name,"domain":domain,"method":method,"frquent_rate_limit":frequent_rate_limit,
                "exists":False,
                "rateLimit":False,
                "emailrecovery":None,
                "phoneNumber":None,
                "others":None}
                
        else:
            return {"name":name,"domain":domain,"method":method,"frquent_rate_limit":frequent_rate_limit,
                "exists":False,
                "rateLimit":True,
                "emailrecovery":None,
                "phoneNumber":None,
                "others":None}
    except Exception as e:
        return {"name":name,"domain":domain,"method":method,"frquent_rate_limit":frequent_rate_limit,
                "exists":False,
                "rateLimit":True,
                "emailrecovery":None,
                "phoneNumber":None,
                "others":str(e)}
