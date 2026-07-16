class PriceHistory:
    def __init__(self, product_id, product_name):
        self.product_id = product_id
        self.product_name = product_name
        self.records = []  # [(date, price), ...] 라고 가정

    def add_record(self, date, price):
        self.records.append({"date": date, "price": price})

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "records": self.records
        }