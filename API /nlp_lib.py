import requests
import spacy
import numpy as np

nlp = spacy.load("en_core_web_sm")

class NamedEntityRecognition:
    def __init__(self, nlp):
        self.nlp = nlp

    def find_entities(self, doc, entities=['ORG', 'PERSON', 'DATE']):
        sentence_with_numbers = []
        for sentence in nlp(doc).sents:
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

class GoogleNewsQuery(NamedEntityRecognition):
    def __init__(self, nlp, api_key):
        self.api_key = api_key
        self.url = 'https://newsapi.org/v2/everything?'
        super().__init__(nlp)

    def query(self, text, from_date='2019-10-03', lang='en', sortBy='relevancy', page='1'):

        # find entities in each sentence with organization as label
        swn = self.find_entities(text)

        # find most important keyword (extracted from entities)
        kw = self.most_important_ent(swn)

        # append kw to the entities
        swn = [sen + [kw] if kw not in sen else sen for sen in swn]

        # remove duplicates from entities
        swn = list(np.unique(swn))

        # store query results
        query_results = []

        for k in swn:
            q = ' '.join(k)
            params = {'q': q,
                      'from': from_date,
                      'apiKey': self.api_key,
                      'lang': 'en',
                      'sortBy': 'relevancy',
                      'page': '1'}

            r = requests.get(self.url, params=params)

            if r.json()['articles']:
                query_results.append((q, r.json()))

        return query_results

class HKEXNewsQuery(NamedEntityRecognition):
    def __init__(self):
        super().__init__()

class StockDataAPI(NamedEntityRecognition):
    def __init__(self):
        super().__init__()

class TwitterAPI(NamedEntityRecognition):
    def __init__(self):
        super().__init__()

class LawSuitAPI(NamedEntityRecognition):
    def __init__(self):
        super().__init__()
