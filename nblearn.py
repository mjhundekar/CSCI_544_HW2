import math
import random
import json
import re
import sys
# from decimal import *
# import PorterStemmer
import Stemmer_new
import collections

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

review = {}
sentiment_bool = {True: [], False: []}
trust_bool = {True: [], False: []}
sentiment = {}
trust = {}
cnt_all_words = {}
cnt_trust_true = {}
cnt_trust_false = {}
cnt_senti_true = {}
cnt_senti_false = {}
tf_idf_review = {}
final_words = set()

debug = open('debug.txt', 'w')
word_list = []
rand_keys = []
blob_list = {}
scores = {}
test_review = {}


def tf(word, blob, k):
    if k == 'positive':
        return cnt_senti_true[word] / (len(blob) * 1.0)
    elif k == 'negative':
        return cnt_senti_false[word] / (len(blob) * 1.0)
    elif k == 'deceptive':
        return cnt_trust_false[word] / (len(blob) * 1.0)
    elif k == 'truthful':
        return cnt_trust_true[word] / (len(blob) * 1.0)


def n_containing(word, bloblist):
    #    print 'n_containing ' + word
    #    print 'n_containing ' +str(sum(1 for blob in bloblist.values() if word in blob))
    cnt = 0
    for blob in bloblist.values():
        if word in blob:
            cnt += 1

    return cnt


def idf(word, bloblist):
    return math.log(len(bloblist) / (1.0 + n_containing(word, bloblist)))


# tfidf(word, review[key], review) for word in review[key]}
# tfidf(word, blob, blob_list)

def tfidf(word, blob, bloblist, k):
    return tf(word, blob, k) * idf(word, bloblist)


def split_test(a_size):
    global rand_keys
    global test_review
    global review
    f_test = open('test_data.txt', 'w')
    f_test_dgb = open('test_dbg.txt', 'w')
    rand_keys = random.sample(review, a_size)
    count = 1
    for key in rand_keys:
        test_review[key] = tokenize(review[key])
        if count < len(rand_keys):
            f_test.write(key + ' ' + review[key] + '\n')
            f_test_dgb.write(key + '\n')
        else:
            f_test.write(key + ' ' + review[key])
            f_test_dgb.write(key)
        # test_data[key] = a_dict[key]
        del review[key]
        count += 1

    f_test.close()


def tokenize(a_review):
    tmp0 = a_review.replace("'", "")
    tmp1 = re.sub(r'([a-zA-Z])([^\w\s]+)', r'\1 \2', tmp0)
    tmp2 = re.sub(r'([^\w\s]+)([a-zA-Z])', r'\1 \2', tmp1)
    tmp3 = re.sub(r'([a-zA-Z])([^a-zA-Z., ])', r'\1 \2', re.sub(r'([^a-zA-Z., ])([a-zA-Z])', r'\1 \2', tmp2))
    tmp4 = re.sub('[-!,.:]', ' ', re.sub('[^a-zA-Z0-9-!,.: ]', '', tmp3))
    tmp5 = re.sub('\s\s+', ' ', tmp4)
    lst_token = map(str.lower, tmp5.split(' '))
    #    item_list = [e for e in lst_token if e not in listOfStopWords]
    #    for token in item_list:
    #        if token in cnt_all_words:
    #            cnt_all_words[token] += 1
    #        else:
    #            cnt_all_words[token] = 1
    #    return item_list

    from Stemmer_new import Stemmer
    a_stemmer = Stemmer()
    stemmed_token = a_stemmer.stemWords(lst_token)
    item_list = [e for e in stemmed_token if e not in listOfStopWords]

    for token in item_list:
        if token in cnt_all_words:
            cnt_all_words[token] += 1
        else:
            cnt_all_words[token] = 1

    return item_list


