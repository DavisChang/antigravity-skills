import sys
from playwright.sync_api import sync_playwright
import time
import argparse

def fetch_urls(urls):
    results = {}
    with sync_playwright() as p:
        # channel="chrome" uses the default installed Chrome browser, heavily reducing bot detection
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context()
        page = context.new_page()
        for url in urls:
            print(f"Fetching: {url}", file=sys.stderr)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(4) # Wait for Cloudflare validation and dynamic content
                text = page.evaluate("document.body.innerText")
                results[url] = text
            except Exception as e:
                print(f"Error on {url}: {e}", file=sys.stderr)
                results[url] = f"Error: {e}"
        browser.close()
    return results

def main():
    parser = argparse.ArgumentParser(description="Fetch full text from Medium URLs bypassing Cloudflare via Playwright")
    parser.add_argument("urls", nargs="+", help="One or more URLs to fetch")
    args = parser.parse_args()

    contents = fetch_urls(args.urls)
    for url, text in contents.items():
        print(f"=== CONTENT FOR: {url} ===")
        print(text)
        print("=== END CONTENT ===\n")

if __name__ == "__main__":
    main()
