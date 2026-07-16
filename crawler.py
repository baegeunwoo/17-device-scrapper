import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class Crawler:


    def _normalize(self, s):
        return re.sub(r"[^0-9a-zA-Z가-힣]", "", s).lower()
    

    def search(self, keyword):

        url = f"https://search.danawa.com/dsearch.php?query={keyword}&tab=main"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        prod_list = soup.find("div", class_="main_prodlist main_prodlist_list")
        lis = prod_list.find_all("li", class_="prod_item")

        products = []
        kw_norm = self._normalize(keyword)

        for li in lis:
            a = li.select_one("p.prod_name a")
            b = li.select_one("p.price_sect a")
            img = li.select_one("div.thumb_image img")

            if not a or not b:
                continue

            title = a.get_text(strip=True)
            price = b.get_text(strip=True)

            numbers = re.sub(r"[^0-9]", "", price)
            if numbers == "":
                continue
            price = int(numbers)

            href = a.get("href")

            # data-src 우선, 없으면 src (lazy loading 대응)
            img_src = None
            if img:
                img_src = img.get("data-src") or img.get("src")

            # 키워드가 제목에 실제로 포함된 경우만 채택
            if kw_norm not in self._normalize(title):
                continue
            BUNDLE_KEYWORDS = ["조립", "완조립", "데스크탑", "데스크톱", "세트PC", "게이밍PC", "PC세트"]
            if any(word in title for word in BUNDLE_KEYWORDS):
                continue

            data = {
                "title": title,
                "price": price,
                "href": href,
                "image": img_src
            }

            products.append(data)

        return products
    

    def save_price(self, matched, path):

        df = pd.DataFrame(matched)

        df.to_csv(
            "./"+path,
            index=False,
            encoding="utf-8-sig"
        )

# c = Crawler()
# a=c.search("cpu")
# print(a)