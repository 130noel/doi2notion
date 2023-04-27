# 必要なライブラリをインポートする
import pyperclip
import requests
from notion_client import Client

# クリップボードからDOIのURLを取得する
doi_url = pyperclip.paste()
doi = '/'.join(doi_url.split('/')[-2:]) #doiを抽出して取り出す

# CrossRefのエンドポイントを設定
crossref_endpoint = 'https://api.crossref.org/works/'

# NotionのAPIキーとデータベースIDを設定してください
notion_api = 'your_api'
notion_db = 'your_db_id'

# Notionの初期化
notion = Client(auth=notion_api)
database = notion.databases.retrieve(database_id=notion_db)

# 論文の情報（JSON）を取得しPythonの辞書形式に変換
url = f"{crossref_endpoint}{doi}"
headers = {'Accept': 'application/json'}
params = {'mailto': 'your_mail_adress'}  # 任意
response = requests.get(url, headers=headers, params=params)


if response.status_code == 200:
    data = response.json()
    if 'message' in data:
        data = data['message']
        title = data['title'][0] if 'title' in data else ''
        authors = ', '.join(author['given'] + ' ' + author['family'] for author in data['author']) if 'author' in data else ''
        year = data['created']['date-parts'][0][0] if 'created' in data else ''
        journal = data['container-title'][0] if 'container-title' in data else ''
        filename = title.replace(' ', '_') + '.pdf'
        url = data['URL'] if 'URL' in data else ''
        abstract = data['abstract'] if 'abstract' in data else ''
        doi = data['DOI'] if 'DOI' in data else ''
        type = 'Journal Article'
        bibtex = f"@article{{{doi},\n author = {{{authors}}},\n title = {{{title}}},\n journal = {{{journal}}},\n year = {{{year}}},\n doi = {{{doi}}}\n}}"

        # Notionにデータを格納する
        new_page = {
            'Title': {'title': [{'text': {'content': title}}]},
            'Authors': {'rich_text': [{'text': {'content': authors}}]},
            'Year': {'number': int(year)},
            'Journal': {'rich_text': [{'text': {'content': journal}}]},
            'Filename': {'rich_text': [{'text': {'content': filename}}]},
            'URL': {'url': url},
            'Abstract': {'rich_text': [{'text': {'content': abstract}}]},
            'DOI': {'rich_text': [{'text': {'content': doi}}]},
            'Type': {'select': {'name': type}},
            'Bibtex': {'rich_text': [{'text': {'content': bibtex}}]}
        }

        notion.pages.create(parent={'database_id': notion_db}, properties=new_page)
    else:
        print('No message in data')
else:
    print('Request failed with status code', response.status_code)
