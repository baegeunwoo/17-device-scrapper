import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta


class PricePredictor:

    def predict_next_7days(self, history):

        """
        PriceHistory 객체를 받아
        앞으로 7일의 가격을 예측한다.
        """

        records = history.records

        # 데이터가 너무 적으면 예측 불가
        if len(records) < 2:
            return []

        # -----------------------
        # X : 날짜 번호
        # -----------------------

        X = np.arange(len(records)).reshape(-1, 1)

        # -----------------------
        # y : 가격
        # -----------------------

        y = np.array([
            record["price"]
            for record in records
        ])

        # -----------------------
        # 선형회귀 학습
        # -----------------------

        model = LinearRegression()

        model.fit(X, y)

        # -----------------------
        # 마지막 날짜
        # -----------------------

        last_date = datetime.strptime(
            records[-1]["date"],
            "%Y-%m-%d"
        )

        # -----------------------
        # 7일 예측
        # -----------------------

        future_x = np.arange(
            len(records),
            len(records) + 7
        ).reshape(-1, 1)

        predicted = model.predict(future_x)

        result = []

        for i in range(7):

            result.append({

                "date": (
                    last_date +
                    timedelta(days=i + 1)
                ).strftime("%Y-%m-%d"),

                "price": int(predicted[i])

            })

        return result
    

    def get_trend(self, history):

        records = history.records

        if len(records) < 2:
            return "보합"

        X = np.arange(len(records)).reshape(-1,1)

        y = np.array([
            record["price"]
            for record in records
        ])

        model = LinearRegression()

        model.fit(X, y)

        slope = model.coef_[0]

        if slope > 100:
            return "상승"

        elif slope < -100:
            return "하락"

        else:
            return "보합"
        

    def expected_change(self, history):

        prediction = self.predict_next_7days(history)

        if not prediction:
            return 0

        current_price = history.records[-1]["price"]

        future_price = prediction[-1]["price"]

        return future_price - current_price