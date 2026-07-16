from dataset_manager import DatasetManager
from recommender import Recommender
from analyzer import PriceAnalyzer
from matcher import ProductMatcher
from crawler import Crawler

def main():
    # p = ProductMatcher()
    # c = Crawler()
    # dataset = DatasetManager()

    # ram = p.match_products(c.search("RAM"), "./data/ram.csv", "ram_id")
    # cpu = p.match_products(c.search("CPU"), "./data/cpu.csv", "cpu_id")
    # gpu = p.match_products(c.search("RTX"), "./data/gpu.csv", "gpu_id")
    
    # dataset.make_price_csv("./data/cpu.csv", "./data/cpu_price.csv","cpu_id")
    # dataset.make_price_csv("./data/gpu.csv", "./data/gpu_price.csv","gpu_id")
    # dataset.make_price_csv("./data/ram.csv", "./data/ram_price.csv","ram_id")
    
    import pandas as pd
    import numpy as np
    cpu_df = pd.read_csv("./data/cpu2.csv")

    numeric_cols = ["price", "benchmark", "performance_score", "game_score",
                    "work_score", "ai_score", "value_score"]

    for col in numeric_cols:
        cleaned = (
            cpu_df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        cpu_df[col] = pd.to_numeric(cleaned, errors="coerce")

    print(cpu_df.dtypes)
    print(cpu_df[numeric_cols].isna().sum())
    # d = DatasetManager()
    # d.make_score_csv("./data/cpu.csv", "./data/cpu_price.csv", "./data/cpu2.csv", "cpu_id")
    # d.make_score_csv("./data/gpu.csv", "./data/gpu_price.csv", "./data/gpu2.csv", "gpu_id")

    # d.make_score_csv("./data/ram.csv", "./data/ram_price.csv", "./data/ram2.csv", "ram_id")

    # recommender = Recommender()
    # # analyzer = PriceAnalyzer()

    # money = int(input("예산을 입력하세요 : "))

    # budget = money * 0.7

    # results = recommender.recommend(
    #     budget,"game"
    # )

    # top3 = results[:3]

    # best = results[0]

    # print(best.cpu.keyword)
    # print(best.gpu.model)
    # print(best.final_score)
    # print(best.value_score)
    # print(best.balance_score)
    # print(best.budget_usage)


    # for result in top3:

    #     print("-------------------")
    #     print(result.cpu.keyword)
    #     print(result.gpu.model)
    #     print(result.final_score)

    # board = recommender.recommend_motherboard(cpu)

    # analyzer.analyze_price(
    #     "./data/cpu_price_history.csv",
    #     cpu.cpu_id
    # )

    # analyzer.analyze_price(
    #     "./data/gpu_price_history.csv",
    #     gpu.gpu_id
    # )

    # analyzer.draw_price_graph(
    #     "./data/gpu_price_history.csv",
    #     gpu.gpu_id
    # )


if __name__ == "__main__":
    main()