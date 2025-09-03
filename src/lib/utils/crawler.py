import urllib.request

def fetch_html_content(url: str, headers: dict):
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

def crawl_detective_conan(url: str):
    browser_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🌐 Crawling: {url}")
    html_content = fetch_html_content(url, browser_headers)
    
    if html_content:
        print(f"✅ Successfully crawled: {url}")
        return html_content
    else:
        print(f"❌ Failed to crawl: {url}")
        return None

def crawling():
    base_url = "https://www.detectiveconanworld.com"
    main_page_url = base_url + "/wiki/Anime"
    
    # ===== Level 1: Crawl หน้าหลัก =====
    main_html_content = crawl_detective_conan(main_page_url)
    
    if not main_html_content:
        return False

    with open('conan_main_page_raw.html', 'w', encoding='utf-8') as main_file:
        main_file.write(main_html_content)
    print("✅ Main page saved: conan_main_page_raw.html")
    
    # ===== Level 2: Crawl แต่ละตอน (เทส 5 ตอน) =====
    episode_urls = [
        base_url + "/wiki/Episode_1",
        base_url + "/wiki/Episode_2", 
        base_url + "/wiki/Episode_3",
        base_url + "/wiki/Episode_4",
        base_url + "/wiki/Episode_5"
    ]
    
    print(f"\nCrawling {len(episode_urls)} episode pages... 🔄")
    
    for i, episode_url in enumerate(episode_urls):
        print(f"Crawling episode {i+1}: {episode_url}") 

        episode_html = crawl_detective_conan(episode_url)
        if episode_html:
            filename = f'conan_episode_{i+1}_raw.html'
            with open(filename, 'w', encoding='utf-8') as ep_file:
                ep_file.write(episode_html)
            print(f"Saved: {filename}")
    
    print(f"\n✅ All crawling completed successfully!")
    return True

crawling()