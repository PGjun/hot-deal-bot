# 필요한 모듈을 임포트합니다.
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

    url = "https://quasarzone.com/bbs/qb_saleinfo"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all(class_='market-info-list')

    new_content_found = False
    for post in posts:
        post_title = post.text.strip()
        if post_title not in known_content:
            new_content_found = True
            # Embed 형태로 메시지 데이터를 구성합니다.
            embed = {
                "title": "🔥 새로운 핫딜 🔥",
                "description": post_title,
                "color": 0xFF0000,
                "fields": [
                    {
                        "name": "링크",
                        "value": url,
                        "inline": True
                    }
                ]
            }
            # Discord 웹훅 URL로 POST 요청을 보냅니다.
            headers = {'Content-Type': 'application/json'}
            payload = {"embeds": [embed]}
            requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
            known_content.add(post_title)

    if new_content_found:
        with open(log_file_path, 'w') as file:
            file.write("\n".join(known_content))

# 스크립트 실행
check_new_posts_and_log()
