import math
import random
import json
import re
import sys

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

# debug = open('debug.txt', 'w')


def split_test(a_dict, a_size):
    f_test = open('test_data.txt', 'w')
    # f_test_labels = open('test_data_labels.txt', 'w')
    rand_keys = random.sample(a_dict, a_size)
    # test_data = {}
    count = 1
    for key in rand_keys:
        if key in a_dict:
            if count < len(rand_keys):
                f_test.write(key + ' ' + a_dict[key] + '\n')
            else:
                f_test.write(key + ' ' + a_dict[key])
            # test_data[key] = a_dict[key]
            del a_dict[key]
            count += 1
        # else:
        #     a_dict[key] = tokenize(a_dict[key])
    # json.dump(test_data, open('test_data.txt', 'w'))
    # d2 = json.load(open("text.txt"))
    # lines = f_test.readlines()
    f_test.close()
    # write = open('test_data.txt', 'w')
    # write.writelines([item for item in lines[:-1]])
    # item = lines[-1].rstrip()
    # write.write(item)
    # write.close()

def tokenize(a_review):
    lst_token = []
    #re.sub(' +', ' ', a_review)
    re.sub('\s\s+', ' ', a_review)
    lst_token = map(str.lower, a_review.split(' '))
    count_words(lst_token, cnt_all_words)
    return lst_token


def count_words(text, a_dict):
    for token in text:
        if token in a_dict:
            a_dict[token] += 1
        else:
            a_dict[token] = 1


def read_file(nm_train_text, nm_train_label):
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
    split_test(review, int(len(ln_train_text)*0.25))
    # @to remove
    for key in review.keys():
        review[key] = tokenize(review[key])

    ln_train_label = fl_train_label.readlines()
    # train_label = {}
    for line in ln_train_label:
        temp = line.strip('\n\r').split(' ')
        if temp[0] in review:
            if temp[1] == 'deceptive':
                trust[temp[0]] = False
                trust_bool[False].append(temp[0])
                count_words(review[temp[0]], cnt_trust_false)
            else:
                trust[temp[0]] = True
                trust_bool[True].append(temp[0])
                count_words(review[temp[0]], cnt_trust_true)

            if temp[2] == 'negative':
                sentiment[temp[0]] = False
                sentiment_bool[False].append(temp[0])
                count_words(review[temp[0]], cnt_senti_false)
            else:
                sentiment[temp[0]] = True
                sentiment_bool[True].append(temp[0])
                count_words(review[temp[0]], cnt_senti_true)
        # @to remove
        else:
            f_test_labels .write(line)
        # @to remove

def write_conditional(f, given, a_dict):
    total = sum(a_dict.values(), 0.0)
    alpha = len(a_dict.keys())
    cond_prob = {k: math.log10(v / total) for k, v in a_dict.iteritems()}
    # laplace smoothing
    # cond_prob = {k: math.log10((v + 1) / (total + alpha)) for k, v in a_dict.iteritems()}
    for key in cond_prob:
        # if key is None:
        #     debug.write(str(key), review[key])
        cond_str = key + given + '= '
        f.write(cond_str + str(cond_prob[key]) + '\n')



def main():
    nm_train_text = sys.argv[1]
    nm_train_label = sys.argv[2]
    # fl_train_label = open('train-labels.txt','r')
    # fl_train_text = open('train-text.txt','r')
    # nm_train_label = 'train-labels.txt'
    # nm_train_text = 'train-text.txt'
    read_file(nm_train_text, nm_train_label)
    model = open('nbmodel.txt','w')
    tot_review = len(review)
    tot_senti_true = len(sentiment_bool[True])
    tot_trust_true = len(trust_bool[True])

    p_true = math.log10(tot_trust_true / float(tot_review))
    p_deceptive = math.log10(1 - p_true)
    p_positive = math.log10(tot_senti_true / float(tot_review))
    p_negative = math.log10(1 - p_positive)

    # model.write('P(Truthful)= ' + str(p_true) + '\n')
    # model.write('P(Deceptive)= ' + str(p_deceptive) + '\n')
    # model.write('P(Positive)= ' + str(p_positive) + '\n')
    # model.write('P(Negative)= ' + str(p_negative) + '\n')

    model.write('truthful= ' + str(p_true) + '\n')
    model.write('deceptive= ' + str(p_deceptive) + '\n')
    model.write('positive= ' + str(p_positive) + '\n')
    model.write('negative= ' + str(p_negative) + '\n')

    write_conditional(model, '|truthful', cnt_trust_true)
    write_conditional(model, '|deceptive', cnt_trust_false)

    write_conditional(model, '|positive', cnt_senti_true)
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
# def tf(word, blob):
#     return blob.words.count(word) / len(blob.words)
#
# def n_containing(word, bloblist):
#     return sum(1 for blob in bloblist if word in blob.words)
#
# def idf(word, bloblist):
#     return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))
#
# def tfidf(word, blob, bloblist):
#     return tf(word, blob) * idf(word, bloblist)


# python nblearn.py train-text.txt train-labels.txt
if __name__ == '__main__':
    #   python hw3cs561s16.py -i sample01.txt
    main()