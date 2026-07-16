from dataset_manager import DatasetManager
from recommender import Recommender
from buytiming_analyzer import BuyTimingAnalyzer
from price_predictor import PricePredictor
from history_manager import HistoryManager

def main():
    history_manager = HistoryManager()

    predictor = PricePredictor()

    analyzer = BuyTimingAnalyzer()


    history = history_manager.load_history(
        "./data/gpu_history.csv",
        "product_id",
        1
    )

    prediction = predictor.predict_next_7days(history)

    result = analyzer.analyze(
        history,
        prediction
    )

    print(result)


if __name__ == "__main__":
    main()