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
                   "have", "had", "he", "her", "him", "how",
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
    # tmp0 = a_review.replace("'", "")
    # tmp1 = re.sub(r'([a-zA-Z])([^\w\s]+)', r'\1 \2', tmp0)
    # tmp2 = re.sub(r'([^\w\s]+)([a-zA-Z])', r'\1 \2', tmp1)
    # tmp3 = re.sub(r'([a-zA-Z])([^a-zA-Z., ])', r'\1 \2', re.sub(r'([^a-zA-Z., ])([a-zA-Z])', r'\1 \2', tmp2))
    # tmp4 = re.sub('[-!,.:]', ' ', re.sub('[^a-zA-Z0-9-!,.: ]', '', tmp3))
    # tmp5 = re.sub('\s\s+', ' ', tmp4)
    # lst_token = map(str.lower, tmp5.split(' '))

    # tmp0 = a_review.replace("'", "")
    tmp = re.sub('[-!,.:]', ' ', re.sub('[^a-zA-Z0-9-!,.: ]', '', a_review))
    tmp1 = re.sub(r'([a-zA-Z])([^a-zA-Z., ])', r'\1 \2', re.sub(r'([^a-zA-Z., ])([a-zA-Z])', r'\1 \2', tmp))
    tmp2 = re.sub(r'([a-zA-Z])([^\w\s]+)', r'\1 \2', tmp1)
    tmp3 = re.sub(r'([^\w\s]+)([a-zA-Z])', r'\1 \2', tmp2)
    tmp4 = re.sub('\s\s+', ' ', tmp3)
    lst_token = map(str.lower, tmp4.split(' '))

    # lst_token = re.sub('[-!,.:]', ' ', re.sub('[^a-zA-Z0-9-!,.: ]', '', a_review)).split(' ')

    # item_list = [e for e in lst_token if e not in listOfStopWords]
    # for token in item_list:
    #     if token in test_cnt_all_words:
    #         test_cnt_all_words[token] += 1.0
    #     else:
    #         test_cnt_all_words[token] = 1.0
    # return item_list

    from Stemmer_new import Stemmer
    a_stemmer = Stemmer()
    stemmed_token = a_stemmer.stemWords(lst_token)
    item_list = [e for e in stemmed_token if e not in listOfStopWords]

    for token in item_list:
        if token in test_cnt_all_words:
            test_cnt_all_words[token] += 1
        else:
            test_cnt_all_words[token] = 1

    return item_list


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
            prior['truthful'] = float(curr[1].strip()) * 1.0
            count += 1
            continue
        if count == 2:
            prior['deceptive'] = float(curr[1].strip()) * 1.0
            count += 1
            continue
        if count == 3:
            prior['positive'] = float(curr[1].strip()) * 1.0
            count += 1
            continue
        if count == 4:
            prior['negative'] = float(curr[1].strip()) * 1.0
            count += 1
            continue
        if count > 4:
            count += 1
            curr_cond = curr[0].split('|')
            key = curr_cond[0].strip()
            which_dict = curr_cond[1][:-1].strip()
            # print which_dict
            if which_dict == 'truthful':
                cond_truthful[key] = float(curr[1].strip()) * 1.0
                # print which_dict
                continue
            if which_dict == 'deceptive':
                cond_deceptive[key] = float(curr[1].strip()) * 1.0
                # print which_dict
                continue
            if which_dict == 'positive':
                cond_positive[key] = float(curr[1].strip()) * 1.0
                # print which_dict
                continue
            if which_dict == 'negative':
                cond_negative[key] = float(curr[1].strip()) * 1.0
                # print which_dict
                continue

    print 'TOTAL LINES READ :: ' + str(count) + '\n'


def compute_probability(a_id, a_review, which_dict):
    prob = float(0.0)
    # prob = 1.0
    a_class_dict = {}

    # a_review_dict = test_review[a_id]
    # dbg.write(str(a_review_dict) + '\n')
    if which_dict == 'truthful':
        a_class_dict = cond_truthful
    elif which_dict == 'deceptive':
        a_class_dict = cond_deceptive
    elif which_dict == 'positive':
        a_class_dict = cond_positive
    elif which_dict == 'negative':
        a_class_dict = cond_negative

    for key in a_review:
        # cnt_key = int(a_review[key])
        if key in a_class_dict:
            temp = a_class_dict[key]
            prob += (a_class_dict[key] * 1.0)
            # prob *= (a_class_dict[key] * 1.0)
            # dbg.write(a_id + ' ' + key + ' ' + str(cnt_key) + ' ' + str(a_class_dict[key]) + '\n')
            dbg.write(a_id + ' ' + which_dict + ' ' + key + ' ' + str(a_class_dict[key]) + '\n')
            # prob *= (math.pow(int(a_class_dict[key]), cnt_key))
            # print a_class_dict[key]
        else:
            dbg.write('NOT FOUND ' + key + '\n')
    return prob


def classify_sentiment(a_id, a_review):
    # positive
    prior_positive = prior['positive']
    rev_cond_positive = compute_probability(a_id, a_review, 'positive')
    # positive_score = prior_positive * rev_cond_positive
    positive_score = prior_positive + rev_cond_positive
    dbg.write('Final POSITIVE PROB = ' + str(positive_score) + '\n')

    # negative
    prior_negative = prior['negative']
    rev_cond_negative = compute_probability(a_id, a_review, 'negative')
    # negative_score = prior_negative * rev_cond_negative
    negative_score = prior_negative + rev_cond_negative
    dbg.write('Final NEGATIVE PROB = ' + str(negative_score) + '\n')

    if positive_score > negative_score:
        return 'positive'
    else:
        return 'negative'
        # return ''


def classify_trust(a_id, a_review):
    # truthful
    prior_truthful = prior['truthful']
    rev_cond_truthful = compute_probability(a_id, a_review, 'truthful')
    # truthful_score = prior_truthful * rev_cond_truthful
    truthful_score = prior_truthful + rev_cond_truthful
    dbg.write('Final TRUTHFUL PROB = ' + str(truthful_score) + '\n')

    # deceptive
    prior_deceptive = prior['deceptive']
    rev_cond_deceptive = compute_probability(a_id, a_review, 'deceptive')
    # deceptive_score = prior_deceptive * rev_cond_deceptive
    deceptive_score = prior_deceptive + rev_cond_deceptive
    dbg.write('Final DECEPTIVE PROB = ' + str(deceptive_score) + '\n')

    if truthful_score > deceptive_score:
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
        else:  # true_trust[key] is False and pred_trust[key] is True:
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
        else:  # true_senti[key] is False and pred_senti[key] is True:
            m_negative['FP'] += 1
            m_positive['FP'] += 1
    # precision = {'deceptive': 0, 'truthful': 0, 'positive': 0, 'negative': 0}
    precision['deceptive'] = m_deceptive['TP'] / (m_deceptive['TP'] + m_deceptive['FP'])
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
            nboutput.write('%s %s %s\n' % (key, str_trust, str_sentiment))
            # nboutput.write(key + ' ' + str_trust + ' ' + str_sentiment + '\n')
        else:
            nboutput.write('%s %s %s' % (key, str_trust, str_sentiment))
        cnt += 1
    nboutput.close()
    # compute_metric()


# python nbclassify.py test_data.txt
if __name__ == '__main__':
    main()
