import asyncio
import json
from playwright.async_api import async_playwright
from shared import utils

async def site(email, client):
    name = "buymeacoffee"
    domain = "buymeacoffee.com"
    
    # We ignore the 'client' (httpx) because we are using a full browser
    
    try:
        async with async_playwright() as p:
            # 1. Launch Browser
            # headless=True is faster, but if it fails, try headless=False to see what's happening
            browser = await p.chromium.launch(headless=True)
            
            # Create a context with a real user agent to look human
            user_agent = utils.get_random_user_agent()
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()

            # 2. Go to Signup Page
            # We go to the login page because it often handles 'exists' checks faster/cleaner
            # or the signup page directly.
            await page.goto("https://www.buymeacoffee.com/signup", timeout=30000)

            # 3. Fill the Form
            # Wait for email input to be visible
            await page.wait_for_selector('input[name="email"]', state="visible")
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="password"]', "Sup3rS3cur3P@ss!")
            
            # 4. Setup Network Interception
            # We want to catch the API response that happens after we click submit.
            # We rely on the server's JSON response rather than reading UI text (more accurate).
            async with page.expect_response(lambda response: "auth/signup" in response.url, timeout=10000) as response_info:
                
                # Click the submit button (Finding the button by type or text)
                # Usually: button[type="submit"] or text="Continue"
                submit_btn = page.locator('button[type="submit"]')
                await submit_btn.click()

            # 5. Analyze the Response
            response = await response_info.value
            status = response.status
            text = await response.text()
            
            await browser.close()

            # Logic: 422 usually means Validation Error (Account Exists)
            if status == 422:
                if "exists" in text.lower() or "taken" in text.lower():
                    return {
                        "name": name, "domain": domain, "exists": True, "rateLimit": False,
                        "others": "Account Found (Intercepted 422)"
                    }
                else:
                    return {
                        "name": name, "domain": domain, "exists": False, "rateLimit": False,
                        "others": f"Validation Error: {text[:50]}"
                    }

            # Logic: 200/201 means Success (Account Created -> Email did NOT exist)
            elif status in [200, 201]:
                return {
                    "name": name, "domain": domain, "exists": False, "rateLimit": False,
                    "others": None
                }

            # Logic: 429 Rate Limit
            elif status == 429:
                return {
                    "name": name, "domain": domain, "exists": False, "rateLimit": True,
                    "others": "Too Many Requests (API)"
                }
            
            else:
                return {
                    "name": name, "domain": domain, "exists": False, "rateLimit": False,
                    "others": f"Unexpected Status: {status}"
                }

    except Exception as e:
        # Check for timeout (common with Playwright if selectors change)
        err_msg = str(e)
        if "Timeout" in err_msg:
             return {"name": name, "domain": domain, "exists": False, "rateLimit": True, "others": "Browser Timeout (WAF or Slow)"}
        
        return {"name": name, "domain": domain, "exists": False, "rateLimit": False, "others": f"Browser Error: {err_msg[:50]}"}