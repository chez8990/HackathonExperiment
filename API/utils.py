import base64
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
from io import BytesIO


MASK = np.array(Image.open('meta/circle.png'))
COMPANIES = pd.read_csv('../Data/companies.csv', dtype={'Stock Code':str})
COMPANIES['Stock Code'] = COMPANIES['Stock Code'].str.slice(1)
CODES = pd.read_csv('../Data/companies_match.csv')
CODES['Stock Code'] = CODES['Stock Code'].astype(str).str.zfill(4)

def edit_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def get_closest_company_code(name, companies):
    companies['Dist'] = companies['Stock Name'].apply(lambda x: edit_distance(x, name))
    companies = companies.sort_values('Dist', ascending=True)
    code = companies.iloc[companies['Dist'].idxmin()]['Stock Code']

    del companies['Dist']
    return code

def wordcloud_as_base64(text):
    wordcloud = WordCloud(width=800, height=400, background_color="white", stopwords=STOPWORDS, mask=MASK).generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    image = BytesIO()
    plt.savefig(image, format='png')
    return base64.b64encode(image.getvalue()).decode('utf8')

def stock_as_base64(stock):
    plt.figure()
    stock.plot()
    image = BytesIO()
    plt.savefig(image, format='png')
    return base64.b64encode(image.getvalue()).decode('utf8')

def wordcloud(text):
    WC = WordCloud(width=800, height=400, max_font_size=50, max_words=100, background_color="white", stopwords=STOPWORDS)
    image = WC.generate(text).to_array()
    image = Image.fromarray(image)
    return image

def image_to_base64():
    image = BytesIO()
    plt.savefig(image, format='png')
    return base64.b64encode(image.getvalue()).decode('utf8')

def base64_to_image(b64):
    image = Image.open(BytesIO(base64.b64decode(b64)))
    image.save('test.png')
    return image


def get_date(dates, sent, ent_order):
    if (len(dates) == 0):
        ent_date = []
    else:
        ent_date = [d['value'] for d in dates if d['sent'] == sent]
        if (len(ent_date) == 0):
            ent_date = [d['value'] for d in dates if d['order'] < ent_order]
    return ([ent_date[0] if len(ent_date) != 0 else ''][0])


def match_org(org):
    api_key = "AIzaSyBM6PdtA2iP0ry04W8rCJkgRTk0vm01RfA"
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    params = {
        'query': org,
        'limit': 1,
        'indent': True,
        'key': api_key,
    }
    r = requests.get(service_url, params=params)

    for element in r.json()['itemListElement']:
          return element['result']['name']

def match_org_all(orgs):
    org_keys = []
    for org in orgs:
        org_key = match_org(org)
        org_keys.append(org_key)
    return (org_keys)

def get_stock_code(org_keys):
    return(CODES[CODES['Match'].isin(org_keys)]['Stock Code'])