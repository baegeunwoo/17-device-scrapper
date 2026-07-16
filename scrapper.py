import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

def match_products(products, csv_file, id_column):

    # CPU/GPU 기준 CSV 읽기
    df = pd.read_csv(csv_file)

    # keyword 길이가 긴 것부터 매칭
    df = df.sort_values(
        "keyword",
        key=lambda s: s.str.len(),
        ascending=False
    )

    # 결과를 저장할 딕셔너리
    matched = {}

    # 상품 하나씩 검사
    for product in products:

        title = product["title"]
        price = product["price"]

        product_id = None

        # -----------------------------
        # CPU는 정규식으로 모델명 추출
        # -----------------------------
        if id_column == "cpu_id":

            pattern = r"\d{4,5}(?:X3D2|X3D|X|KF|K|F|T|GT|G)?"

            m = re.search(pattern, title)

            if not m:
                continue

            model = m.group()

            for _, row in df.iterrows():

                keyword = str(row["keyword"]).strip()

                if model == keyword:
                    product_id = row[id_column]
                    break

        # -----------------------------
        # GPU, RAM은 keyword 포함 여부
        # -----------------------------
        else:

            for _, row in df.iterrows():

                keyword = str(row["keyword"]).replace("-", " ")

                if keyword in title.replace("-", " "):
                    product_id = row[id_column]
                    break

        # 매칭 실패
        if product_id is None:
            continue

        # 가격 숫자로 변환
        price = int(
            str(price)
            .replace(",", "")
            .replace("원", "")
        )

        # -----------------------------
        # 처음 나온 모델이면 저장
        # -----------------------------
        if product_id not in matched:

            matched[product_id] = {
                id_column: product_id,
                "title": title,
                "price": price
            }

        # -----------------------------
        # 이미 저장된 모델이면
        # 더 싼 가격만 남김
        # -----------------------------
        else:

            if price < matched[product_id]["price"]:

                matched[product_id]["price"] = price
                matched[product_id]["title"] = title

    # 딕셔너리 → 리스트 변환
    return list(matched.values())

def search(keyword):

    url=f"https://search.danawa.com/dsearch.php?query={keyword}&tab=main"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    prod_list = soup.find("div", class_="main_prodlist main_prodlist_list")
    lis = prod_list.find_all("li", class_="prod_item")

    products = []

    for li in lis:

        a = li.select_one("p.prod_name a")
        b = li.select_one("p.price_sect a")

        if not a or not b:
            continue

        title = a.get_text(strip=True)
        price = b.get_text(strip=True)

        # print(title)
        # print("-"*40)
        # print(price)
        data = {
            "title" : title,
            "price" : price 
        }

        products.append(data)
    return products

def save_price(matched, path):

    df = pd.DataFrame(matched)

    df.to_csv(
        "./"+path,
        index=False,
        encoding="utf-8-sig"
    )

def update_values():
    cpu = pd.read_csv("cpu.csv")
    price = pd.read_csv("cpu_price.csv")
    
    gpu = pd.read_csv("gpu.csv")
    gpu_price = pd.read_csv("gpu_price.csv")
    
    # cpu_id 기준으로 합치기
    df = cpu.merge(price, on="cpu_id", how="left")
    df2 = gpu.merge(gpu_price, on="gpu_id", how="left")
    
    # 가성비 계산
    df["value"] = df["benchmark"] / df["price"]
    df2["value"] = df2["benchmark"] / df2["price"]

    # 소수점 둘째자리까지
    df["value"] = df["value"].round(4)
    df2["value"] = df2["value"].round(4)

    df.to_csv("cpu2.csv", index=False)
    df2.to_csv("gpu2.csv", index=False)


def search_cpuandgpu(max_budget):
    cpu_df = pd.read_csv("cpu2.csv")
    gpu_df = pd.read_csv("gpu2.csv")

    possible = []

    for _, cpu in cpu_df.iterrows():
        for _, gpu in gpu_df.iterrows():

            if cpu["price"] + gpu["price"] > max_budget:
                continue
            possible.append((cpu, gpu))

    return possible


def calculate_score(cpu, gpu, purpose):

    if purpose == "game":
        return cpu["game_score"] * 0.3 + gpu["game_score"] * 0.7

    elif purpose == "work":
        return cpu["work_score"] * 0.7 + gpu["work_score"] * 0.3

    elif purpose == "ai":
        return cpu["work_score"] * 0.2 + gpu["ai_score"] * 0.8

