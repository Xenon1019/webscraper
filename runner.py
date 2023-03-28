import datetime, time
from webscraper import Scraper, verge_url

def run_scraper(scraper):
  try:
    scraper.scrape()
    scraper.write_to_csv()
    scraper.write_to_db()
  except Exception as e:
    print(f'Error: {e.args}')

def main(last_run, scraper):
  while True:
    if last_run is None:
      run_scraper(scraper)
      last_run = datetime.datetime.now()
    else:
      diff = datetime.datetime.now() - last_run
      if diff.total_seconds() > (3 * 3600):
        last_run = None
        continue;
    time.sleep(60)

if __name__ == '__main__':
  last_run = None
  scraper = Scraper(verge_url, 'lxml')
  main(last_run, scraper)