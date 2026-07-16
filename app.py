from flask import Flask, render_template, request, Response, jsonify
import csv
import io
from product_manager import ProductManager
from recommender import Recommender
from analyzer import PriceAnalyzer
from dataset_manager import DatasetManager
from buytiming_analyzer import BuyTimingAnalyzer
from price_predictor import PricePredictor
from history_manager import HistoryManager

app = Flask(__name__)
recommender = Recommender()
analyzer = PriceAnalyzer()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    buytiming_analyzer = BuyTimingAnalyzer()

    budget = request.args.get("budget", type=int)
    purpose = request.args.get("purpose")
    budget2 = budget * 0.7
    results = recommender.recommend(budget2, purpose)

    if results:
        top = results[0]

        cpu_history_obj = top.cpu.price_history
        gpu_history_obj = top.gpu.price_history

        predictor = PricePredictor()
        cpu_prediction = predictor.predict_next_7days(cpu_history_obj) if cpu_history_obj else []
        gpu_prediction = predictor.predict_next_7days(gpu_history_obj) if gpu_history_obj else []

        try:
            top.cpu.price_analysis = buytiming_analyzer.analyze(cpu_history_obj, cpu_prediction)
            top.gpu.price_analysis = buytiming_analyzer.analyze(gpu_history_obj, gpu_prediction)
        except AttributeError as e:
            print("analyze 에러:", e)
            top.cpu.price_analysis = None
            top.gpu.price_analysis = None

        top.cpu.price_history = cpu_history_obj.records if cpu_history_obj else []
        top.gpu.price_history = gpu_history_obj.records if gpu_history_obj else []

    return render_template(
        "search.html",
        budget=budget,
        purpose=purpose,
        results=results
    )


@app.route("/api/gpu-price-history")
def gpu_price_history():
    gpu_model = request.args.get("gpu")

    history_manager = HistoryManager("gpu_history.csv")
    price_history = history_manager.get_history(gpu_model)

    predictor = PricePredictor(price_history)
    analyzer = BuyTimingAnalyzer(price_history, predictor)
    timing = analyzer.analyze()
    # {"current_price":950000,"predicted_price":935000,"expected_change":-15000,
    #  "expected_change_rate":-1.58,"price_score":80,"recommendation":"..."}

    return jsonify({
        "history": [
            {"date": d, "price": p} for d, p in zip(price_history.dates, price_history.prices)
        ],
        "timing": timing
    })



@app.route("/search/download")
def download_csv():
    budget = request.args.get("budget", type=int)
    budget2 = budget*0.7
    purpose = request.args.get("purpose")

    combinations = recommender.recommend(budget2, purpose) 
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "순위", "CPU", "CPU 가격", "GPU", "GPU 가격",
        "총 가격", "종합 점수", "가성비 점수", "밸런스 점수", "예산 사용률(%)"
    ])

    for i, item in enumerate(combinations, start=1):
        writer.writerow([
            i,
            item.cpu.keyword,
            item.cpu.price,
            item.gpu.model,
            item.gpu.price,
            item.cpu.price + item.gpu.price,
            round(item.final_score, 1),
            round(item.value_score, 1),
            round(item.balance_score, 1),
            round(item.budget_usage, 1),
        ])

    csv_data = output.getvalue()
    output.close()

    # 한글 깨짐 방지 (엑셀에서 열 때) - BOM 추가
    csv_bytes = "\ufeff" + csv_data

    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=pc_recommendation_{budget}_{purpose}.csv"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)














# import pandas as pd

# @app.route("/cpu")
# def cpu():
#     df = pd.read_csv("./data/cpu2.csv")
#     return df.head().to_html()

# @app.route("/recommend")
# def recommend_page():

#     best_cpu, best_gpu, score = recommender.recommend(
#         budget=4000000,
#         purpose="ai"
#     )

    
#     history = dataset.load_price_history(
#         "./data/cpu_history.csv",
#         best_cpu.cpu_id
#     )
#     history2 = dataset.load_price_history(
#         "./data/gpu_history.csv",
#         best_gpu.gpu_id
#     )
    
#     price_info = analyzer.analyze_price(history)
#     price_info2 = analyzer.analyze_price(history2)
#     graph_path = analyzer.draw_price_graph(history)
#     graph_path2 = analyzer.draw_price_graph(history2)

#     return render_template(
#     "result.html",
#     price_info=price_info,
#     price_info2=price_info2,
#     score = score,
#     graph_path=graph_path,
#     graph_path2=graph_path2
# )


# if __name__ == "__main__":
#     app.run(debug=True)


