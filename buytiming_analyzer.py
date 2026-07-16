class BuyTimingAnalyzer:

    def analyze(self, history, prediction):

        prices = [record["price"] for record in history.records]

        highest_price = max(prices)
        lowest_price = min(prices)
        average_price = int(sum(prices) / len(prices))

        current_price = history.records[-1]["price"]
        predicted_price = prediction[-1]["price"]

        expected_change = predicted_price - current_price
        expected_change_rate = expected_change / current_price * 100

        return {
            "current_price": current_price,
            "highest_price": highest_price,
            "lowest_price": lowest_price,
            "average_price": average_price,
            "predicted_price": predicted_price,
            "expected_change": expected_change,
            "percent": round(expected_change_rate, 2),
            "price_score": self.calculate_price_score(expected_change_rate),
            "recommendation": self.recommend(expected_change_rate)
        }
    

    def recommend(self, change_rate):

        """
        구매 추천 문구 생성
        """

        if change_rate <= -5:
            return "조금 기다리는 것을 추천합니다."

        elif change_rate < 3:
            return "지금 구매해도 적절한 시기입니다."

        else:
            return "가격 상승이 예상되므로 지금 구매를 추천합니다."
        

    def calculate_price_score(self, change_rate):

        """
        가격 타이밍 점수 (0~100)
        """

        if change_rate <= -10:
            return 100

        elif change_rate <= -5:
            return 90

        elif change_rate <= 0:
            return 80

        elif change_rate <= 5:
            return 60

        else:
            return 40