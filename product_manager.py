import pandas as pd

from cpu import CPU
from gpu import GPU


class ProductManager:

    @staticmethod
    def load_products():

        cpus = []
        gpus = []

        cpu_df = pd.read_csv("./data/cpu2.csv")

        for _, row in cpu_df.iterrows():

            cpu = CPU(
                cpu_id=row["cpu_id"],
                keyword=row["keyword"],
                price=row["price"],
                brand=row["brand"],
                socket=row["socket"],
                benchmark=row["benchmark"],
                performance_score=row["performance_score"],
                game_score=row["game_score"],
                work_score=row["work_score"],
                ai_score=row["ai_score"],
                value_score=row["value_score"]
            )

            cpus.append(cpu)


        gpu_df = pd.read_csv("./data/gpu2.csv")

        for _, row in gpu_df.iterrows():

            gpu = GPU(
                gpu_id=row["gpu_id"],
                model=row["model"],
                price=row["price"],
                benchmark=row["benchmark"],
                game_score=row["game_score"],
                work_score=row["work_score"],
                ai_score=row["ai_score"],
                value_score=row["value_score"],
                performance_score=row["performance_score"]
            )

            gpus.append(gpu)


        return {
            "cpu": cpus,
            "gpu": gpus
        }