def calculate_balance_score(cpu, gpu):

    ratio = cpu["price"] / gpu["price"]

    ideal = 0.5

    score = 100 - abs(ratio-ideal)*100

    return max(0, min(score,100))

def calculate_value_score(cpu, gpu):

    return (
        cpu["value_score"]
        +
        gpu["value_score"]
    )/2

def calculate_final_score(cpu, gpu, purpose):

    performance = calculate_score(cpu, gpu, purpose)

    balance = calculate_balance_score(cpu, gpu)

    value = calculate_value_score(cpu, gpu)

    if purpose == "game":
        final = performance*0.6 + balance*0.2 + value*0.2

    elif purpose == "work":
        final = performance*0.5 + balance*0.1 + value*0.4

    elif purpose == "ai":
        final = performance*0.7 + balance*0.1 + value*0.2
    
    return final

def calculate_budget_usage(cpu, gpu, budget):

    used = cpu["price"] + gpu["price"]

    return used / budget * 100

def calculate_game_score(cpu, gpu):

    return (
        cpu["performance_score"]*0.3
        +
        gpu["performance_score"]*0.7
    )

def recommend(possible, purpose):

    best_score = -1

    best_cpu = None
    best_gpu = None

    for cpu, gpu in possible:

        score = calculate_final_score(cpu, gpu, purpose)

        if score > best_score:
            best_score = score
            best_cpu = cpu
            best_gpu = gpu

    return best_cpu, best_gpu, best_score


def recommend_motherboard(cpu):

    mb_df = pd.read_csv("motherboard.csv")

    compatible = mb_df[
        mb_df["socket"] == cpu["socket"]
    ]

    compatible = compatible.sort_values("price")

    return compatible.iloc[0]



def create_price_history(csv_file,
                         output_file,
                         id_column,
                         name_column,
                         days=30):

    df = pd.read_csv(csv_file)
    df = df.dropna(subset=["price"])
    history = []

    today = datetime.today()

    for _, row in df.iterrows():

        current_price = row["price"]

        start_price = current_price * random.uniform(0.95,1.10)

        price = start_price

        for i in range(days):

            date = today - timedelta(days=days-i-1)

            change = random.uniform(-0.02,0.02)

            price *= (1+change)

            history.append({
                "date":date.strftime("%Y-%m-%d"),
                "product_id":row[id_column],
                "product_name":row[name_column],
                "price":int(price)
            })

    pd.DataFrame(history).to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )


def make_score_csv(
    input_file,
    price_file,
    output_file,
    id_column
):
    df = pd.read_csv(input_file)
    price_df = pd.read_csv(price_file)

    df = pd.merge(
        df,
        price_df[[id_column, "price"]],
        on=id_column,
        how="left"
    )

    # -----------------------------
    # Performance Score (60~100)
    # -----------------------------
    normalized = (
        (df["benchmark"] - df["benchmark"].min()) /
        (df["benchmark"].max() - df["benchmark"].min())
    )

    df["performance_score"] = (
        60 + normalized * 40
    ).round(2)

    # -----------------------------
    # Game Score
    # -----------------------------
    df["game_score"] = (
        df["performance_score"] * 1.00
    ).clip(60, 100).round(2)

    # -----------------------------
    # Work Score
    # -----------------------------
    df["work_score"] = (
        df["performance_score"] * 0.95 + 5
    ).clip(60, 100).round(2)

    # -----------------------------
    # AI Score
    # -----------------------------
    df["ai_score"] = (
        df["performance_score"] * 0.90 + 8
    ).clip(60, 100).round(2)

    # -----------------------------
    # Value Score
    # -----------------------------
    value = df["benchmark"] / df["price"]

    value_normalized = (
        (value - value.min()) /
        (value.max() - value.min())
    )

    df["value_score"] = (
        60 + value_normalized * 40
    ).round(2)

    # 저장
    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"{output_file} 저장 완료")


