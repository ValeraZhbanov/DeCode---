

import pandas as pd
import yake
import requests
import os


class FileSearchEngine:


    def __init__(self, dir):
        self.extractor = yake.KeywordExtractor(lan="ru", n=1, dedupLim=0.3, top=5)
        
        data = open(os.path.join(dir, "AI_data", "data.txt"), 'r').readlines()
        data = pd.DataFrame(data)
        self.links = data[0].str.split("\t", n=2, expand=True)


        self.exc_link = "http://publication.pravo.gov.ru/document/{number_doc}"
        self.guids = open(os.path.join(dir, "AI_data", "guids.txt"), 'r').readlines()


    def get_keywords(self, text):
        return [word for word, _ in self.extractor.extract_keywords(text)]
            

    
    def get_files(self, text):
        try:
            for keyword in self.get_keywords(text):
                for guid in self.guids:
                    batch = self.get_batch_docs(guid, keyword[: -2])
                    if len(batch) != 0:
                        return "\n\n".join([doc['complexName'].replace('\n', '') + '\n' + self.exc_link.replace('{number_doc}', doc['eoNumber']) for doc in batch[:2]])

        except Exception as e:
            print("FileSearchEngine get_files", e)

        return None


    def get_batch_docs(self, guid, keyword):
        req = "http://publication.pravo.gov.ru/api/Documents?SignatoryAuthorityId={guid}&PageSize=10&SortedBy=4&NumberSearchType=3&Name={keyword}"
        req = req.replace('{keyword}', keyword).replace('{guid}', guid)
        docs = requests.get(req).json()
        docs = docs['items']
        return docs


    def get_links(self, text):
        try:
            data = self.links
            for keyword in self.get_keywords(text)[:1]:
                docs = data[data[2].str.contains(keyword[: -2])]
                if len(docs) != 0:
                    return "\n\n".join([doc[1] + '\n' + doc[2] for doc in docs[:2].itertuples()])

        except Exception as e:
            print("FileSearchEngine get_links", e)

        return None
