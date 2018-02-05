
import json
from traceback import format_exc

import requests
import pprint
import datetime
from ns_log import NsLog

class active_rules:
    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=2)
        self.logger = NsLog("log")

    def goog_safe_browsing(self, domain_features):

        try:

            url_list = []
            updated_domain_features = domain_features
            for sample in domain_features:
                url_list.append(sample['info']['url'])

            sep_list = self.__seperate(url_list, 500)

            #phishing_url_list = self.get_urls(self.google_sb_query(list, sep_list.index(list), len(domain_features)))  # aktif

            phishing_url_list = self.get_urls(json.loads(open("constant/gb_phish.json", "r").read()))  #dosyadan

            updated_domain_features = []
            for each in domain_features:
                element = each
                if each['info']['url'] in phishing_url_list:
                    element.update({'active_features': {'google_safe_browsing': 1}})
                else:
                    element.update({'active_features': {'google_safe_browsing': 0}})

                updated_domain_features.append(element)
        except:
            self.logger.error("Error : {0}".format(format_exc()))

        return updated_domain_features

    def __seperate(self, url_list, size):

        sep_urls = []

        k = int((len(url_list)/size)+1)

        for i in range(1, k+1):
            if (i*size) > len(url_list):
                sep_urls.append(url_list[(i - 1) * size : len(url_list)])
            else:
                sep_urls.append(url_list[(i-1)*size: i*size])

        return sep_urls

    def google_sb_query(self, url_list, count, overall_count):

        query_url_list = self.sb_format(url_list)
        sep_list = self.__seperate(query_url_list, 500)

        for list in sep_list:
            time_now = str(datetime.datetime.now())[0:19].replace(" ", "_")

            api_key = 'AIzaSyCGmGpCMt-PNQTrWAsp3LqcM_UvCF6NJ1I'
            url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
            payload = {'client': {'clientId': "mycompany", 'clientVersion': "0.1"},
                       'threatInfo': {'threatTypes': ["SOCIAL_ENGINEERING", "MALWARE"],
                                      'platformTypes': ["ANY_PLATFORM"],
                                      'threatEntryTypes': ["URL"],
                                      'threatEntries': list
                                      }}
            params = {'key': api_key}
            r = requests.post(url, params=params, json=payload).json()

            phish_url_list = []
            if 'matches' in r.keys():
                for each in r['matches']:
                    phish_url_list.append(each['threat']['url'])
            elif 'error' in r.keys():
                self.logger.debug("Google-SB sorgusunda hata - Toplam işlenen örnek sayısı: "+overall_count+"\nişlenen parça (500): "+count)

        return phish_url_list

    def sb_format(self, url_list):

        sb_query = []
        for url in url_list:
            sb_query.append({'url': url})

        return sb_query

    def get_urls(self, ph_db_json):

        urls = []

        for obj in ph_db_json:
            urls.append(obj['url'])

        return urls

    def txt_to_list(self, txt_object):
        list = []

        for line in txt_object:
            list.append(line.strip())
        txt_object.close()
        return list
