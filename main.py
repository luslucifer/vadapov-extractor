import requests
from bs4 import BeautifulSoup
import re
import json
from flask import Flask
import os , sys


class VadaPov:
    def __init__(self):
        self.ROOT = 'https://vadapav.mov'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.tmdb_api_key = 'f6f2a9e9b0f5eed81b4cabe35d5a9c1b'  # Move API key to a variable
        self.MvStringPattern = r'\d{3,4}p'


    def getTmdbTitle(self, id: str | int):
        url = f'https://api.themoviedb.org/3/movie/{id}?append_to_response=videos&api_key={self.tmdb_api_key}'
        res = requests.get(url).json()
        title = res['title'].replace(':','')
        release_year = res['release_date'][:4]
        ul_title = f'{title} ({release_year})'
        return title, ul_title

    def get_links(self, query: str):
        arr = []
        res = requests.get(url=f'{self.ROOT}/s/{query}', headers=self.headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        directory_div = soup.find('div', class_='directory')
        links = directory_div.find_all('a')
        for link in links:
            part = link.get('href')
            arr.append(f'{self.ROOT}{part}')
        return arr
    def extract_file_details (self,li:BeautifulSoup): 
        try:
            a = li.find('a')
            size = li.find('div',class_='size-div').get_text()
            partial_link = a.get('href')
            link = f'{self.ROOT}{partial_link}'
            name = a.get_text()
            quality = None
            match = re.search(self.MvStringPattern,name)
            if match : 
                quality = match.group()

            type_ = name.split('.')[-1]
            # print(a.get_text())
            return {'name':name,'downloadLink':link,'size':size,'quality':quality,'type':type_}
        
        except Exception as err : 
            print(err)
            # return err


    def process_link(self, link: str):
        res = requests.get(link, headers=self.headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        directory_div = soup.find('div', class_='directory')
        lis = directory_div.find_all('li')
        arr = []
        for li in lis:
            obj = self.extract_file_details(li)
            if obj:
                arr.append(obj)
        return arr
    
    def main(self, id: str | int):
        title, ul_title = self.getTmdbTitle(id)
        links = self.get_links(ul_title)
        arr = []
        if links:
            for link in links :
                ar = self.process_link(link)
                arr = arr+ar
        return arr
    

app = Flask(__name__)

@app.route('/')
def home():
    return ' made in chaina '


@app.route('/<id>')
def Movie(id):
    try :  
        v = VadaPov()
        x = v.main(id)
        return x
    except Exception as err : 
        return {'message':'movie not found '}
if __name__ == "__main__":
    port = os.getenv("PORT", "8000")  # Default to port 8000 if PORT is not set
    command = f"gunicorn -b 0.0.0.0:{port} main:app"
    os.system(command)
    