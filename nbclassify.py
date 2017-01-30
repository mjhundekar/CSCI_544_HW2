import re
import json
import sys
import math
import collections

# from decimal import *
prior = {}
cond_truthful = {}
cond_deceptive = {}
cond_positive = {}
cond_negative = {}
# cond_all = {}
test_cnt_all_words = {}
test_review = {}

true_trust = {}
true_senti = {}
pred_trust = {}
pred_senti = {}
precision = {'deceptive': 0, 'truthful': 0, 'positive': 0, 'negative': 0}
recall = {'deceptive': 0, 'truthful': 0, 'positive': 0, 'negative': 0}
f1 = {'deceptive': 0, 'truthful': 0, 'positive': 0, 'negative': 0}
dbg = open('debug_classify.txt', 'w')
metrics = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}

listOfStopWords = ["", "-", "!", ",", ".", ":",
                   "a", "able", "about", "all", "also", "am", "an", "and", "any", "as", "are", "at",
                   "be", "but", "by",
                   "can",
                   "did", "do"
                          "etc",
                   "find", "for", "from",
                   "get", "go",
                   "have", "had", "he", "her", "him", "how,"
                                                      "i", "if", "in", "is", "it", "its",
                   "me", "my",
                   "of", "on", "or", "our",
                   "so",
                   "than", "that", "the", "their", "there", "these", "they", "things", "this", "to", "too",
                   "you", "youll", "your",
                   "us", "up",
                   "was", "want", "we", "were", "what", "when", "where", "which", "whom", "why", "will", "with", "who"]


# true_deceptive = {}
# true_truthful = {}
# true_positive = {}
# true_negative = {}
#
# pred_deceptive = {}
# pred_truthful = {}
# pred_positive = {}
# pred_negative = {}


# def read_test_remove(fname):
#     global test_review
#     test_review = json.load(open(fname))
#     for key in test_review.keys():
#         test_review[key] = tokenize(test_review[key])



def tokenize(a_review):
    tmp0 = a_review.replace("'", "")
    tmp = re.sub('[-!,.:]', ' ', re.sub('[^a-zA-Z0-9-!,.: ]', '', tmp0))
    tmp1 = re.sub(r'([a-zA-Z])([^\w\s]+)', r'\1 \2', tmp)
    tmp2 = re.sub(r'([^\w\s]+)([a-zA-Z])', r'\1 \2', tmp1)
    tmp3 = re.sub('\s\s+', ' ', tmp2)
    lst_token = map(str.lower, tmp3.split(' '))
    item_list = [e for e in lst_token if e not in listOfStopWords]
    from Stemmer_new import Stemmer
    a_stemmer = Stemmer()
    stemmed_token = a_stemmer.stemWords(item_list)
    count_words(stemmed_token, test_cnt_all_words)
    # count_words(lst_token, test_cnt_all_words)
    # review_dict = collections.OrderedDict()
    # for token in lst_token:
    #     if token in review_dict:
    #         review_dict[token] += 1
    #     else:
    #         review_dict[token] = 1
    # return review_dict
    return stemmed_token


def count_words(text, a_dict):
    for token in text:
        if token in a_dict:
            a_dict[token] += 1
        else:
            a_dict[token] = 1


def read_test(nm_test_text):
    global test_review
    fl_test_text = open(nm_test_text, 'r')
    ln_test_text = fl_test_text.readlines()
    #        test_text = {}
    for line in ln_test_text:
        temp = line.strip().split(' ', 1)
        test_review[temp[0]] = tokenize(temp[1].strip())
        # review[temp[0]] = temp[1].strip()


def read_model():
    f = open('nbmodel.txt', 'r')
    lines = f.readlines()
    count = 1
    for line in lines:
        curr = line.strip().split(' ')
        if count == 1:
            prior['truthful'] = float(curr[1])
            count += 1
            continue
        if count == 2:
            prior['deceptive'] = float(curr[1])
            count += 1
            continue
        if count == 3:
            prior['positive'] = float(curr[1])
            count += 1
            continue
        if count == 4:
            prior['negative'] = float(curr[1])
            count += 1
            continue
        if count > 4:
            curr_cond = curr[0].split('|')
            key = curr_cond[0]
            which_dict = curr_cond[1][:-1]

            if which_dict == 'truthful':
                cond_truthful[key] = float(curr[1])
                continue
            if which_dict == 'deceptive':
                cond_deceptive[key] = float(curr[1])
                continue
            if which_dict == 'positive':
                cond_positive[key] = float(curr[1])
                continue
            if which_dict == 'negative':
                cond_negative[key] = float(curr[1])
                continue


