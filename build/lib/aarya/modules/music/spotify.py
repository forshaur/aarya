from aarya.shared import utils

async def site(email,client):
    name = "spotify"
    domain = "spotify.com"
    method= "register"
    frequent_rate_limit=True

    headers = {
        'User-Agent': utils.get_random_user_agent(),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    params = {
        'validate': '1',
        'email': email,
    }
    try:
        req = await client.get(
            'https://spclient.wg.spotify.com/signup/public/v1/account',
            headers=headers,
            params=params)
        if req.json()["status"] == 1:
            return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False,
                        "emailrecovery": None,
                        "phoneNumber": None,
                        "others": None}
        elif req.json()["status"] == 20:
            return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True,
                        "emailrecovery": None,
                        "phoneNumber": None,
                        "others": None}
        else:
            return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": True,
                        "exists": None,
                        "emailrecovery": None,
                        "phoneNumber": None,
                        "others": None}
    except Exception:
        return {"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": True,
                    "exists": None,
                    "emailrecovery": None,
                    "phoneNumber": None,
                    "others": None}