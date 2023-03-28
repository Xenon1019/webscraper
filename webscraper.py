from bs4 import BeautifulSoup
import requests, re, datetime
import csv, sqlite3

verge_url = 'https://www.theverge.com/'
bs4_parser = 'lxml'
db_file = 'article.db'

class Scraper:
  def __init__(self, url, parser):
    self.url = url
    self.parser = parser
    self.links = None
    self.last_saved_file = None


  def get_link_data(self, link):
    response = requests.get(link).text
    link_soup = BeautifulSoup(response, self.parser)

    def get_meta_property(property):
      return link_soup.find('meta', attrs={'property': property})

    content_type = get_meta_property('og:type')
    if content_type is None or content_type['content'] != 'article':
     return None

    link_data = [get_meta_property(property)['content'] \
      for property in [
        'og:url', 
        'og:title', 
        'author', 
        'article:published_time'
        ]]
    link_data[3] = link_data[3][:10]
    return link_data


  def scrape(self):
    response = requests.get(self.url).text
    soup = BeautifulSoup(response, self.parser)

    #Look for data in script tag with id '__NEXT_DATA__'
    data_id = '__NEXT_DATA__'
    page_data = soup.find('script', id=data_id)
    if page_data is None:
        raise Exception(f"The page data can not be recognized.\
                        The webpage does not contain a <script id='{data_id}'>")
    page_data = str(page_data.text)

    #Look for weblinks that matches the regexp pattern.
    pattern = re.compile(f"\"({verge_url}\d+[^\"]*)\"")
    self.links = set(pattern.findall(page_data))
    print(f'{len(self.links)} links found.')


  def write_to_csv(self, csv_file=None):
    if self.links is None:
      raise Exception('Scraper never run.')
    if csv_file is None:
      csv_file = datetime.date.today().strftime('%d%m%Y_verge.csv')
    
    with open(csv_file, 'w') as csv_file_handle:
      writer = csv.writer(csv_file_handle)
      writer.writerow(['id', 'url', 'headline', 'author', 'date'])
      id = 0
      for link in self.links:
        link_data = self.get_link_data(link)
        print(f'Scanning... {link}')
        if link_data is None:
          print(f'Link data not found.')
          continue
        writer.writerow([id] + link_data)
        id += 1
    self.last_saved_file = csv_file


  def write_to_db(self, file=db_file):
    if self.last_saved_file is None:
      raise Exception('No file to write to database. First run write_to_csv.')
    conn = sqlite3.connect(file)
    try:
      cursor = conn.cursor()
      table_name = 'Articles'
      cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY,
        url TEXT,
        headline TEXT,
        author TEXT,
        date 
      );''')

      with open(self.last_saved_file) as csv_file_handle:
        csv_reader = csv.reader(csv_file_handle)
        next(csv_reader)  #Skip the headers
        for row in csv_reader:
          row[0] = int(row[0])
          cursor.execute(f'INSERT INTO {table_name} VALUES(?, ?, ?, ?, DATE(?))', row)
      conn.commit()
    except sqlite3.Error as e:
      raise Exception(f'SQLite Error {e.sqlite_errorcode}: {e.sqlite_errorname}')
    finally:
      conn.close()



if __name__ == '__main__':
    scraper = Scraper(verge_url, bs4_parser)
    scraper.scrape()
    scraper.write_to_csv()
    scraper.write_to_db()
