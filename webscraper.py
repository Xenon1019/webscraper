from bs4 import BeautifulSoup
import requests, re, datetime
import csv, sqlite3

url = 'https://www.theverge.com/'
bs4_parser = 'lxml'
db_file = 'article.db'
def get_link_data(link):
    response = requests.get(link).text
    link_soup = BeautifulSoup(response, bs4_parser)
    
    def get_meta_property(property):
        return link_soup.find('meta', attrs={'property': property})
    content_type = get_meta_property('og:type')
    if content_type is None or content_type['content'] != 'article':
        return None
    url = get_meta_property('og:url')['content']
    headline = get_meta_property('og:title')['content']
    author = get_meta_property('author')['content']
    publish_date = get_meta_property('article:published_time')['content'][:10]

    return [url, headline, author, publish_date]
print(__name__)
if __name__ == 'main':
    response = requests.get(url).text
    soup = BeautifulSoup(response, bs4_parser)

    data_id = '__NEXT_DATA__'
    page_data = soup.find('script', id=data_id)
    if page_data is None:
        raise Exception(f"The page data can not be recognized.\
                        The webpage does not contain a <script id='{data_id}'>")

    page_data = str(page_data.text)
    pattern = re.compile(f"\"({url}\d+[^\"]*)\"")
    links = set(pattern.findall(page_data))

    print(f'{len(links)} links found. Scanning the links...')
    csv_file_name = datetime.date.today().strftime("%d%m%Y") + '_verge.csv'

    with open(csv_file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['id', 'url', 'headline', 'author', 'date'])
        id = 0
        for link in links:
            link_data = get_link_data(link)
            print(f'Scanning... {link}')
            if link_data is None:
                print(f'Link data not found.')
                continue
            writer.writerow([id] + get_link_data(link))
            id += 1

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    table_name = 'Articles'
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY,
    url TEXT,
    headline TEXT,
    author TEXT,
    date 
    );''')

    with open(csv_file_name) as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  #Skip the headers

        for row in csv_reader:
            row[0] = int(row[0])
            cur.execute(f'INSERT INTO {table_name} VALUES(?, ?, ?, ?, DATE(?))', row)
    conn.commit()
