
import requests         # 發送 HTTP 請求，用來從網站抓取網頁內容
from bs4 import BeautifulSoup as bs  # 解析 HTML / XML，將字串轉成可以操作的樹狀結構
import lxml             # 上課用的解析器（解析器需已安裝）
import time             # 取得目前時間，或讓程式暫停一段時間，做延遲，避免被 PTT 封鎖
import json             # 處理 JSON 格式的資料（例如 API 回傳或儲存設定）
import re               # 正規表達式
from datetime import datetime
from time import sleep
import pprint


def month_extract():
    current_time: datetime = datetime.now()
    This_month : int = current_time.month
    return This_month


def get_last_month():
    current_month = month_extract()
    if int(month_extract()) == 1:
        return 12
    else:
        last_month = month_extract() -1
        return last_month


def fetch_ptt_search_page(keyword, page):
    url = f'https://www.ptt.cc/bbs/Stock/search?page={page}&q={keyword}'


    res = requests.get(url)


    if res.status_code != 200:
        raise RuntimeError(f'爬取網頁失敗，狀態碼:{res.status_code}')
    
    soup = bs(res.text, 'lxml')


    return soup


def filter_posts_by_month(soup, last_month):
    pattern = f"{last_month}/"
    target_urls = []
    base_url = 'https://www.ptt.cc'
    post_entries = soup.select('div.r-ent')


    for post in post_entries:
        date_tag = post.find('div', class_='date')
        date_text = date_tag.text


        if date_text.strip().startswith(pattern):
            p_url = post.select_one('div.title > a[href]')['href']
            complete_url = base_url + p_url
            target_urls.append(complete_url)
    return target_urls


def scrape_article_content(url):
    try:
        res = requests.get(url)
        soup = bs(res.text,'lxml')


        # 取標題
        meta_value = soup.select('span.article-meta-value')


        if len(meta_value) >= 3 :
            title = meta_value[2].text
        else :
            title = "格式錯誤"


        # 取時間
        if len(meta_value) >= 4 :
            time = meta_value[3].text
        else :
            time = "格式錯誤"
        
        # 取留言
        comments = []
        comment_list = soup.select('span.f3.push-content')
        for c in comment_list:
                    comments.append(c.text)
        
        # 取內容
        main_content = soup.select_one('#main-content')


        if main_content:
            unwanted_elements = main_content.select('.article-metaline, .article-metaline-right, span, div.push')


            for element in unwanted_elements:
                element.decompose()


            content = main_content.text.strip().replace('\n',' ')
        else:
            content ='無法提取內文'
        
        article_info ={
            "title" :  title,
            'url' : url,
            'time' : time,
            'comments' : comments,
            'content': content,
        }


        print(f"已成功:{title}")
        return article_info
    except Exception as e:
        print(f"爬取失敗{url}，錯誤原因:{e}")


def save_to_json(data, filename):
    output = json.dumps(data, ensure_ascii=False, indent=4)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output)


def scrape_ptt_article(keyword, page, last_month, output_file):
    
    soup = fetch_ptt_search_page(keyword, page)


    target_urls = filter_posts_by_month(soup, last_month)


    articles_list = []


    for url in target_urls:
        article_info = scrape_article_content(url)


        articles_list.append(article_info)
    save_to_json(articles_list, output_file)


    return articles_list


# ============
if __name__ == "__main__":
    articles = scrape_ptt_article(keyword='0050',output_file='ptt_stock_articles.json', page = 2, last_month = 3)
    

