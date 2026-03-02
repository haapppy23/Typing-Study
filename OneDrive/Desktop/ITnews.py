import schedule
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_news():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 야, 뉴스 긁어왔다. 확인해라.")
    
    # 1. 뉴스 검색 (키워드: IT 신기술, 전자기기)
    query = "IT 신기술 전자기기"
    url = f"https://search.naver.com/search.naver?where=news&query={query}&sort=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.select(".news_tit")[:10] # 넉넉하게 10개 긁어옴
        
        # 2. 결과물 정리
        news_list = []
        news_list.append(f"📅 수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        news_list.append("="*50)
        
        for i, item in enumerate(items, 1):
            title = item['title']
            link = item['href']
            news_list.append(f"{i}. {title}\n   {link}")
        
        news_result = "\n\n".join(news_list)
        
        # 3. 파일로 저장 (항상 최신 정보로 덮어쓰거나 추가 가능)
        # 'a'로 하면 계속 쌓이고, 'w'로 하면 매번 최신 것만 남습니다.
        with open("news_raw.txt", "w", encoding="utf-8") as f:
            f.write(news_result)
            
        print("✅ 'news_raw.txt'에 저장 완료했다.")
        print("="*30)
        print(news_result[:300] + "...") # 터미널에도 살짝 보여줌
        
    except Exception as e:
        print(f"❌ 에러 났다: {e}")

# --- 스케줄 설정 (형님이 정한 골든타임) ---
schedule.every().day.at("09:00").do(fetch_news)
schedule.every().day.at("14:00").do(fetch_news)
schedule.every().day.at("20:00").do(fetch_news)

print("🚀 뉴스 셔틀 가동 중...")
print("09:00 / 14:00 / 20:00 에 뉴스를 긁어서 'news_raw.txt'에 넣어둘게.")
print("그냥 켜두고 니 할 일 해라!")

# 테스트용: 지금 바로 긁어보고 싶으면 아래 줄 주석(#)을 해제하세요.
# fetch_news()

while True:
    schedule.run_pending()
    time.sleep(60)
