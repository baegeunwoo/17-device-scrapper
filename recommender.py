import pandas as pd
from score import ScoreCalculator
from dataset_manager import DatasetManager
from recommendation_result import RecommendationResult
class Recommender:

    def __init__(self):
        self.data = DatasetManager()
        self.score = ScoreCalculator()

    def recommend(self, budget, purpose):

        cpus = self.data.load_cpus()
        gpus = self.data.load_gpus()

        combinations = []

        for cpu in cpus:

            for gpu in gpus:

                # 예산 초과하면 제외
                if cpu.price + gpu.price > budget:
                    continue

                # 각 점수 계산
                performance_score = self.score.calculate_score(
                    cpu,
                    gpu,
                    purpose
                )

                value_score = self.score.calculate_value_score(
                    cpu,
                    gpu
                )

                balance_score = self.score.calculate_balance_score(
                    cpu,
                    gpu
                )

                budget_usage = (
                    (cpu.price + gpu.price)
                    / budget
                ) * 100

                final_score = self.score.calculate_final_score(
                    cpu,
                    gpu,
                    purpose
                )

                # 결과 객체 생성
                result = RecommendationResult(
                    cpu=cpu,
                    gpu=gpu,
                    final_score=final_score,
                    performance_score=performance_score,
                    value_score=value_score,
                    balance_score=balance_score,
                    budget_usage=budget_usage
                )

                combinations.append(result)

        # 점수 높은 순으로 정렬
        combinations.sort(
            key=lambda x: x.final_score,
            reverse=True
        )

        # 상위 N개만 가격 히스토리 로드 (예: 상위 3개)
        for result in combinations[:3]:
            result.cpu.price_history = self.data.load_price_history(
                "./data/cpu_history.csv", result.cpu.cpu_id
            )
            result.gpu.price_history = self.data.load_price_history(
                "./data/gpu_history.csv", result.gpu.gpu_id
            )

        return combinations
    

    def recommend_motherboard(self, cpu):

        mb_df = pd.read_csv("./data/motherboard.csv")

        compatible = mb_df[
            mb_df["socket"] == cpu.socket
        ]

        compatible = compatible.sort_values("price")

        return compatible.iloc[0]