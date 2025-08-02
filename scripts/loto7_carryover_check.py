import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import os

# === GitHub 이슈 assignees, mentions (실제 GitHub 사용자명으로 수정) ===
github_assignees = ["Koony2510"]
github_mentions = ["Koony2510"]

def create_github_issue(title, body):
    github_repo = os.getenv("GITHUB_REPOSITORY")
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_repo or not github_token:
        print("⚠️ GITHUB_REPOSITORY 또는 GITHUB_TOKEN 환경변수가 설정되어 있지 않습니다.")
        return False

    api_url = f"https://api.github.com/repos/{github_repo}/issues"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    mention_text = " ".join([f"@{user}" for user in github_mentions])
    full_body = f"{mention_text}\n\n{body}"

    payload = {
        "title": title,
        "body": full_body,
        "assignees": github_assignees
    }

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 201:
        print("📌 GitHub 이슈가 성공적으로 생성되었습니다.")
        return True
    else:
        print(f"⚠️ GitHub 이슈 생성 실패: {response.status_code} - {response.text}")
        return False

def parse_date_jp(text):
    """
    'YYYY/M/D' 형식의 일본 날짜를 datetime.date로 변환 (예: '2025/8/1')
    """
    try:
        dt = datetime.strptime(text, "%Y/%m/%d").date()
        return dt
    except:
        return None

def main():
    target_date = date.today()  # 워크플로우 실행일 기준으로
    url = "https://www.ohtashp.com/topics/takarakuji/loto7/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 테이블 찾기 (추첨 데이터가 담긴 테이블)
    table = soup.find("table", class_="table")
    if not table:
        print("❌ 당첨 번호 테이블을 찾지 못했습니다.")
        return

    rows = table.find_all("tr")
    headers = [th.get_text(strip=True) for th in rows[0].find_all("th")]
    # 예상 헤더 예: ['回別', '抽選日', '本数字', ..., 'キャリー*オーバー']

    found_data = None
    for row in rows[2:]:  # 0: 헤더 1: 소제목, 2부터 데이터 시작 (테이블 구조에 따라 조절)
        cols = row.find_all(["td", "th"])
        if len(cols) < 12:
            continue

        round_num = cols[0].get_text(strip=True)
        draw_date_str = cols[1].get_text(strip=True)
        draw_date = parse_date_jp(draw_date_str)
        carryover_str = cols[-1].get_text(strip=True)  # 마지막 컬럼 캐리오버 금액

        if draw_date == target_date:
            found_data = {
                "round": round_num,
                "date": draw_date,
                "carryover": carryover_str
            }
            break

    if not found_data:
        print(f"📅 {target_date}에 해당하는 추첨 데이터가 없습니다. 작업 종료.")
        return

    # 캐리오버가 0円이 아니면 이슈 생성
    if found_data["carryover"] != "0円":
        title = f"ロト7 {found_data['round']} ({found_data['carryover']}) キャリーオーバー発生"
        body = title
        create_github_issue(title, body)
    else:
        print("캐리오버 없음. 이슈 생성하지 않음.")

if __name__ == "__main__":
    main()
