import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter


class PriceAnalyzer:

    def analyze_price(self, records, product_name=None):

        if not records:
            print("가격 정보가 없습니다.")
            return None

        prices = [record["price"] for record in records]

        current_price = prices[-1]
        highest_price = max(prices)
        lowest_price = min(prices)
        average_price = sum(prices) / len(prices)

        percent = (current_price - average_price) / average_price * 100

        if percent <= -10:
            recommendation = "★★★★★ 지금 구매 추천"
        elif percent <= -5:
            recommendation = "★★★★☆ 구매하기 좋은 시기"
        elif percent <= 5:
            recommendation = "★★★☆☆ 평균 가격"
        else:
            recommendation = "★☆☆☆☆ 가격이 높음"

        return {
            "product_name": product_name,
            "current_price": current_price,
            "highest_price": highest_price,
            "lowest_price": lowest_price,
            "average_price": average_price,
            "percent": round(percent, 2),
            "recommendation": recommendation
        }


    def draw_price_graph(self, history):

        if history is None:
            return None

        dates = [record["date"] for record in history.records]
        prices = [record["price"] for record in history.records]

        plt.figure(figsize=(10, 5))

        plt.plot(dates, prices, marker="o")

        plt.title(history.product_name)
        plt.xlabel("Date")
        plt.ylabel("Price (KRW)")
        plt.grid(True)

        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.tight_layout()

        save_path = f"static/graphs/{history.product_id}.png"

        plt.savefig(save_path)
        plt.close()

        return save_path