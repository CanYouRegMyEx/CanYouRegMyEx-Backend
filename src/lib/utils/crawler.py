import urllib.request

def crawl(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")
        return None