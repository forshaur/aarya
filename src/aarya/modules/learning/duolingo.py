from aarya.shared import utils


async def site(email, client):
    name = "duolingo"
    domain = "duolingo.com"
    method= "other"
    frequent_rate_limit=False



    headers = {
'authority': 'www.duolingo.com',
'method': 'GET',
'path': '/2017-06-30/users?email=' +email,
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, br, zstd',
'Accept-Language': 'en-US,en;q=0.8',
'User-Agent': utils.get_random_user_agent(),
}

    try:
        req = await client.get(
            "https://www.duolingo.com/2017-06-30/users?email="+email,)
        if req.json()["users"]:
            return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True,
                        "emailrecovery": None,
                        "phoneNumber": None,
                        "others": None}
        else:
            return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False,
                        "emailrecovery": None,
                        "phoneNumber": None,
                        "others": None}
    except Exception:
        return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": True,
                    "exists": False,
                    "emailrecovery": None,
                    "phoneNumber": None,
                    "others": None}