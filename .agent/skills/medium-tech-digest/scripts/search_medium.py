import argparse
import urllib.request
import urllib.parse
import json
import re
import sys

def search_ddg(query):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        # extract duckduckgo redirect links
        links_uddg = re.findall(r'href="//duckduckgo\.com/l/\?uddg=([^"&]+)', html)
        
        links = []
        for l in links_uddg:
            links.append(urllib.parse.unquote(l))
            
        return [l for l in links if 'medium.com' in l]
    except urllib.error.URLError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

def main():
    parser = argparse.ArgumentParser(description="Search DDG for specific queries and return unique Medium links")
    parser.add_argument("query", type=str, nargs="+", help="The search query as strings")
    parser.add_argument("--limit", type=int, default=15, help="Number of max URLs to return")
    args = parser.parse_args()

    full_query = " ".join(args.query)
    links = search_ddg(full_query)
    
    unique_links = []
    seen = set()
    for l in links:
        # Ignore tag and topic pages
        if '/tag/' in l or '/topic/' in l:
            continue
        if l not in seen:
            unique_links.append(l)
            seen.add(l)
            
    for l in unique_links[:args.limit]:
        print(l)

if __name__ == "__main__":
    main()
