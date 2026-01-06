from playwright.sync_api import sync_playwright
import json
from pathlib import Path
import time

COOKIE_FILE = Path("cookies.json")

def get_bearer_token():
    with sync_playwright() as p:
        headless_mode = COOKIE_FILE.exists()
        browser = p.chromium.launch(headless=headless_mode)
        context = browser.new_context()
        
        if COOKIE_FILE.exists():
            context.add_cookies(json.loads(COOKIE_FILE.read_text()))
            print("loaded existing cookies")
        else:
            print("No cookies found. Please log in manually in the opened browser.")
        
        page = context.new_page()
        token = None
        
        def on_request(request):
            nonlocal token
            auth = request.headers.get("authorization")
            if auth and auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1]
        
        page.on("request", on_request)
        
        # First go to main Spotify to establish session
        page.goto("https://open.spotify.com/", wait_until="networkidle")
        
        if not COOKIE_FILE.exists():
            print("Waiting for you to log in to Spotify...")
            try:
                page.wait_for_selector("button[data-testid='user-widget-link']", timeout=300000)
                print("Login detected")
            except:
                browser.close()
                raise RuntimeError("Timeout waiting for login")
        
        # Wait a bit for API requests
        time.sleep(1)
        
        # If still no token, try interacting with the page
        if not token:
            print("Triggering more requests...")
            # Scroll or click to trigger lazy-loaded content
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)
        
        # Wait for Bearer token
        timeout = 30
        start_time = time.time()
        
        while not token:
            if time.time() - start_time > timeout:
                browser.close()
                raise RuntimeError("Timeout waiting for Bearer token")
            time.sleep(0.5)
        
        COOKIE_FILE.write_text(json.dumps(context.cookies()))
        browser.close()
        print("retrieved token")
        return token

if __name__ == "__main__":
    token = get_bearer_token()
    if token:
        print(f"\nBearer Token: {token}")
    else:
        print("\nFailed to capture token")