def remove_final_words():
    keys = cnt_all_words.keys()
    for key in keys:
        if key not in final_words:
            del cnt_all_words[key]

    keys = cnt_trust_true.keys()
    for key in keys:
        if key not in final_words:
            del cnt_trust_true[key]

    keys = cnt_trust_false.keys()
    for key in keys:
        if key not in final_words:
            del cnt_trust_false[key]

    keys = cnt_senti_true.keys()
    for key in keys:
        if key not in final_words:
            del cnt_senti_true[key]

    keys = cnt_senti_false.keys()
    for key in keys:
        if key not in final_words:
            del cnt_senti_false[key]


def read_file(nm_train_text, nm_train_label):
    global review
    global scores
    global sentiment
    global trust
    global cnt_all_words
    global cnt_trust_true
    global cnt_trust_false
    global cnt_senti_true
    global cnt_senti_false
    global tf_idf_review
    global final_words

    f_test_labels = open('test_data_labels.txt', 'w')

    fl_train_label = open(nm_train_label, 'r')
    fl_train_text = open(nm_train_text, 'r')
    ln_train_text = fl_train_text.readlines()
    for line in ln_train_text:
        temp = line.strip().split(' ', 1)
        review[temp[0]] = temp[1].strip()
    # @to remove
    # split_test(int(len(ln_train_text)*0.25))
    # @to remove
    for key in review.keys():
        review[key] = tokenize(review[key])

    ln_train_label = fl_train_label.readlines()
    # train_label = {}
    # @to remove
    positive = open('positive.txt', 'w')
    negative = open('negative.txt', 'w')
    deceptive = open('deceptive.txt', 'w')
    truthful = open('truthful.txt', 'w')
    test_positive = open('test_positive.txt', 'w')
    test_negative = open('test_negative.txt', 'w')
    test_deceptive = open('test_deceptive.txt', 'w')
    test_truthful = open('test_truthful.txt', 'w')
    b_positive = set()
    b_negative = set()
    b_deceptive = set()
    b_truthful = set()
    # @to remove
    for line in ln_train_label:
        temp = line.strip('\n\r').split(' ')
        if temp[0] in review:
            if temp[1] == 'deceptive':
                trust[temp[0]] = False
                trust_bool[False].append(temp[0])
                for token in review[temp[0]]:
                    if token in cnt_trust_false:
                        cnt_trust_false[token] += 1
                    else:
                        cnt_trust_false[token] = 1

                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_deceptive |= set(review[temp[0]])
                deceptive.write(temp[0] + ' ' + tmp_str)

            elif temp[1] == 'truthful':
                trust[temp[0]] = True
                trust_bool[True].append(temp[0])
                for token in review[temp[0]]:
                    if token in cnt_trust_true:
                        cnt_trust_true[token] += 1
                    else:
                        cnt_trust_true[token] = 1

                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_truthful |= set(review[temp[0]])
                truthful.write(temp[0] + ' ' + tmp_str)

            if temp[2] == 'negative':
                sentiment[temp[0]] = False
                sentiment_bool[False].append(temp[0])
                for token in review[temp[0]]:
                    if token in cnt_senti_false:
                        cnt_senti_false[token] += 1
                    else:
                        cnt_senti_false[token] = 1

                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_negative |= set(review[temp[0]])
                negative.write(temp[0] + ' ' + tmp_str)

            elif temp[2] == 'positive':
                sentiment[temp[0]] = True
                sentiment_bool[True].append(temp[0])

                for token in review[temp[0]]:
                    if token in cnt_senti_true:
                        cnt_senti_true[token] += 1
                    else:
                        cnt_senti_true[token] = 1

                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_positive |= set(review[temp[0]])
                positive.write(temp[0] + ' ' + tmp_str)

        # @to remove
        # else:
        #     tmp_str = ' '.join(map(str, test_review[temp[0]])) + '\n'
        #     f_test_labels.write(line)
        #     if temp[1] == 'deceptive':
        #         test_deceptive.write(temp[0] + ' ' + tmp_str)
        #     elif temp[1] == 'truthful':
        #         test_truthful.write(temp[0] + ' ' + tmp_str)
        #     if temp[2] == 'negative':
        #         test_negative.write(temp[0] + ' ' + tmp_str)
        #     elif temp[2] == 'positive':
        #         test_positive.write(temp[0] + ' ' + tmp_str)


    blob_list['deceptive'] = list(b_deceptive)
    blob_list['truthful'] = list(b_truthful)
    blob_list['negative'] = list(b_negative)
    blob_list['positive'] = list(b_positive)

    for k, blob in blob_list.iteritems():
        scores = {word: tfidf(word, blob, blob_list, k) for word in blob}
        tf_idf_review[k] = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for word, score in tf_idf_review[k][:2000]:
            word_list.append(word)
        final_words = set(word_list)
    # remove_final_words()


