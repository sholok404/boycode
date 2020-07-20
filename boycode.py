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

def lookup_brand(barcode):
    url = 'https://api.upcitemdb.com/prod/trial/lookup?upc=' + barcode
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()['items'][0]['brand'].split()[0].casefold()
    else:
        return 'Make sure you\'ve entered the barcode correctly'

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
        if brand == 'Make sure you\'ve entered the barcode correctly':
            return render_template('index.html', verdict='red', message=brand)
        elif brand in boycotts:
            message = 'This product is associated with the company ' + brand.upper() + ' which has had a boycott called on it by ' + boycotts[brand]['Called By'] + ' since ' + boycotts[brand]['Boycott Started'] + ' due to ' + boycotts[brand]['Category'] + ' violations.'
            return render_template('index.html', verdict='red', message=message)
        else:
            message = 'This product is associated with the company ' + brand.upper() + ' which currently has no boycott called on it.'
            return render_template('index.html', verdict='green', message=message)

if __name__ == "__main__":
    app.run()
