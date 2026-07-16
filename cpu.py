class CPU:

    def __init__(
        self,
        cpu_id,
        keyword,
        brand,
        socket,
        benchmark,
        price,
        performance_score,
        game_score,
        work_score,
        ai_score,
        value_score,
        href,
        img
    ):

        self.cpu_id = cpu_id
        self.keyword = keyword
        self.brand = brand
        self.socket = socket

        self.benchmark = benchmark
        self.price = price

        self.performance_score = performance_score
        self.game_score = game_score
        self.work_score = work_score
        self.ai_score = ai_score
        self.value_score = value_score
        self.href = href
        self.img = img
        self.price_history: "PriceHistory | None" = None