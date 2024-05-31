import requests
from bs4 import BeautifulSoup
import re
import json
from flask import Flask, request, jsonify
import os
from urllib.parse import quote

class VadaPov:
    def __init__(self):
        self.ROOT = 'https://vadapav.mov'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.tmdb_api_key = 'f6f2a9e9b0f5eed81b4cabe35d5a9c1b'
        self.MvStringPattern = r'\d{3,4}p'
        self.types = ['movie', 'tv']

    def getTmdbTitle(self, id, type_=0):
        t = ['title', 'name']
        url = f'https://api.themoviedb.org/3/{self.types[type_]}/{id}?append_to_response=videos&api_key={self.tmdb_api_key}'
        res = requests.get(url).json()
        title = res[t[type_]].replace(':', '')
        release_year = ''
        if type_ != 1:
            release_year = f" ({res['release_date'][:4]})"
        ul_title = f'{title}{release_year}'
        return ul_title

    def get_links(self, query):
        arr = []
        res = requests.get(url=f'{self.ROOT}/s/{quote(query)}', headers=self.headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        directory_div = soup.find('div', class_='directory')
        links = directory_div.find_all('a')
        for link in links:
            part = link.get('href')
            arr.append(f'{self.ROOT}{part}')
        return arr

    def extract_file_details(self, li, ss=None, ep=None):
        try:
            a = li.find('a')
            size = li.find('div', class_='size-div').get_text()
            partial_link = a.get('href')
            link = f'{self.ROOT}{partial_link}'
            name = a.get_text()
            quality = None
            match = re.search(self.MvStringPattern, name)
            if match:
                quality = match.group()
            type_ = name.split('.')[-1]
            default_obj = {'name': name, 'downloadLink': link, 'size': size, 'quality': quality, 'type_': type_}

            if ss and ep:
                default_obj['season'] = ss
                default_obj['episode'] = ep
            return default_obj

        except Exception as err:
            print(err)
    
    def process_link(self, link):
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

    def tv_season(self, link, no):
        res = requests.get(link, headers=self.headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        directory_div = soup.find('div', class_='directory')
        all_a = directory_div.find_all('a')
        for a in all_a:
            try:
                season_no = a.get_text()[-2:]
                if int(season_no) == int(no):
                    p_link = a.get('href')
                    link = f'{self.ROOT}{p_link}'
                    return link
            except Exception as err:
                print(err)
        return None

    def tv_download(self, link, ss, ep):
        res = requests.get(link, headers=self.headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        directory_div = soup.find('div', class_='directory')
        lis = directory_div.find_all('li')
        pattern = rf'S0?{ss}E0?{ep}\.'
        for li in lis:
            try:
                a = li.find('a')
                match_ = re.search(pattern, a.get_text())
                if match_:
                    return self.extract_file_details(li=li, ss=ss, ep=ep)
            except Exception as err:
                print(err)
        return None

    def main(self, id, ss=None, ep=None):
        if ss and ep:
            ul_title = self.getTmdbTitle(id, 1)
            links = self.get_links(ul_title)
            link = self.tv_season(links[0], ss)
            return [self.tv_download(link, ss, ep)]
        else:
            ul_title = self.getTmdbTitle(id, 0)
            links = self.get_links(ul_title)
            arr = []
            if links:
                for link in links:
                    ar = self.process_link(link)
                    arr.extend(ar)
            return arr

app = Flask(__name__)

@app.route('/')
def home():
    return 'Made in China (fun) . .....'

@app.route('/<id>')
def media(id):
    ss = request.args.get('ss')
    ep = request.args.get('ep')
    try:
        v = VadaPov()
        x = v.main(id, ss, ep)
        print(x)
        return jsonify(x)
    except Exception as err:
        return jsonify({'message': str(err)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
    v = VadaPov()
    x = v.main(297802)
    print(x)
