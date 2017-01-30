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
                   "have", "had", "he", "her", "him", "how,"
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

debug = open('debug.txt', 'w')

rand_keys = []
blob_list = {}
scores = {}


def tf(word, blob, k):
    if k == 'positive':
        return cnt_senti_true[word] / len(blob)
    elif k == 'negative':
        return cnt_senti_false[word] / len(blob)
    elif k == 'deceptive':
        return cnt_trust_false[word] / len(blob)
    elif k == 'truthful':
        return cnt_trust_true[word] / len(blob)


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


def split_test(a_dict, a_size):
    global rand_keys
    f_test = open('test_data.txt', 'w')
    f_test_dgb = open('test_dbg.txt', 'w')
    rand_keys = random.sample(a_dict, a_size)
    count = 1
    for key in rand_keys:

        if count < len(rand_keys):
            f_test.write(key + ' ' + a_dict[key] + '\n')
            f_test_dgb.write(key + '\n')
        else:
            f_test.write(key + ' ' + a_dict[key])
            f_test_dgb.write(key)
        # test_data[key] = a_dict[key]
        del a_dict[key]
        count += 1

    f_test.close()


def tokenize(a_review):
    tmp0 = a_review.replace("'", "")
    tmp = re.sub('[-!,.:]', ' ', re.sub('[^a-zA-Z0-9-!,.: ]', ' ', tmp0))
    #    tmp1 = re.sub(r'([a-zA-Z])([^\w\s]+)', r'\1 \2', tmp)
    #    tmp2 = re.sub(r'([^\w\s]+)([a-zA-Z])', r'\1 \2', tmp1)
    #    tmp3 = re.sub('\s\s+', ' ', tmp2)
    tmp3 = re.sub('\s\s+', ' ', tmp)
    lst_token = map(str.lower, tmp3.split(' '))
    item_list = [e for e in lst_token if e not in listOfStopWords]
    from Stemmer_new import Stemmer
    a_stemmer = Stemmer()
    stemmed_token = a_stemmer.stemWords(item_list)
    count_words(stemmed_token, cnt_all_words)
    # count_words(lst_token, cnt_all_words)
    # return lst_token
    return stemmed_token


def count_words(text, a_dict):
    for token in text:
        if token in a_dict:
            a_dict[token] += 1
        else:
            a_dict[token] = 1


def read_file(nm_train_text, nm_train_label):
    global review
    f_test_labels = open('test_data_labels.txt', 'w')
    fl_train_label = open(nm_train_label, 'r')
    fl_train_text = open(nm_train_text, 'r')
    ln_train_text = fl_train_text.readlines()
    #        train_text = {}
    for line in ln_train_text:
        temp = line.strip().split(' ', 1)
        # review[temp[0]] = tokenize(temp[1])
        review[temp[0]] = temp[1].strip()
    # @to remove
    split_test(review, int(len(ln_train_text) * 0.25))
    # @to remove
    for key in review.keys():
        review[key] = tokenize(review[key])

    # for key in review.keys():
    #     scores = {word: tfidf(word, review[key], review) for word in review[key]}
    #     tf_idf_review[key] = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    #     print key
    #     for word, score in tf_idf_review[key][:3]:
    #         print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))
    ln_train_label = fl_train_label.readlines()
    # train_label = {}
    positive = open('positive.txt', 'w')
    negative = open('negative.txt', 'w')
    deceptive = open('deceptive.txt', 'w')
    truthful = open('truthful.txt', 'w')
    b_positive = []
    b_negative = []
    b_deceptive = []
    b_truthful = []

    for line in ln_train_label:
        temp = line.strip('\n\r').split(' ')
        if temp[0] in review:
            if temp[1] == 'deceptive':
                trust[temp[0]] = False
                trust_bool[False].append(temp[0])
                count_words(review[temp[0]], cnt_trust_false)

                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_deceptive += review[temp[0]]
                deceptive.write(temp[0] + ' ' + tmp_str)
            elif temp[1] == 'truthful':
                trust[temp[0]] = True
                trust_bool[True].append(temp[0])
                count_words(review[temp[0]], cnt_trust_true)
                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_truthful += review[temp[0]]
                truthful.write(temp[0] + ' ' + tmp_str)

            if temp[2] == 'negative':
                sentiment[temp[0]] = False
                sentiment_bool[False].append(temp[0])
                count_words(review[temp[0]], cnt_senti_false)
                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_negative += review[temp[0]]
                negative.write(temp[0] + ' ' + tmp_str)
            elif temp[2] == 'positive':
                sentiment[temp[0]] = True
                sentiment_bool[True].append(temp[0])
                count_words(review[temp[0]], cnt_senti_true)
                tmp_str = ' '.join(map(str, review[temp[0]])) + '\n'
                b_positive += review[temp[0]]
                positive.write(temp[0] + ' ' + tmp_str)
        # @to remove
        else:
            f_test_labels.write(line)
            # @to remove

    # tmp_str = ' '.join(map(str, b_deceptive)) + '\n'
    blob_list['deceptive'] = b_deceptive
    # tmp_str = ' '.join(map(str, b_truthful)) + '\n'
    blob_list['truthful'] = b_truthful
    # tmp_str = ' '.join(map(str, b_negative)) + '\n'
    blob_list['negative'] = b_negative
    # tmp_str = ' '.join(map(str, b_truthful)) + '\n'
    blob_list['positive'] = b_truthful
    for k, blob in blob_list.iteritems():
        scores = {word: tfidf(word, blob, blob_list, k) for word in blob}


