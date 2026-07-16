import pandas as pd
from price_history import PriceHistory

class HistoryManager:

    def load_history(self, file_name, id_column, product_id):
        """
        CSV에서 제품의 가격 이력을 읽어 PriceHistory 객체를 반환
        """

        df = pd.read_csv(file_name)

        history_df = df[df[id_column] == product_id]

        if history_df.empty:
            return None

        product_name = history_df.iloc[0]["product_name"]

        history = PriceHistory(product_id, product_name)

        for _, row in history_df.iterrows():
            history.add_record(
                row["date"],
                row["price"]
            )

        return history
    

    def save_history(self, history, file_name, id_column):
        """
        PriceHistory 객체를 CSV에 저장
        """

        rows = []

        for record in history.records:

            rows.append({
                id_column: history.product_id,
                "product_name": history.product_name,
                "date": record["date"],
                "price": record["price"]
            })

        df = pd.DataFrame(rows)

        df.to_csv(file_name, index=False)


    def add_price(self,
                file_name,
                id_column,
                product_id,
                product_name,
                date,
                price):
        """
        CSV에 가격 기록 추가
        """

        df = pd.read_csv(file_name)

        new_row = {
            id_column: product_id,
            "product_name": product_name,
            "date": date,
            "price": price
        }

        df.loc[len(df)] = new_row

        df.to_csv(file_name, index=False)


        