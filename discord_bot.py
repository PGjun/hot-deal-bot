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
            for line in file.read().splitlines():
                # 파일에서 게시물 번호만 추출하여 집합에 저장
                known_content.add(line.split('|')[-1])  # 게시물 URL 마지막 부분이 번호
    except FileNotFoundError:
        pass

    base_url = "https://quasarzone.com"
    url = f"{base_url}/bbs/qb_saleinfo"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all(class_='ellipsis-with-reply-cnt')

    new_content_found = False
    for post in posts:
        a_tag = post.find('a')
        if a_tag and 'href' in a_tag.attrs:
            post_url_suffix = a_tag.attrs['href']
            post_url = base_url + post_url_suffix
            post_id = post_url_suffix.split('/')[-1]
            
            if post_id not in known_content:
                new_content_found = True
                post_title = post.text.strip()
                # 금액 정보 추출
                price_info = post.find_next_sibling(class_='market-info-sub').find(class_='text-orange').text.strip()

                # Embed 형태로 메시지 데이터를 구성합니다.
                embed = {
                    "title": "🔥 새로운 핫딜 🔥",
                    "description": f"{post_title}\n금액: {price_info}",
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
                
                # 중복 검사를 위해 게시물 제목과 URL을 함께 파일에 저장
                known_content.add(post_id)

    if new_content_found:
        with open(log_file_path, 'w') as file:
            for content in known_content:
                file.write(f"{content}\n")

# 스크립트 실행
check_new_posts_and_log()
