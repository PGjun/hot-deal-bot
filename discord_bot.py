import requests
import os
from bs4 import BeautifulSoup

# 환경 변수에서 필요한 값들을 가져옵니다.
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
log_file_path = "content_list.txt"

# 새 글을 확인하고 로그를 남기는 함수
def check_new_posts_and_log():
    known_content = set()
    try:
        with open(log_file_path, 'r') as file:
            known_content.update(file.read().splitlines())
    except FileNotFoundError:
        pass

    base_url = "https://quasarzone.com"
    response = requests.get(f"{base_url}/bbs/qb_saleinfo")
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='market-info-list')

    new_content_found = False
    for post in posts:
        post_link = post.select_one('.market-info-list-cont .tit a')
        if post_link and 'href' in post_link.attrs:
            post_url = base_url + post_link['href']
            post_id = post_link['href'].split('/')[-1]
            if post_id not in known_content:
                title = post_link.select_one('.ellipsis-with-reply-cnt').text.strip()
                price_info = post.select_one('.market-info-sub .text-orange').text.strip() if post.select_one('.market-info-sub .text-orange') else "가격 정보 없음"

                # Embed 형태로 메시지 데이터를 구성합니다.
                embed = {
                    "title": title,
                    "description": f"가격: {price_info}",
                    "color": 0xFF0000,
                    "fields": [
                        {
                            "name": "링크",
                            "value": post_url,
                            "inline": True
                        }
                    ]
                }
                # Discord 웹훅 URL로 POST 요청을 보냅니다.
                headers = {'Content-Type': 'application/json'}
                payload = {"embeds": [embed]}
                requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
                
                known_content.add(post_id)
                new_content_found = True

    if new_content_found:
        with open(log_file_path, 'w') as file:
            file.write("\n".join(known_content))

# 스크립트 실행
check_new_posts_and_log()
