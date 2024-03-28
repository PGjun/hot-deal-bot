# 필요한 모듈을 임포트합니다.
import requests
import os
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 환경 변수에서 필요한 값들을 가져옵니다.
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
log_file_path = "content_list.txt"

# 새 글을 확인하고 로그를 남기는 함수
async def check_new_posts_and_log():
    try:
        with open(log_file_path, 'r') as file:
            known_content = file.read().splitlines()
    except FileNotFoundError:
        known_content = []

    # 크롤링 로직 (예시 URL 및 콘텐츠 선택자는 적절히 수정해주세요)
    url = "https://quasarzone.com/bbs/qb_saleinfo"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all(class_='ellipsis-with-reply-cnt')

    for post in posts:
        post_title = post.text.strip()
        if post_title not in known_content:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": f"새 글 알림: {post_title}"})
            known_content.append(post_title)

    # 파일을 업데이트합니다.
    with open(log_file_path, 'w') as file:
        file.write("\n".join(known_content))

# 봇이 준비되면 새 글 확인 로직을 주기적으로 실행합니다.
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    while True:
        await check_new_posts_and_log()
        await asyncio.sleep(300)  # 5분 대기

bot.run(DISCORD_TOKEN)