def compute_probability(a_id, a_review, a_class_dict):
    prob = float(0.0)
    # prob = 1.0
    # a_review_dict = test_review[a_id]
    # dbg.write(str(a_review_dict) + '\n')
    for key in a_review:
        # cnt_key = int(a_review[key])
        if key in a_class_dict:
            prob += float(a_class_dict[key])
            # dbg.write(a_id + ' ' + key + ' ' + str(cnt_key) + ' ' + str(a_class_dict[key]) + '\n')
            dbg.write(a_id + ' ' + key + ' ' + str(a_class_dict[key]) + '\n')
            # prob *= (math.pow(int(a_class_dict[key]), cnt_key))
            # print a_class_dict[key]
        else:
            dbg.write('NOT FOUND ' + key + '\n')
    return prob


def classify_sentiment(a_id, a_review):
    # positive
    prior_positive = prior['positive']
    rev_cond_positive = compute_probability(a_id, a_review, cond_positive)
    positive_score = prior_positive + rev_cond_positive
    dbg.write('Final POSITIVE PROB = ' + str(positive_score) + '\n')
    # positive_score = prior_positive * rev_cond_positive
    # negative
    prior_negative = prior['negative']
    rev_cond_negative = compute_probability(a_id, a_review, cond_negative)
    negative_score = prior_negative + rev_cond_negative
    dbg.write('Final NEGATIVE PROB = ' + str(negative_score) + '\n')
    # negative_score = prior_negative * rev_cond_negative
    if positive_score >= negative_score:
        return 'positive'
    else:
        return 'negative'
        # return ''


def classify_trust(a_id, a_review):
    # truthful
    prior_truthful = prior['truthful']
    rev_cond_truthful = compute_probability(a_id, a_review, cond_truthful)
    truthful_score = prior_truthful + rev_cond_truthful
    dbg.write('Final TRUTHFUL PROB = ' + str(truthful_score) + '\n')
    # truthful_score = prior_truthful * rev_cond_truthful
    # deceptive
    prior_deceptive = prior['deceptive']
    rev_cond_deceptive = compute_probability(a_id, a_review, cond_deceptive)
    deceptive_score = prior_deceptive + rev_cond_deceptive
    dbg.write('Final DECEPTIVE PROB = ' + str(deceptive_score) + '\n')
    # deceptive_score = prior_deceptive * rev_cond_deceptive
    if truthful_score >= deceptive_score:
        return 'truthful'
    else:
        return 'deceptive'
        # return ''


def read_output_labels():
    op_labels = open('test_data_labels.txt', 'r')
    ln_op_labels = op_labels.readlines()
    for line in ln_op_labels:
        temp = line.strip('\n\r').split(' ')
        if temp[1] == 'deceptive':
            true_trust[temp[0]] = False
            # trust_bool[False].append(temp[0])
            # count_words(review[temp[0]], cnt_trust_false)
        else:
            true_trust[temp[0]] = True
            # trust_bool[True].append(temp[0])
            # count_words(review[temp[0]], cnt_trust_true)

        if temp[2] == 'negative':
            true_senti[temp[0]] = False
            # sentiment_bool[False].append(temp[0])
            # count_words(review[temp[0]], cnt_senti_false)
        else:
            true_senti[temp[0]] = True
            # sentiment_bool[True].append(temp[0])
            # count_words(review[temp[0]], cnt_senti_true)