def analyze_price(history_file, product_id):

    df = pd.read_csv(history_file)

    # 원하는 제품만 선택
    product = df[df["product_id"] == product_id]

    if product.empty:
        print("가격 정보가 없습니다.")
        return

    # 날짜순 정렬
    product = product.sort_values("date")

    # 현재 가격 (가장 최근)
    current_price = product.iloc[-1]["price"]

    # 최고가
    highest_price = product["price"].max()

    # 최저가
    lowest_price = product["price"].min()

    # 평균가
    average_price = product["price"].mean()

    # 평균 대비 %
    percent = (current_price - average_price) / average_price * 100

    # 구매 추천
    if percent <= -10:
        recommendation = "★★★★★ 지금 구매 추천"

    elif percent <= -5:
        recommendation = "★★★★☆ 구매하기 좋은 시기"

    elif percent <= 5:
        recommendation = "★★★☆☆ 평균 가격"

    else:
        recommendation = "★☆☆☆☆ 가격이 높음, 기다리는 것을 추천"

    print("제품 :", product.iloc[0]["product_name"])
    print(f"현재 가격 : {current_price:,}원")
    print(f"30일 최고가 : {highest_price:,}원")
    print(f"30일 최저가 : {lowest_price:,}원")
    print(f"30일 평균가 : {average_price:,.0f}원")
    print(f"평균 대비 : {percent:.2f}%")
    print("구매 추천 :", recommendation)

def draw_price_graph(history_file, product_id):

    # CSV 읽기
    df = pd.read_csv(history_file)

    # product_id 자료형 맞추기
    df["product_id"] = df["product_id"].astype(int)

    # 원하는 제품만 선택
    product = df[df["product_id"] == int(product_id)].copy()

    if product.empty:
        print("가격 정보가 없습니다.")
        return

    # 날짜 변환 및 정렬
    product["date"] = pd.to_datetime(product["date"])
    product = product.sort_values("date")

    # 평균 가격
    avg_price = product["price"].mean()

    # 그래프 크기
    plt.figure(figsize=(11, 5))

    # 가격 그래프
    plt.plot(
        product["date"],
        product["price"],
        marker="o",
        linewidth=2,
        label="Price"
    )

    # 평균 가격
    plt.axhline(
        avg_price,
        linestyle="--",
        linewidth=2,
        label=f"Average ({avg_price:,.0f}원)"
    )

    # 제목
    plt.title(
        f"{product.iloc[0]['product_name']} Price History",
        fontsize=15
    )

    plt.xlabel("Date")
    plt.ylabel("Price")

    # 날짜를 5일 간격으로 표시
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

    # 가격을 만원 단위로 표시
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{x/10000:.0f}만원")
    )

    # 격자
    plt.grid(True, linestyle="--", alpha=0.5)

    # 범례
    plt.legend()

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.show()

# create_price_history(
#     "cpu2.csv",
#     "cpu_price_history.csv",
#     "cpu_id",
#     "keyword"
# )

# create_price_history(
#     "gpu2.csv",
#     "gpu_price_history.csv",
#     "gpu_id",
#     "model"
# )

print("예산: ")
money = int(input())
budget = money*0.7
possible = search_cpuandgpu(budget)


best_cpu, best_gpu, final_score = recommend(possible, "work")
analyze_price(
    "cpu_price_history.csv",
    best_cpu["cpu_id"]
)
analyze_price(
    "gpu_price_history.csv",
    best_gpu["gpu_id"]
)
draw_price_graph(
    "gpu_price_history.csv",
    best_gpu["gpu_id"]
)
draw_price_graph(
    "cpu_price_history.csv",
    best_cpu["cpu_id"]
)

# gpu_df = pd.read_csv("gpu2.csv")

# duplicates = gpu_df[gpu_df.duplicated(subset=["gpu_id", "model"], keep=False)]

# print(duplicates)

# print("예산: ")
# money = int(input())
# budget = money*0.7
# possible = search_cpuandgpu(budget)


# best_cpu, best_gpu, final_score = recommend(possible, "work")
# perfomance = calculate_score(best_cpu,best_gpu,"work")
# budget_usage = calculate_budget_usage(best_cpu, best_gpu, budget)
# balance_score = calculate_balance_score(best_cpu, best_gpu)
# value_score = calculate_value_score(best_cpu, best_gpu)

# print(perfomance)
# print(value_score)
# print(balance_score)
# print(budget_usage)
# print(final_score)
# print(best_cpu["keyword"])
# print(best_gpu["model"])

# best_board = recommend_motherboard(best_cpu)

# print(best_board["model"])


# ram = match_products(search("RAM"), "./ram.csv", "ram_id")
# cpu = match_products(search("CPU"), "./cpu.csv", "cpu_id")
# gpu = match_products(search("RTX"), "./gpu.csv", "gpu_id")
# save_price(ram, "ram_price.csv")
# save_price(cpu, "cpu_price.csv")
# save_price(gpu, "gpu_price.csv")

# make_score_csv("cpu.csv", "cpu_price.csv","cpu2.csv","cpu_id")
# make_score_csv("gpu.csv", "gpu_price.csv","gpu2.csv","gpu_id")

