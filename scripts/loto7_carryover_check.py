def main():
    # 테스트용 고정 날짜
    target_date = date(2025, 4, 25)
    # target_date = date(2025, 8, 2)  # 예: 2025년 8월 2일로 고정하려면 이 줄로 대체
    # target_date = date.today()

    url = "https://www.ohtashp.com/topics/takarakuji/loto7/"
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    table = soup.find("table", class_="table")
    if not table:
        print("❌ 당첨 번호 테이블을 찾지 못했습니다.")
        return

    rows = table.find_all("tr")
    found_data = None

    for row in rows[2:]:
        cols = row.find_all(["td", "th"])
        if len(cols) < 12:
            continue

        round_num = cols[0].get_text(strip=True)
        draw_date_str = cols[1].get_text(strip=True)
        draw_date = parse_date_jp(draw_date_str)
        carryover_str = cols[-1].get_text(strip=True)

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

    if found_data["carryover"] != "0円":
        title = f"ロト7 {found_data['round']} ({found_data['carryover']}) キャリーオーバー発生"
        body = (
            f"{title}\n\n"
            "📎 출처: [오타상 로또 정보](https://www.ohtashp.com/topics/takarakuji/loto7/)\n"
            "📎 공식: [미즈호 은행 로또7](https://www.mizuhobank.co.jp/takarakuji/check/loto/loto7/index.html)"
        )
        create_github_issue(title, body)
    else:
        print("캐리오버 없음. 이슈 생성하지 않음.")