def compute_metric():
    m_deceptive = {'TP': 0.0, 'TN': 0.0, 'FP': 0.0, 'FN': 0.0}
    m_truthful = {'TP': 0.0, 'TN': 0.0, 'FP': 0.0, 'FN': 0.0}
    m_negative = {'TP': 0.0, 'TN': 0.0, 'FP': 0.0, 'FN': 0.0}
    m_positive = {'TP': 0.0, 'TN': 0.0, 'FP': 0.0, 'FN': 0.0}

    for key in test_review.keys():
        # compute for deceptive
        if true_trust[key] == pred_trust[key]:
            if pred_trust[key] is False:
                m_deceptive['TP'] += 1
                m_truthful['TN'] += 1
            else:
                m_deceptive['TN'] += 1
                m_truthful['TP'] += 1
        elif true_trust[key] is True and pred_trust[key] is False:
            m_deceptive['FN'] += 1
            m_truthful['FN'] += 1
        else: # true_trust[key] is False and pred_trust[key] is True:
            m_deceptive['FP'] += 1
            m_truthful['FP'] += 1


        if true_senti[key] == pred_senti[key]:
            if pred_senti[key] is False:
                m_negative['TP'] += 1
                m_positive['TN'] += 1
            else:
                m_negative['TN'] += 1
                m_positive['TP'] += 1
        elif true_senti[key] is True and pred_senti[key] is False:
            m_negative['FN'] += 1
            m_positive['FN'] += 1
        else: # true_senti[key] is False and pred_senti[key] is True:
            m_negative['FP'] += 1
            m_positive['FP'] += 1
    # precision = {'deceptive': 0, 'truthful': 0, 'positive': 0, 'negative': 0}
    precision['deceptive'] = m_deceptive['TP']/(m_deceptive['TP'] + m_deceptive['FP'])
    precision['truthful'] = m_truthful['TP'] / (m_truthful['TP'] + m_truthful['FP'])
    precision['positive'] = m_positive['TP'] / (m_positive['TP'] + m_positive['FP'])
    precision['negative'] = m_negative['TP'] / (m_negative['TP'] + m_negative['FP'])

    recall['deceptive'] = m_deceptive['TP'] / (m_deceptive['TP'] + m_deceptive['FN'])
    recall['truthful'] = m_truthful['TP'] / (m_truthful['TP'] + m_truthful['FN'])
    recall['positive'] = m_positive['TP'] / (m_positive['TP'] + m_positive['FN'])
    recall['negative'] = m_negative['TP'] / (m_negative['TP'] + m_negative['FN'])

    f1['deceptive'] = 2 * m_deceptive['TP'] / ((2 * m_deceptive['TP']) + m_deceptive['FP'] + m_deceptive['FN'])
    f1['truthful'] = 2 * m_truthful['TP'] / ((2 * m_truthful['TP']) + m_truthful['FP'] + m_deceptive['FN'])
    f1['positive'] = 2 * m_positive['TP'] / ((2 * m_positive['TP']) + m_positive['FP'] + m_deceptive['FN'])
    f1['negative'] = 2 * m_negative['TP'] / ((2 * m_negative['TP']) + m_negative['FP'] + m_deceptive['FN'])

    print '\n\nPRECISION'
    print precision
    print '\n\nRECALL'
    print recall
    print '\n\nF1'
    print f1

def main():
    nm_test_text = sys.argv[1]
    # nm_test_text = 'test_data.txt'
    global test_review

    read_model()
    read_test(nm_test_text)
    # read_output_labels()
    # read_test_remove(nm_test_text)
    nboutput = open('nboutput.txt', 'w')
    cnt = 1
    for key in test_review.keys():
        dbg.write('TRUST\n')
        str_trust = classify_trust(key, test_review[key])
        dbg.write('SENTI\n')
        str_sentiment = classify_sentiment(key, test_review[key])

        if str_trust == 'deceptive':
            pred_trust[key] = False
        else:
            pred_trust[key] = True

        if str_sentiment == 'negative':
            pred_senti[key] = False
        else:
            pred_senti[key] = True
        if cnt < len(test_review.keys()):
            nboutput.write(key + ' ' + str_trust + ' ' + str_sentiment + '\n')
        else:
            nboutput.write(key + ' ' + str_trust + ' ' + str_sentiment)
        cnt += 1
    nboutput.close()
    # compute_metric()


# python nbclassify.py test_data.txt
if __name__ == '__main__':
    main()
