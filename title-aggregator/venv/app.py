from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

def get_titles_from_the_verge():
    url = 'https://www.theverge.com/'
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        titles = []

        for h2_tag in soup.find_all('h2', class_='font-polysans'):
            a_tag = h2_tag.find('a', class_='group-hover:shadow-underline-franklin')
            time_tag = h2_tag.find_next('time')

            if a_tag and time_tag:
                title = a_tag.get_text()
                href = a_tag.get('href')
                pub_time = time_tag.get('datetime')  

                if title and href and pub_time:
                    if not href.startswith('http'):
                        href = 'https://www.theverge.com' + href

                    try:
                        article_date = datetime.fromisoformat(pub_time.replace("Z", "+00:00"))
                        if article_date >= datetime(2022, 1, 1, tzinfo=article_date.tzinfo):
                            titles.append({'title': title.strip(), 'link': href, 'date': article_date})
                    except Exception as e:
                        print(f"Error parsing date for article '{title}': {e}")
                        continue

        titles.sort(key=lambda x: x['date'], reverse=True)

        return titles
    except Exception as e:
        print(f"Error scraping The Verge: {e}")
        return []

@app.route('/')
def home():
    titles = get_titles_from_the_verge()
    return render_template('index.html', titles=titles)

if __name__ == '__main__':
    app.run(debug=True)
