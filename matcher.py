import pandas as pd
import re

class ProductMatcher:
    def match_products(self, products, csv_file, id_column):

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