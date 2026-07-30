import json
from aarya.shared import utils

async def site(email, client):
    name = "instagram"
    domain = "instagram.com"
    method = "recovery"
    frequent_rate_limit = False

    import urllib.parse
    import asyncio
    encoded_email = urllib.parse.quote(email, safe='')

    curl_cmd = f"""curl -s 'https://www.instagram.com/api/graphql' \
  --compressed \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'X-FB-Friendly-Name: CAAIGAccountSearchViewQuery' \
  -H 'X-CSRFToken: oXrMxL_C2FSc-Vu448HYJK' \
  -H 'X-IG-App-ID: 936619743392459' \
  -H 'X-IG-Max-Touch-Points: 0' \
  -H 'X-FB-LSD: AdRcDkTe92_OKZ2PfhReOaqjwgg' \
  -H 'X-ASBD-ID: 359341' \
  -H 'Origin: https://www.instagram.com' \
  -H 'Sec-GPC: 1' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://www.instagram.com/accounts/password/reset/' \
  -H 'Cookie: csrftoken=oXrMxL_C2FSc-Vu448HYJK; datr=GwFqaoOQX-_dZnItC0HBFAGO; ig_did=2F4EA602-C56F-4FBD-9855-287970F150C0; wd=958x935; mid=amoBGwAEAAHlVz9ipKvuVhl1P6tm' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  -H 'TE: trailers' \
  --data-raw 'av=0&__d=www&__user=0&__a=1&__req=1c&lsd=AdRcDkTe92_OKZ2PfhReOaqjwgg&__crn=comet.igweb.PolarisCAAIGAccountRecoverySearchRoute&fb_api_caller_class=RelayModern&fb_api_req_friendly_name=CAAIGAccountSearchViewQuery&server_timestamps=true&variables=%7B%22params%22%3A%7B%22search_query%22%3A%22{encoded_email}%22%7D%7D&doc_id=36716895674620546'"""

    try:
        proc = await asyncio.create_subprocess_shell(
            curl_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        
        if not stdout:
            return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "others": "Empty Response"}

        check = json.loads(stdout.decode('utf-8'))
        
        data_block = check.get("data", {}).get("caa_ar_ig_account_search")
        
        if data_block is None:
             return {
                 "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                 "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None
             }
        
        profiles = data_block.get("profiles", [])
        contact_points = data_block.get("contact_points", [])
        
        if profiles or contact_points:
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": True, "emailrecovery": None, "phoneNumber": None, "others": None
            }
            
        error_content = data_block.get("error_content")
        if error_content and "Something went wrong" in error_content.get("description", ""):
             return {"name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "others": "Soft Block"}

        else:
            return {
                "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False, "exists": False, "emailrecovery": None, "phoneNumber": None, "others": None
            }

    except Exception as e:
        return {
            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True, "exists": False, "others": str(e)
        }