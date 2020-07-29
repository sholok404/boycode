import requests

# Creating boycotts list
from bs4 import BeautifulSoup

soup = BeautifulSoup(requests.get('https://www.ethicalconsumer.org/ethicalcampaigns/boycotts').text, 'lxml')

boycotts = {}

for boycott in soup.find_all('div', 'boycott'):
    boycotts[boycott.h3.string.casefold()] = {'Category': boycott.select('.field--name-field-category')[0].string,
            'Called By' : boycott.select('.field--name-field-called-by')[0].a.string,
            'Boycott Started' : boycott.select('.field--name-field-date-boycott-started')[0].time.string}


# The actual program

apikey = 'EAFC5A4C71DB785D50B15B8957F0FF19'
def lookup_brand(barcode):
    url = 'https://api.upcdatabase.org/product/' + barcode + '?apikey=' + apikey
    resp_json = requests.get(url).json()
    if resp_json['success']:
        if resp_json['brand']:
            return resp_json['brand']
        elif resp_json['manufacturer']:
            return resp_json['manufacturer']
        elif resp_json['description']:
            return resp_json['description']
        else:
            return 'unidentifiable'
    else:
        return 'error'

import re
def investigate(brand):
    for key, val in boycotts.items():
        if re.search(key, brand):
            return (True, key, val)
    return (False, brand , False)
            

from flask import Flask
from flask import request
from flask import render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', verdict=None, message=None)

@app.route('/boycott', methods=['GET', 'POST'])
def boycott():
    if request.method == 'POST':
        brand = lookup_brand(request.form['barcode'])
        investigation =  investigate(brand.casefold())
        
        if brand == 'error':
           return render_template('index.html', verdict='red', message='Make sure you\'ve entered the barcode correctly')
        elif brand == 'unidentifiable':
            return render_template('index.html', verdict='red', message='The product\'s brand couldn\'t be identified')
        elif investigation[0]:
            message = 'This product is associated with the company ' + investigation[1] + ' which has had a boycott called on it by ' + investigation[2]['Called By'] + ' since ' + investigation[2]['Boycott Started'] + ' due to ' + investigation[2]['Category'] + ' violations.'
            return render_template('index.html', verdict='red', message=message)
        else:
            message = 'This product, \'' + investigation[1] + '\'s\' company does not seem to have any boycott associated with it'
            return render_template('index.html', verdict='green', message=message)
 
if __name__ == "__main__":
    app.run()