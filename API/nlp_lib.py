import requests
import spacy
import numpy as np
import utils
import datetime
import yfinance

class NamedEntityRecognition:
    def __init__(self, nlp):
        self.nlp = nlp

    def find_entities(self, doc, entities=['ORG', 'PERSON', 'DATE', 'PERSON', 'GPE']):
        sentence_with_numbers = []
        for sentence in self.nlp(doc).sents:
            extracted_sentence = []
            for ent in sentence.ents:
                txt = ent.text.strip().replace('\n', ' ')
                label = ent.label_
                if label in entities and txt not in extracted_sentence:
                    extracted_sentence.append(txt)
            if extracted_sentence:
                sentence_with_numbers.append(extracted_sentence)
        return sentence_with_numbers

    @staticmethod
    def most_important_ent(ent_doc):
        current_max_count = 0
        max_word = None
        word_count = {}

        for ents in ent_doc:
            for ent in ents:
                if ent in word_count:
                    word_count[ent] += 1
                else:
                    word_count[ent] = 1

                if word_count[ent] > current_max_count:
                    max_word = ent
        return max_word

    def extract_interesting_entities(self, text, threshold=3):

        # find entities in each sentence with organization as label
        swn = self.find_entities(text)

        # find most important keyword (extracted from entities)
        kw = self.most_important_ent(swn)

        # append kw to the entities
        swn = [sen + [kw] if kw not in sen else sen for sen in swn]

        # remove duplicates from entities
        swn = list(np.unique(swn))

        if not swn or len(swn) < threshold:
            swn = [[ent.text for ent in NLP(text)]]

        return swn

def google_news_query(entities, lang='en', sort_by='relevancy', page='1',
                      top_n=10, sources=['Bloomberg', 'BBC', 'CNBC', 'Sky News'],
                      generate_wordcloud=True):
    # store query results
    query_results = []
    all_articles = []
    for k in entities:
        q = ' '.join(k)
        params = {'q': q,
                  'apiKey': '2fce71693d12423fadcb8f1871bf7b82',
                  'lang': lang,
                  'sortBy': sort_by,
                  # 'sources': ','.join(sources),
                  'page': page}

        r = requests.get('https://newsapi.org/v2/everything', params=params)

        articles = r.json()['articles']
        all_articles += articles
        if articles:
            for article in articles[:top_n]:
                package = {'value': article['description'], 'type':'news', 'display_value': article['content']}
                query_results.append(package)

    # generate wordcloud
    all_text = '\n'.join([art['description'] for art in all_articles])

    try:
        ### word cloud generation

        utils.wordcloud(all_text)
        wordcloud_image_base64 = utils.wordcloud_as_base64(all_text)
        # wordcloud_image_base64 = utils.image_to_base64()
        # wordcloud_image_base64 = utils.wordcloud_as_base64(all_text)
        package = {'value': wordcloud_image_base64, 'type': 'image'}
        query_results = [package] + query_results
        utils.base64_to_image(wordcloud_image_base64)

        ### tabular extraction
        tables = tabular_extracion(NLP(all_text), all_text)
        package = {'value': tables, 'type':'table'}
        query_results = [package] + query_results

    except Exception as e:
        print(e)
        pass
    return query_results

def tabular_extracion(doc, txt):
    sents = [i for l in [str(s).split(',') for s in list(doc.sents)] for i in l]
    sents_start = np.array([txt.find(sents[i]) for i in range(len(sents))])
    sents_end = sents_start + np.array([len(sents[i]) for i in range(len(sents))])

    sents_idx = []
    for end in [e.end_char for e in doc.ents]:
        sents_idx.append([i for i, x in enumerate(end <= sents_end) if x][0])

    ents_data = []
    for i in range(len(doc.ents)):
        ent = doc.ents[i]
        sent = sents_idx[i]
        if ent.label_ in ['DATE', 'TIME', 'MONEY', 'PERCENT', 'CARDINAL', 'QUANTITY']:
            ents_data.append({
                'value': ent.text,
                'item': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'sent': sent,
                'order': i
            })

    dates = [d for d in ents_data if d['item'] in ['DATE', 'TIME']]
    data = [d for d in ents_data if d['item'] in ['MONEY', 'PERCENT', 'CARDINAL', 'QUANTITY']]
    for v in data:
        v['date'] = utils.get_date(dates, v['sent'], v['order'])
    data = [{'value': d['value'], 'item': d['item'], 'date': d['date']} for d in data]
    data = [list(d.values()) for d in data]
    data.insert(0, ['Value', 'Item', 'Date'])

    return data
    # output = {
    #     'value': data,
    #     'type': 'table'
    # }
    # return [output]

def hkex_query(entities):
    return None

def stock_data(text):
    doc = NLP(text)
    org_keys = utils.match_org_all([e.text for e in doc.ents if e.label_ == 'ORG'])
    stock_codes = utils.get_stock_code(org_keys)

    upper = datetime.datetime.today() - datetime.timedelta(days=30)
    lower = datetime.datetime.today()

    upper = upper.strftime('%Y-%m-%d')
    lower = lower.strftime('%Y-%m-%d')

    results = []

    for code in stock_codes:
        df = yfinance.download('{}.HK'.format(code), start=upper, end=lower)
        df = df['Adj Close']

        plots_base64 = utils.stock_as_base64(df)
        # df.plot()
        # plots_base64 = utils.image_to_base64()
        package = {'value': plots_base64, 'type': 'image'}
        results.append(package)
    return results

def twitter_data(entities):
    return None

def law_suits_data(entities):
    return None

NLP = spacy.load("en_core_web_sm")
NER = NamedEntityRecognition(NLP)

