


import re
import sys
import pickle
import numpy as np
import editdistance
import gib_detect_train

from traceback import format_exc

from ns_log import NsLog


class nlp_class:

    def __init__(self):
        self.logger = NsLog("log")
        self.path_data = "../data/"
        self.name_keywords = "keywords.txt"
        self.name_brand_file = "allbrand.txt"
        self.name_random_model = "gib_model.pki"

        model_data = pickle.load(open(self.name_random_model, 'rb'))
        self.model_mat = model_data['mat']
        self.threshold = model_data['thresh']

        self.allbrand = self.__txt_to_list(open("{0}{1}".format(self.path_data, self.name_brand_file), "r"))
        self.keywords = self.__txt_to_list(open("{0}{1}".format(self.path_data, self.name_keywords), "r"))


    def __txt_to_list(self, txt_object):
        list = []

        for line in txt_object:
            list.append(line.strip())
        txt_object.close()
        return list

    def __is_similar_to_any_element(self, word, list):

        target = ''
        for l in list:
            if editdistance.eval(word, l) < 2:
                target = l

        if len(target) > 0:
            return word
        else:
            return 0

    def parse(self, words):

        keywords_in_words = []
        brands_in_words = []
        similar_to_brands = []
        similar_to_keywords = []
        dga_in_words = []
        len_gt_7 = []
        len_lt_7 = []
        try:
            for word in words:

                word = re.sub("\d+", "", word)

                if word in self.keywords:
                    keywords_in_words.append(word)

                elif word in self.allbrand:
                    brands_in_words.append(word)

                elif self.__is_similar_to_any_element(word, self.allbrand) != 0:
                    target = self.__is_similar_to_any_element(word, self.allbrand)
                    similar_to_brands.append(target)

                elif self.__is_similar_to_any_element(word, self.keywords) != 0:
                    target = self.__is_similar_to_any_element(word, self.keywords)
                    similar_to_keywords.append(target)

                elif len(word) > 3 and not word.isnumeric():

                    if (gib_detect_train.avg_transition_prob(word, self.model_mat) > self.threshold) == False:
                        dga_in_words.append(word)
                        # todo keyword benzeri olanlar temizlenmeli
                    elif len(word) < 7:
                        len_lt_7.append(word)
                    else:
                        len_gt_7.append(word)

            result = {'keywords_in_words': keywords_in_words, 'brands_in_words': brands_in_words,
                      'dga_in_words': dga_in_words, 'len_lt_7': len_lt_7, 'len_gt_7': len_gt_7,
                      'similar_to_brands': similar_to_brands, 'similar_to_keywords': similar_to_keywords}
        except:
            self.logger.debug(str(words) + " işlenirken hata")
            self.logger.error("Error : {0}".format(format_exc()))

        return result

    def fraud_analysis(self, grouped_words, splitted_words):

        word_list = grouped_words['len_lt_7'] + grouped_words['similar_to_brands'] + grouped_words[
            'similar_to_keywords'] + splitted_words

        word_list_nlp = grouped_words['len_lt_7'] + grouped_words['similar_to_brands'] + \
                        grouped_words['similar_to_keywords'] + grouped_words['brands_in_words'] + \
                        grouped_words['keywords_in_words'] + grouped_words['dga_in_words'] + splitted_words

        found_keywords = []
        found_brands = []
        similar_to_keyword = []
        similar_to_brand = []
        other_words = []
        target_words = {'brand': [], 'keyword': []}
        try:
            for word in word_list:

                word = re.sub("\d+", "", word)

                if word in self.keywords:
                    found_keywords.append(word)
                elif word in self.allbrand:
                    found_brands.append(word)
                else:

                    for brand in self.allbrand:
                        if editdistance.eval(word, brand) < 2:
                            target_words['brand'].append(brand)
                            similar_to_brand.append(word)

                    for keyword in self.keywords:
                        if editdistance.eval(word, keyword) < 2:
                            target_words['keyword'].append(keyword)
                            similar_to_keyword.append(word)

                if word not in found_keywords+found_brands+similar_to_keyword+similar_to_brand:
                    other_words.append(word)

            result = {'found_keywords': found_keywords,
                      'found_brands': found_brands,
                      'similar_to_keywords': similar_to_keyword,
                      'similar_to_brands': similar_to_brand,
                      'other_words': other_words,
                      'target_words': target_words,
                      'words_nlp': word_list_nlp}
        except:
            self.logger.debug(str(word_list)+" işlenirken hata")
            self.logger.error("Error : {0}".format(format_exc()))
        return result

    def evaluate(self, grouped_words, fraud_analyze_result, splitted_words):

        """
        grouped_words
        keywords_in_words, brands_in_words,
        dga_in_words, len_lt_7, len_gt_7 

        fraud_anaylze_result
        found_keywords, found_brands,
        similar_to_keyword, similar_to_brand,
        other_words, target_words 
        """
        try:
            words_raw = grouped_words['keywords_in_words'] + grouped_words['brands_in_words'] + \
                        grouped_words['similar_to_brands'] + grouped_words['similar_to_keywords'] + \
                        grouped_words['dga_in_words'] + grouped_words['len_lt_7'] + grouped_words['len_gt_7']

            words_len = []
            compound_word_len = []

            for word in words_raw:
                words_len.append(len(word))

            for word in grouped_words['len_gt_7']:
                compound_word_len.append(len(word))

            all_keywords = grouped_words['keywords_in_words'] + fraud_analyze_result['found_keywords']
            all_brands = grouped_words['brands_in_words'] + fraud_analyze_result['found_brands']
            similar_brands = fraud_analyze_result['similar_to_brands']
            similar_keywords = fraud_analyze_result['similar_to_keywords']

            if len(compound_word_len) == 0:
                av_com = 0
            else:
                av_com = float(np.average(compound_word_len))

            if len(words_len) == 0:
                min = 0
                max = 0
                av_w = 0
                std = 0
            else:
                min = int(np.min(words_len))
                max = int(np.max(words_len))
                av_w = float(np.average(words_len))
                std = float(np.std(words_len))

            result = {'info': {'keywords': all_keywords,
                               'brands': all_brands,
                               'dga_in_words': grouped_words['dga_in_words'],
                               'similar_to_keywords': similar_keywords,
                               'similar_to_brands': similar_brands,
                               'negligible_words': fraud_analyze_result['other_words'],
                               'target_words': fraud_analyze_result['target_words'],
                               'words_nlp': fraud_analyze_result['words_nlp']
                               },
                      'features': {'raw_word_count': len(words_len),
                                   'splitted_word_count': len(splitted_words),
                                   'average_word_length': av_w,
                                   'longest_word_length': max,
                                   'shortest_word_length': min,
                                   'std_word_length': std,
                                   'compound_word_count': len(grouped_words['len_gt_7']),
                                   'keyword_count': len(all_keywords),
                                   'brand_name_count': len(all_brands),
                                   'negligible_word_count': len(fraud_analyze_result['other_words']),
                                   'target_brand_count': len(fraud_analyze_result['target_words']['brand']),
                                   'target_keyword_count': len(fraud_analyze_result['target_words']['keyword']),
                                   'similar_keyword_count': len(similar_keywords),
                                   'similar_brand_count': len(similar_brands),
                                   'average_compound_words': av_com,
                                   'random_words': len(grouped_words['dga_in_words'])
                                   }}
        except:
            self.logger.error("Error : {0}".format(format_exc()))
        return result

    def check_word_random(self, word):

        if gib_detect_train.avg_transition_prob(word, self.model_mat) < self.threshold:
            return 1
        else:
            return 0