def write_conditional(f, given, a_dict):
    total = float(sum(a_dict.values(), 0.0))
    debug.write('Total = ' + str(total) + '\n')
    alpha = len(cnt_all_words.keys())
    # cond_prob = {k: math.log10(v / total) for k, v in a_dict.iteritems()}
    # laplace smoothing
    cond_prob = {k: math.log10((v + 1.0) / (1.0 * (total + alpha))) for k, v in a_dict.iteritems()}
    # cond_prob = {k: math.log10((v) / (1.0 * (total))) for k, v in a_dict.iteritems()}
    # cond_prob = {k: ((v) / (total)) for k, v in a_dict.iteritems()}
    count = 1
    for key in cond_prob:
        cond_str = key + given + '= '
        if count < len(cond_prob.keys()):
            f.write(cond_str + str(cond_prob[key]) + '\n')
            debug.write(cond_str + str(cond_prob[key]) + '\n')
        else:
            f.write(cond_str + str(cond_prob[key]))
            debug.write(cond_str + str(cond_prob[key]))


def main():
    nm_train_text = sys.argv[1]
    nm_train_label = sys.argv[2]
    # nm_train_label = 'train-labels.txt'
    # nm_train_text = 'train-text.txt'


    read_file(nm_train_text, nm_train_label)

    model = open('nbmodel.txt', 'w')
    tot_review = len(review) * 1.0
    tot_senti_true = len(sentiment_bool[True]) * 1.0
    tot_trust_true = len(trust_bool[True]) * 1.0

    p_true = math.log10(tot_trust_true / (tot_review * 1.0))
    p_deceptive = math.log10(1 - p_true)
    p_positive = math.log10(tot_senti_true / (tot_review * 1.0))
    p_negative = math.log10(1 - p_positive)


    model.write('truthful= ' + str(p_true) + '\n')

    model.write('deceptive= ' + str(p_deceptive) + '\n')

    model.write('positive= ' + str(p_positive) + '\n')

    model.write('negative= ' + str(p_negative) + '\n')

    debug.write('Writing truthful\n')
    write_conditional(model, '|truthful', cnt_trust_true)
    debug.write('Writing deceptive\n')
    write_conditional(model, '|deceptive', cnt_trust_false)
    debug.write('Writing positive\n')
    write_conditional(model, '|positive', cnt_senti_true)
    debug.write('Writing negative\n')
    write_conditional(model, '|negative', cnt_senti_false)

    print '\ncnt_all_words', str(len(cnt_all_words.keys()))
    print '\nSum', str(sum(cnt_all_words.values()))

    print '\ncnt_senti_true', str(len(cnt_senti_true.keys()))
    print '\nSum', str(sum(cnt_senti_true.values()))

    print '\ncnt_senti_false', str(len(cnt_senti_false.keys()))
    print '\nSum', str(sum(cnt_senti_false.values()))

    print '\ncnt_trust_false', str(len(cnt_trust_false.keys()))
    print '\nSum', str(sum(cnt_trust_false.values()))

    print '\ncnt_trust_true', str(len(cnt_trust_true.keys()))
    print '\nSum', str(sum(cnt_trust_true.values()))


# python nblearn.py train-text.txt train-labels.txt
if __name__ == '__main__':
    #   python hw3cs561s16.py -i sample01.txt
    main()