# tf_idf_review[k] = sorted(scores.items(), key=lambda x: x[1], reverse=True)
#         print k
#         for word, score in tf_idf_review[k][:3]:
#             print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))


def write_conditional(f, given, a_dict):
    total = float(sum(a_dict.values(), 0.0))
    debug.write('Total = ' + str(total) + '\n')
    alpha = len(cnt_all_words.keys())
    # cond_prob = {k: math.log10(v / total) for k, v in a_dict.iteritems()}
    # laplace smoothing
    cond_prob = {k: math.log10((v + 1) / float(total + alpha)) for k, v in a_dict.iteritems()}
    # cond_prob = {k: ((v) / (total)) for k, v in a_dict.iteritems()}
    count = 1
    for key in cond_prob:

        # if key is None:
        #     debug.write(str(key), review[key])
        cond_str = key + given + '= '
        if count < len(cond_prob.keys()):
            f.write(cond_str + str(cond_prob[key]) + '\n')
            debug.write(cond_str + str(cond_prob[key]) + '\n')
        else:
            f.write(cond_str + str(cond_prob[key]))
            debug.write(cond_str + str(cond_prob[key]))


def main():
    #    nm_train_text = sys.argv[1]
    #    nm_train_label = sys.argv[2]
    nm_train_label = 'train-labels.txt'
    nm_train_text = 'train-text.txt'
    # fl_train_label = open('train-labels.txt','r')
    # fl_train_text = open('train-text.txt','r')

    read_file(nm_train_text, nm_train_label)
    model = open('nbmodel.txt', 'w')
    tot_review = len(review)
    tot_senti_true = len(sentiment_bool[True])
    tot_trust_true = len(trust_bool[True])

    p_true = math.log10(tot_trust_true / float(tot_review))
    p_deceptive = math.log10(1 - p_true)
    p_positive = math.log10(tot_senti_true / float(tot_review))
    p_negative = math.log10(1 - p_positive)

    # p_true = tot_trust_true / decimal(tot_review)
    # p_deceptive = 1 - p_true
    # p_positive = (tot_senti_true / decimal(tot_review))
    # p_negative = (1 - p_positive)


    # model.write('P(Truthful)= ' + str(p_true) + '\n')
    # model.write('P(Deceptive)= ' + str(p_deceptive) + '\n')
    # model.write('P(Positive)= ' + str(p_positive) + '\n')
    # model.write('P(Negative)= ' + str(p_negative) + '\n')

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

    # total = sum(a.itervalues(), 0.0)
    # a = {k: v / total for k, v in a.iteritems()}


# import math
#
#



# python nblearn.py train-text.txt train-labels.txt
if __name__ == '__main__':
    #   python hw3cs561s16.py -i sample01.txt
    main()