import urllib.request

cache = {}

def crawl(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    if url in cache:
        print(f"Loaded from memory cache: {url}")
        return cache[url]

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            html = response.read().decode("utf-8")
            cache[url] = html
            print(f"Fetched and cached in memory: {url}")
            return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None