
import pprint

from traceback import format_exc
from ns_log import NsLog

pp = pprint.PrettyPrinter(indent=4)

class json2arff:
    def __init__(self):
        self.logger = NsLog("log")

    def convert_for_train(self, features, param):

        # arff convert header
        try:
            ArffStr = '''@relation weka-test\n\n'''

            features_keys_url = list(features[0]['url_features'].keys())
            features_keys_active = []

            if param == '-a':
                features_keys_active = list(features[0]['active_features'].keys())

            for line in features_keys_url:
                ArffStr = ArffStr + '@attribute ' + line + " numeric\n"

            if param == '-a':
                for line in features_keys_active:
                    ArffStr = ArffStr + '@attribute ' + line + " numeric\n"

            ArffStr = ArffStr + '@attribute class {phish, legitimate}' + "\n\n@data\n"
        except:
            self.logger.debug("Hata - Json_to_arff e gelen sample sayısı"+str(len(features))+
                              "\nurl_feature_keys: "+str(features_keys_url)+
                              "\nactive_features_key: "+str(features_keys_active))
            self.logger.error("Error Arff Header : {0}".format(format_exc()))
        # header son


        for each_domain in features:
            try:
                tmp = ""

                for key in features_keys_url:
                    tmp = tmp + str(each_domain['url_features'][key])+","

                if param == '-a':
                    for key_a in features_keys_active:
                        tmp = tmp + str(each_domain['active_features'][key_a]) + ","

                tmp = tmp + each_domain['info']['class']+"\n"
                ArffStr = ArffStr + tmp
            except:
                self.logger.debug("Arffe çevrilen sample da hata :\n" + str(each_domain))
                self.logger.error("Error Arff Body : {0}".format(format_exc()))

        return ArffStr

    def convert_for_test(self, features, param):

        #todo active rules a göre güncellenecek

        # arff convert header

        ArffStr = '''@relation weka-test\n\n'''

        features_keys_url = features[0]['url_features'].keys()

        if param == '-dns':
            features_keys_dns = features[0]['dns_features'].keys()

        for line in features_keys_url:
            ArffStr = ArffStr + '@attribute ' + line + " numeric\n"

        if param == '-dns':
            for key in features_keys_dns:
              ArffStr = ArffStr + '@attribute ' + key + " numeric\n"

        ArffStr = ArffStr + "\n@data\n"

        # header son

        for each_domain in features:
            tmp = ""

            for key in features_keys_url:
                tmp = tmp + str(each_domain['url_features'][key])+","

            if param == '-dns':
                for key_dns in features_keys_dns:
                    tmp = tmp + str(each_domain['dns_features'][key_dns]) + ","

            tmp = tmp[0:len(tmp)-1] +"\n"
            ArffStr = ArffStr + tmp

        return ArffStr

    def convert_for_NLP_without_features(self, features):
        # arff convert header
        try:
            ArffStr = '''@relation weka-test\n\n'''

            ArffStr += '@attribute words string\n'

            ArffStr += '@attribute class {phish, legitimate}' + "\n\n@data\n"


            for sample in features:
                ArffStr += "'"
                for word in sample['info']['nlp_info']['words_nlp']:
                    ArffStr += word+" "
                ArffStr = ArffStr.strip() + "',{0}\n".format(sample['info']['class'])

        except:
            self.logger.error("Error Arff Header : {0}".format(format_exc()))

        return ArffStr

    def convert_for_NLP_with_features(self, features):
        # arff convert header
        try:
            features_keys_url = list(features[0]['url_features'].keys())

            ArffStr = '''@relation weka-test\n\n'''

            ArffStr += '@attribute words string\n'

            for line in features_keys_url:
                ArffStr = ArffStr + '@attribute ' + line + " numeric\n"

            ArffStr += '@attribute class {phish, legitimate}' + "\n\n@data\n"

            for sample in features:
                ArffStr += '"'
                for word in sample['info']['nlp_info']['words_nlp']:
                    ArffStr += word+" "

                ArffStr = ArffStr.strip()+ '",'

                for key in features_keys_url:
                    ArffStr += str(sample['url_features'][key]) + ","
                ArffStr = ArffStr.strip() + '{0}\n'.format(sample['info']['class'])

        except:
            self.logger.error("Error Arff Header : {0}".format(format_exc()))

        return ArffStr




