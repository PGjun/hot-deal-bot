import requests
import os
from bs4 import BeautifulSoup
import time

# 환경 변수에서 필요한 값들을 가져옵니다.
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
log_file_path = "content_list.txt"

def check_new_posts_and_log():
    known_content = set()
    try:
        with open(log_file_path, 'r') as file:
            known_content.update(file.read().splitlines())
    except FileNotFoundError:
        print("Log file not found. Creating a new one.")

    base_url = "https://quasarzone.com"
    url = f"{base_url}/bbs/qb_saleinfo"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the webpage: HTTP {response.status_code}")
        print("Response headers:", response.headers)
        print("Response body:", response.text)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all(class_='market-info-list')
    
    # 게시물 리스트를 역순으로 순회하여 최신 게시물이 마지막에 처리되도록 합니다.
    for post in reversed(posts):
        # 이미지 URL 추출
        img_url_element = post.select_one('.img-background-wrap.lazy')
        if not img_url_element:
            continue
        img_url = img_url_element['style'].split('url(')[-1].strip(')')
        
        # 제목 추출
        title_element = post.select_one('.ellipsis-with-reply-cnt')
        if not title_element:
            continue
        title = title_element.text.strip()

        # URL 추출
        href_element = post.select_one('.market-info-list-cont .tit a')
        if not href_element or 'href' not in href_element.attrs:
            continue
        post_url = base_url + href_element['href']
        post_id = href_element['href'].split('/')[-1]

        # 가격 정보 추출
        price_info_element = post.select_one('.market-info-sub .text-orange')
        price_info = price_info_element.text.strip() if price_info_element else "가격 정보 없음"

        # 중복 검사
        if post_id in known_content:
            continue
        known_content.add(post_id)

        # Discord에 메시지 전송
        embed = {
            "title": title,
            "description": f"가격: {price_info}",
            "color": 0xFF0000,
            "image": {"url": img_url},
            "fields": [
                {
                    "name": "",
                    "value": post_url,
                    "inline": True
                }
            ]
        }
        headers = {'Content-Type': 'application/json'}
        payload = {"embeds": [embed]}
        result = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
        print(f"Discord webhook response: HTTP {result.status_code}, Body: {result.text}")
        if result.status_code == 429:  # Rate limit detected
            retry_after = result.json().get("retry_after", 0.3)  # Use default 0.3s if retry_after is missing
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
        # Optionally, you could implement a retry mechanism here.
        elif result.status_code != 204:
            print(f"Failed to send message to Discord: HTTP {result.status_code}")

        time.sleep(0.3)  # 요청 사이에 0.3초 대기

    # 로그 파일 업데이트
    if known_content:
        with open(log_file_path, 'w') as file:
            for content in known_content:
                file.write(content + '\n')

# 스크립트 실행
check_new_posts_and_log()
