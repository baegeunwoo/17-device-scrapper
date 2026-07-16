class RecommendationResult:

    def __init__(
        self,
        cpu,
        gpu,
        final_score,
        performance_score,
        value_score,
        balance_score,
        budget_usage
    ):
        self.cpu = cpu
        self.gpu = gpu

        self.final_score = final_score
        self.performance_score = performance_score
        self.value_score = value_score
        self.balance_score = balance_score
        self.budget_usage = budget_usage

    def to_dict(self):
        return {
            "cpu": self._part_to_dict(self.cpu),
            "gpu": self._part_to_dict(self.gpu),
            "final_score": self.final_score,
            "performance_score": self.performance_score,
            "value_score": self.value_score,
            "balance_score": self.balance_score,
            "budget_usage": self.budget_usage,
        }

    def _part_to_dict(self, part):
        data = dict(vars(part))  # CPU/GPU 객체의 속성들을 복사
        price_history = data.get("price_history")
        if price_history is not None:
            data["price_history"] = price_history.to_dict()
        return data