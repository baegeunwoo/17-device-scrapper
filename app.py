from flask import Flask, render_template, request
from product_manager import ProductManager
from recommender import Recommender
from analyzer import PriceAnalyzer
from dataset_manager import DatasetManager

app = Flask(__name__)
recommender = Recommender()
analyzer = PriceAnalyzer()
# dataset = DatasetManager()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    budget = request.args.get("budget", type=int)
    purpose = request.args.get("purpose")

    results = recommender.recommend(budget, purpose)

    # 템플릿(JS 차트)에서 쓸 수 있게, 상위 1위의 price_history를
    # PriceHistory 객체가 아니라 순수 리스트로 변환
    if results:
        top = results[0]
        top.cpu.price_history = (
            top.cpu.price_history.records if top.cpu.price_history else []
        )
        top.gpu.price_history = (
            top.gpu.price_history.records if top.gpu.price_history else []
        )

    top.cpu.price_analysis = analyzer.analyze_price(
    top.cpu.price_history, top.cpu.keyword
    )
    top.gpu.price_analysis = analyzer.analyze_price(
        top.gpu.price_history, top.gpu.model
    )
    return render_template(
        "search.html",
        budget=budget,
        purpose=purpose,
        results=results
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


