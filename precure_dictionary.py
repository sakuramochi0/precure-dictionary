#!/usr/bin/env python3
import sys
import csv
from os import path
import time
import re

from bs4 import BeautifulSoup
import requests

dict_file = 'precure_dictionary.csv'

def get_dictionary():
    """
    Get words from prettycure.wikia.com.'
    """
    url_base = 'http://prettycure.wikia.com'
     
    url = url_base + '/wiki/Category:Cures'
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
     
    # get links
    links = soup(id='mw-pages')[0]('a')
     
    names = []
    for link in links:
        url = url_base + link['href']
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        soup = [x for x in soup(id='mw-content-text')[0].children][0].find_next_siblings('p')[0]

        for i in soup(class_='t_nihongo_kanji'):
            en = i.parent.previous
            # if a phrase is in " "
            match = re.search(r'"(.+?)"', en)
            if match:
                en = match.group(1)
            # if a phrase is in <b> tag
            if len(en) <= 1 and i.parent.find_previous('b'):
                en = i.parent.find_previous('b').text

            ja = i.text
            romaji = i.find_next(class_='t_nihongo_romaji').text
            names.append((en, ja, romaji))
            
        time.sleep(1)
     
    with open(dict_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(names)
    with open('html/' + dict_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(names)

def generate_html():
    """
    Generate the dictionary as html.
    """
    soup = BeautifulSoup()
    table = soup.new_tag('table')
    table['class'] = 'table table-striped'
    with open(dict_file) as f:
        dict = csv.reader(f)
        # headers
        tr = soup.new_tag('tr')

        th = soup.new_tag('th')
        th.append(soup.new_string('英語 / English'))
        th['class'] = 'col-xs-2'
        tr.append(th)

        th = soup.new_tag('th')
        th.append(soup.new_string('日本語 / Japanese'))
        th['class'] = 'col-xs-2'
        tr.append(th)

        th = soup.new_tag('th')
        th.append(soup.new_string('ローマ字 / Rōmaji'))
        th['class'] = 'col-xs-1'
        tr.append(th)

        table.append(tr)
        for words in dict:
            tr = soup.new_tag('tr')
            for word in words:
                td = soup.new_tag('td')
                td.append(soup.new_string(word))
                tr.append(td)
            table.append(tr)
        soup.append(table)
    
    with open('template.html') as f:
        template = f.read()
    
    with open('html/index.html', 'w') as f:
        html = template.format(table=soup.prettify(), size=path.getsize(dict_file) // 1000)
        f.write(html)

if __name__ == '__main__':
    if sys.argv[1] == 'generate_html':
        generate_html()
    elif sys.argv[1] == 'get_dictionary':
        get_dictionary()
