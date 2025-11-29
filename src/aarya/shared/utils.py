import requests
import random

# A robust fallback list in case the API is down or user is offline
FALLBACK_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

def get_latest_user_agents():
    """
    Fetches the latest user agents from headers.scrapeops.io.
    Returns a list of strings or None if it fails.
    """
    url = "https://headers.scrapeops.io/v1/user-agents"
    try:
        # Timeout is important so the tool doesn't hang if the API is slow
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            json_response = response.json()
            return json_response.get("result", [])
    except Exception:
        pass
    return None

def get_random_user_agent():
    """
    Returns a random user agent.
    Priority: Live API -> Fallback List
    """
    # 1. Try to get fresh agents
    live_agents = get_latest_user_agents()
    
    if live_agents:
        return random.choice(live_agents)
    
    # 2. If API fails, use fallback
    return random.choice(FALLBACK_USER_AGENTS)