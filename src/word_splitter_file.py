
import re
import pprint
import enchant
from ns_log import NsLog


class WordSplitterClass(object):

    def __init__(self):
        self.logger = NsLog("log")
        self.path_data = "../data/"
        self.name_brand_file = "All_Brand.txt"
        self.dictionary_en = enchant.DictWithPWL("en_US", "{0}{1}".format(self.path_data, self.name_brand_file))
        #self.__file_capitalize(self.path_data, self.name_brand_file)

        self.pp = pprint.PrettyPrinter(indent=4)

    def _split(self, gt7_word_list):

        return_word_list = []

        for word in gt7_word_list:
            try:
                ss = {'raw': word,'splitted':[]}

                # kelime içerisinde rakam varsa temizlenir.
                word = re.sub("\d+", "", word)
                sub_words = []

                if not self.dictionary_en.check(word):
                    #  işlenen kelime sözlükte bu kelimeyi geri döndür. İşlenen kelime sözlükte yoksa ayırma işlemine geç.

                    for number in range(len(word), 3, -1): # uzunluğu 3 den yüksek olan alt kelimelerin üretilmesi
                        for l in range(0, len(word) - number + 1):
                            if self.dictionary_en.check(self.__capitalize(word[l:l + number])):

                                #  bir kelime tespit ettiğim zaman diğer kelimelerin tespit edilmesinde fp ye sebep olmasın diye
                                #  tespit edilen kelime yerine * karekteri koydum
                                w = self.__check_last_char(word[l:l + number])
                                sub_words.append(w)
                                word = word.replace(w, "*" * len(w))

                    rest = max(re.split("\*+", word), key=len)
                    if len(rest) > 3:
                        sub_words.append(rest)

                    split_w = sub_words

                    for l in split_w:
                        for w in reversed(split_w):

                            """
                            tespit edilen bir kelime daha büyük olan bir kelimenin içerisinde de geçiyorsa o fp dir.
                            Bunları temizledim. Örn.  secure, cure.
                            Cure kelimesi listeden çıkarılır.
                            """

                            if l != w:  # todo edit distance eklenecek
                                if l.find(w) != -1 or l.find(w.lower()) != -1:
                                    sub_words.remove(w)

                    if len(sub_words) == 0:
                        #  eğer hiç kelime bulunamadıysa ham kelime olduğu gibi geri döndürülür.
                        sub_words.append(word.lower())
                else:
                    sub_words.append(word.lower())

                ss['splitted']=sub_words
                return_word_list.append(ss)
            except:
                self.logger.debug("|"+word+"| işlenirken hata")
                self.logger.error("word_splitter.split()  muhtemelen boş dizi gelme hatası  /  Error : {0}".format(format_exc()))

        return return_word_list

    def _splitl(self, gt7_word_list):

        result = []

        for val in self._split(gt7_word_list):
            result += val["splitted"]

        return result

    def _splitw(self, word):

        word_l = []
        word_l.append(word)

        result = self._split(word_l)

        return result

    def __check_last_char(self, word):

        confusing_char = ['s', 'y']
        last_char = word[len(word)-1]
        word_except_last_char = word[0:len(word)-1]
        if last_char in confusing_char:
            if self.dictionary_en.check(word_except_last_char):
                return word_except_last_char

        return word

    def __clear_fp(self, sub_words):

        length_check = 0
        for w in sub_words:
            if (length_check + len(w)) < self.length+1:
                length_check = length_check + len(w)
            else:
                sub_words.remove(w)

        sub_words = self.__to_lower(sub_words)
        return sub_words

    def __to_lower(self, sub_words):

        lower_sub_list = []

        for w in sub_words:
            lower_sub_list.append(str(w.lower()))

        return lower_sub_list

    def __capitalize(self, word):
        return word[0].upper() + word[1:]

    def __file_capitalize(self, path, name):

        """
        enchant paketinde özel kelimelerin kontrol edilebilmesi için baş harfinin büyük olması gerekiyor.
        bir kelime kontrol edilmeden önce baş harfi büyük hale gitirilip sonra sözlüğe sorduruyorum.
        Bu nedenle dosyadaki kelimelerin de baş harflerini büyük hale getirip kaydettim ve bu şekilde kullandım.
        :return: 
        """

        personel_dict_txt = open("{0}{1}".format(path, name), "r")

        personel_dict = []

        for word in personel_dict_txt:
            personel_dict.append(self.__capitalize(word.strip()))

        personel_dict_txt.close()

        personel_dict_txt = open("{0}{1}-2".format(path, name), "w")

        for word in personel_dict:
            personel_dict_txt.write(word+"\n")
