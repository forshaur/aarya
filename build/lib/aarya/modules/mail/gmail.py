import browser_cookie3
import time
import hashlib
import re
import os
import shutil
import glob
import sys

ORIGIN = "https://mail.google.com"
API_URL = "https://peoplestack-pa.clients6.google.com/$rpc/peoplestack.PeopleStackAutocompleteService/Autocomplete"
API_KEY = "AIzaSyBm7aDMG9actsWSlx-MvrYsepwdnLgz69I"

def get_cookies_robust():
    """
    Tries to load Brave/Chrome cookies. Handles locked DBs by copying to /tmp.
    """
    # [assumption]: User is using Brave. If not, fallback to Chrome.
    try:
        cj = browser_cookie3.brave(domain_name='.google.com')
        return {c.name: c.value for c in cj}
    except Exception:
        pass # Fall through to lock bypass

    # Manual path search for Brave/Chrome on Linux
    possible_paths = [
        os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/Cookies"),
        os.path.expanduser("~/.config/google-chrome/Default/Cookies"),
        os.path.expanduser("~/snap/brave/*/.config/BraveSoftware/Brave-Browser/Default/Cookies") 
    ]
    
    cookie_path = None
    for path in possible_paths:
        matches = glob.glob(path)
        if matches:
            cookie_path = matches[0]
            break
            
    if not cookie_path:
        raise Exception("Browser cookies not found. Log into Gmail on Brave/Chrome.")

    # Copy to temp to bypass lock
    tmp_cookie_path = "/tmp/google_cookies_temp.sqlite"
    try:
        shutil.copyfile(cookie_path, tmp_cookie_path)
        cj = browser_cookie3.chrome(cookie_file=tmp_cookie_path, domain_name='.google.com')
        return {c.name: c.value for c in cj}
    except Exception as e:
        raise Exception(f"Cookie extraction failed: {e}")

def get_auth_header(cookies):
    """Generates SAPISIDHASH required for Google APIs"""
    timestamp = str(int(time.time()))
    
    def sign(cookie_name):
        val = cookies.get(cookie_name)
        if not val: return ""
        msg = f"{timestamp} {val} {ORIGIN}"
        return hashlib.sha1(msg.encode()).hexdigest()

    sapisid_hash = sign('SAPISID')
    if not sapisid_hash: return None

    header = f"SAPISIDHASH {timestamp}_{sapisid_hash}"
    return header

def extract_details(data):
    """Parses the nested JSON response"""
    found_data = {}
    
    def search_list(lst):
        if isinstance(lst, list) and len(lst) > 4:
            id_container = lst[4]
            details_container = lst[0]
            
            if (isinstance(id_container, list) and len(id_container) > 0 
                and isinstance(id_container[0], list) and len(id_container[0]) > 0):
                
                raw_id = str(id_container[0][0])
                # Check for GAIA ID (21 digits, starts with 1)
                if re.match(r'^1\d{20}$', raw_id):
                    name = "Unknown"
                    pic_url = "N/A"
                    try:
                        if len(details_container) > 1: name = details_container[1][0]
                        if len(details_container) > 0: pic_url = details_container[0][0]
                    except: pass

                    found_data['gaia_id'] = raw_id
                    found_data['name'] = name
                    found_data['pic'] = pic_url
                    return True
        
        if isinstance(lst, list):
            for item in lst:
                if search_list(item): return True
        return False

    search_list(data)
    return found_data

async def site(email, client):
    name = "google"
    domain = "google.com"
    
    try:
        # 1. Load Cookies (Synchronous operation)
        cookies = get_cookies_robust()
        auth_header = get_auth_header(cookies)
        
        if not auth_header:
             return {
                "name": name, "domain": domain, "exists": False, "rateLimit": False,
                "others": "SAPISID cookie missing. Login to Gmail in Brave/Chrome."
            }

        headers = {
            'authorization': auth_header,
            'content-type': 'application/json+protobuf',
            'origin': ORIGIN,
            'x-goog-api-key': API_KEY,
            'x-goog-authuser': '0', 
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        
        # Payload: [ReqID, Email, [Mobile, Web], ConfigID]
        payload = [134, email, [1, 2], 8]

        # 2. Async Request using the core.py client
        req = await client.post(API_URL, cookies=cookies, headers=headers, json=payload)
        
        if req.status_code == 200:
            result = extract_details(req.json())
            if result:
                # [Fix]: Added "Pic" logic here
                info = (f"Name: {result.get('name')} | "
                        f"ID: {result.get('gaia_id')} | "
                        f"Pic: {result.get('pic')} | "
                        f"Maps: https://google.com/maps/contrib/{result.get('gaia_id')}")
                
                return {
                    "name": name, "domain": domain, "exists": True, "rateLimit": False,
                    "others": info
                }
            else:
                return {
                    "name": name, "domain": domain, "exists": False, "rateLimit": False, "others": None
                }
        elif req.status_code == 429:
             return {
                "name": name, "domain": domain, "exists": False, "rateLimit": True, "others": "Too Many Requests"
            }
        else:
             return {
                "name": name, "domain": domain, "exists": False, "rateLimit": False, 
                "others": f"API Error {req.status_code}"
            }

    except Exception as e:
        return {
            "name": name, "domain": domain, "exists": False, "rateLimit": False,
            "others": str(e)
        }

