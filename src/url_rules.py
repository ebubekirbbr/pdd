
import sys
import json
import pprint
import pickle
import pygtrie
import requests

from traceback import format_exc
from word_with_nlp import nlp_class
from word_splitter_file import WordSplitterClass

from ns_log import NsLog


class url_rules:
    def __init__(self):

        print("initializing")

        self.logger = NsLog("log")
        self.path_data = "../data/"
        self.name_brand_file = "allbrand.txt"
        self.path_alexa_files = "../data/alexa-tld/"

        self.nlp_manager = nlp_class()
        self.pp = pprint.PrettyPrinter(indent=4)
        self.word_splitter = WordSplitterClass()

        allbrand_txt = open("{0}{1}".format(self.path_data, self.name_brand_file), "r")
        self.allbrand = self.__txt_to_list(allbrand_txt)

        #  trie
        #self.trie_alexa_tld = pygtrie.CharTrie(json.loads(open("constant/alexa_tld_json.txt", "r").read()))
        #self.trie_alexa_tldsiz = pygtrie.CharTrie(json.loads(open("constant/alexa_tldsiz_dct.json", "r").read()))


    def __txt_to_list(self, txt_object):

        list = []

        for line in txt_object:
            list.append(line.strip())

        txt_object.close()

        return list

    def rules_main(self, domain, tld, subdomain, path, words_raw):

        features = {}
        info_nlp = {}

        try:
            features.update(self.digit_count(domain, subdomain, path))             # digitcount
            features.update(self.length(domain, subdomain, path))                  # uzunluk
            features.update(self.tld_check(tld))                                   # tld check
            features.update(self.check_rule_5(words_raw))                          # www-com
            features.update(self.punny_code(domain))                               # punnycode
            features.update(self.random_domain(domain))                            # random_domain
            features.update(self.subdomain_count(subdomain))                       # subdomain count
            features.update(self.char_repeat(words_raw))                           # char_repeat
            features.update(self.alexa_check(domain, tld))                         # alexa1m  check
            #features.update(self.alexa_trie(domain, tld))                         # alexa1m check trie
            features.update(self.special_chars(domain, subdomain, path))           # - . / @
            features.update(self.check_domain_in_list(domain))
    
            result_nlp = self.nlp_features(words_raw)
            features.update(result_nlp['features'])                                # words_info
    
            info_nlp = result_nlp['info']
        
        except:
            self.logger.error("url_rules.main() Error : {0}".format(format_exc()))

        return info_nlp, features

    def digit_count(self, domain, subdomain, path):

        result = {'domain_digit_count': 0,
                  'subdomain_digit_count': 0,
                  'path_digit_count': 0}

        for letter in domain:
            if letter.isdigit():
                result['domain_digit_count'] = result['domain_digit_count'] + 1

        for letter in subdomain:
            if letter.isdigit():
                result['subdomain_digit_count'] = result['subdomain_digit_count'] + 1

        for letter in path:
            if letter.isdigit():
                result['path_digit_count'] = result['path_digit_count'] + 1

        return result

    def length(self, domain, subdomain, path):

        domain_uzunluk = len(domain)
        subdomain_uzunluk = len(subdomain)
        path_uzunluk = len(path)

        result = {}

        result['domain_length'] = domain_uzunluk
        result['subdomain_length'] = subdomain_uzunluk
        result['path_length'] = path_uzunluk

        return result

    def tld_check(self, tld):

        common_tld = ["com", "org", "net", "de", "edu", "gov"]

        result = {}

        if tld in common_tld:
            result["isKnownTld"] = 1
        else:
            result["isKnownTld"] = 0

        return result

    def check_rule_5(self, words_raw):

        result = {'www': 0, "com": 0}

        for word in words_raw:
            if not word.find('www') == -1:
                result['www'] = result['www'] + 1

            if not word.find('com') == -1:
                result['com'] = result['com'] + 1

        return result

    def punny_code(self, line):

        result = {}

        if line.startswith("xn--"):

            result['punnyCode'] = 1
            return result

        else:
            result['punnyCode'] = 0
            return result

    def random_domain(self, domain):

        result = {'random_domain': self.nlp_manager.check_word_random(domain)}

        return result

    def subdomain_count(self, line):

        sub = line.split(".")

        result = {}
        result['subDomainCount'] = len(sub)

        return result

    def __all_same(self, items):
        return all(x == items[0] for x in items)

    def char_repeat(self, words_raw):

        result = {'char_repeat': 0}
        repeat = {'2': 0, '3': 0, '4': 0, '5': 0}
        part = [2, 3, 4, 5]

        "sliding window mantigi repeat sayisi kadar eleman al" \
        "hepsi ayni mi diye bak - ayni ise artir"

        for word in words_raw:
            for char_repeat_count in part:
                for i in range(len(word) - char_repeat_count + 1):
                    sub_word = word[i:i + char_repeat_count]
                    if self.__all_same(sub_word):
                        repeat[str(char_repeat_count)] = repeat[str(char_repeat_count)] + 1

        result['char_repeat'] = sum(list(repeat.values()))

        return result

    def alexa_check(self, domain, tld):

        is_find_tld = 0
        is_find = 0
        line = domain+"."+tld

        letter = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                  "n", "o", "p", "r", "s", "t", "u", "v", "y", "z", "w", "x", "q",
                  "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

        try:
            if line[0] in letter:
                alexa_txt = open("{0}{1}.txt".format(self.path_alexa_files, line[0]), "r")
                alexaList_tld = []  #tldli
                alexa_list = []  #tldsiz

                for alexa_line in alexa_txt:
                    alexaList_tld.append(alexa_line.strip())
                    alexa_list.append(alexa_line.strip().split(".")[0])
                alexa_txt.close()

                for alexa_line in alexaList_tld:
                    if line.strip() == alexa_line.strip():
                        is_find_tld = 1
                        break

                for alexa_line in alexa_list:
                    line_domain = line.split(".")[0]
                    if line_domain.strip() == alexa_line.strip():
                        is_find = 1
                        break
        except:
            self.logger.debug(line + "işlenirken hata uzunluktan dolayı")
            self.logger.error("url_rules.check_rule_11()-Alexa  /  Error : {0}".format(format_exc()))

        result = {}

        if is_find_tld == 1:
            result['alexa1m_tld'] = 1
        else:
            result['alexa1m_tld'] = 0

        if is_find == 1:
            result['alexa1m'] = 1
        else:
            result['alexa1m'] = 0

        return result

    def alexa_trie(self, domain, tld):

        line = domain+"."+tld

        result = {}

        try:
            #if self.alexa1mm[line[0].lower()].has_key(line):
            if self.trie_alexa_tld.has_key(line):
                result['alexa1m_tld_trie'] = 1
            else:
                result['alexa1m_tld_trie'] = 0

            if self.trie_alexa_tldsiz.has_key(domain):
                result['alexa1m_tldsiz_trie'] = 1
            else:
                result['alexa1m_tldsiz_trie'] = 0
        except:
            self.logger.debug(line + "işlenirken alexa")
            self.logger.error("url_rules.check_rule_11()-Alexa  /  Error : {0}".format(format_exc()))

        return result

    def special_chars(self, domain, subdomain, path):

        special_char = {'-': 0, ".": 0, "/": 0, '@': 0, '?': 0, '&': 0, '=': 0, "_": 0}
        special_char_letter = special_char.keys()

        for l in domain:
            if l in special_char_letter:
                special_char[l] = special_char[l] + 1

        for l in subdomain:
            if l in special_char_letter:
                special_char[l] = special_char[l] + 1

        for l in path:
            if l in special_char_letter:
                special_char[l] = special_char[l] + 1

        return special_char

    def check_domain_in_list(self, domain):

        result = {}
        if domain in self.allbrand:
            result['domain_in_brand_list'] = 1
        else:
            result['domain_in_brand_list'] = 0

        return result

    def nlp_features(self, words_raw):

        """
        keywords_in_words, brands_in_words,
        dga_in_words, len_lt_7, len_gt_7 
        """
        grouped_words = self.nlp_manager.parse(words_raw)
        splitted_words = self.word_splitter.splitl(grouped_words['len_gt_7'])
        """
        found_keywords, found_brands,
        similar_to_keyword, similar_to_brand,
        other_words, target_words
        """

        fraud_analyze_result = self.nlp_manager.fraud_analysis(grouped_words, splitted_words)

        result = self.nlp_manager.evaluate(grouped_words, fraud_analyze_result, splitted_words)
        split = {'raw': grouped_words['len_gt_7'], 'splitted': splitted_words}
        result['info']['compoun_words'] = split

        return result
