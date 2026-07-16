import pandas as pd
from cpu import CPU
from gpu import GPU
from motherboard import MotherBoard
from price_history import PriceHistory
from crawler import Crawler

class DatasetManager:

    def load_price_history(self, history_file, product_id):

        df = pd.read_csv(history_file)

        product = df[df["product_id"] == product_id]

        if product.empty:
            return None

        product = product.sort_values("date")

        history = PriceHistory(
            product_id,
            product.iloc[0]["product_name"]
        )

        for _, row in product.iterrows():
            history.add_record(
                row["date"],
                row["price"]
            )

        return history

    @staticmethod
    def _clean_numeric(series: pd.Series) -> pd.Series:
        """콤마·공백 등을 제거하고 숫자형으로 변환"""
        cleaned = (
            series
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        return pd.to_numeric(cleaned, errors="coerce")


    def load_cpus(self):
        cpu_df = pd.read_csv("./data/cpu2.csv")

        numeric_cols = [
            "benchmark", "price", "performance_score",
            "game_score", "work_score", "ai_score", "value_score"
        ]
        for col in numeric_cols:
            cpu_df[col] = self._clean_numeric(cpu_df[col])

        # 변환 후에도 값이 없는 행은 걸러내기 (선택)
        cpu_df = cpu_df.dropna(subset=numeric_cols)

        cpus = []
        for _, row in cpu_df.iterrows():
            cpu = CPU(
                row["cpu_id"],
                row["keyword"],
                row["brand"],
                row["socket"],
                row["benchmark"],
                row["price"],
                row["performance_score"],
                row["game_score"],
                row["work_score"],
                row["ai_score"],
                row["value_score"],
                row["href"],
                row["image"]
            )
            cpus.append(cpu)

        return cpus


    def load_gpus(self):
        gpu_df = pd.read_csv("./data/gpu2.csv")

        numeric_cols = [
            "benchmark", "price", "performance_score",
            "game_score", "work_score", "ai_score", "value_score"
        ]
        for col in numeric_cols:
            gpu_df[col] = self._clean_numeric(gpu_df[col])

        gpu_df = gpu_df.dropna(subset=numeric_cols)

        gpus = []
        for _, row in gpu_df.iterrows():
            gpu = GPU(
                row["gpu_id"],
                row["model"],
                row["benchmark"],
                row["price"],
                row["performance_score"],
                row["game_score"],
                row["work_score"],
                row["ai_score"],
                row["value_score"],
                row["href"],
                row["image"]
            )
            gpus.append(gpu)

        return gpus


    def load_boards(self):

        board_df = pd.read_csv("./data/motherboard.csv")

        boards = []

        for _, row in board_df.iterrows():

            board = MotherBoard(
                board_id=row["board_id"],
                model=row["model"],
                socket=row["socket"],
                price=row["price"]
            )

            boards.append(board)

        return boards
    

    def update_values(self):
        cpu = pd.read_csv("./data/cpu.csv")
        price = pd.read_csv("./data/cpu_price.csv")
        
        gpu = pd.read_csv("./data/gpu.csv")
        gpu_price = pd.read_csv("./data/gpu_price.csv")
        
        # cpu_id 기준으로 합치기
        df = cpu.merge(price, on="cpu_id", how="left")
        df2 = gpu.merge(gpu_price, on="gpu_id", how="left")
        
        # 가성비 계산
        df["value"] = df["benchmark"] / df["price"]
        df2["value"] = df2["benchmark"] / df2["price"]

        # 소수점 둘째자리까지
        df["value"] = df["value"].round(4)
        df2["value"] = df2["value"].round(4)

        df.to_csv("./data/cpu2.csv", index=False)
        df2.to_csv("./data/gpu2.csv", index=False)


    def make_score_csv(self, input_file, price_file, output_file, id_column):
        
        df = pd.read_csv(input_file)
        price_df = pd.read_csv(price_file)

        df = pd.merge(
            df,
            price_df[[id_column, "price", "href", "image"]],
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


    def make_price_csv(self, input_file, output_file, id_column):
        
        crawl = Crawler()

        df = pd.read_csv(input_file)

        result = []

        for _, row in df.iterrows():

            product_id = row[id_column]
            keyword = row["keyword"]

            products = crawl.search(keyword)

            if not products:
                continue

            # 가장 저렴한 상품 선택
            cheapest = min(products, key=lambda x: x["price"])

            cheapest[id_column] = product_id

            result.append(cheapest)

        price_df = pd.DataFrame(result)

        # 컬럼 순서
        price_df = price_df[
            [id_column, "title", "price", "href", "image"]
        ]

        price_df.to_csv(
            output_file,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"{output_file} 저장 완료")

# d = DatasetManager()
# d.make_score_csv("./data/cpu.csv", "./data/cpu_price.csv", "./data/cpu2.csv", "cpu_id")
# d.make_score_csv("./data/gpu.csv", "./data/gpu_price.csv", "./data/gpu2.csv", "gpu_id")

# d.make_score_csv("./data/ram.csv", "./data/ram_price.csv", "./data/ram2.csv", "ram_id")