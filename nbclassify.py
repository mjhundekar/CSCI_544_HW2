import re
import json
import sys
prior = {}
cond_truthful = {}
cond_deceptive = {}
cond_positive = {}
cond_negative = {}
# cond_all = {}
test_cnt_all_words = {}
test_review = {}
true_labels = {}
pred_labels = {}


# def read_test_remove(fname):
#     global test_review
#     test_review = json.load(open(fname))
#     for key in test_review.keys():
#         test_review[key] = tokenize(test_review[key])


def tokenize(a_review):
    global test_cnt_all_words
    lst_token = []
    #re.sub(' +', ' ', a_review)
    re.sub('\s\s+', ' ', a_review)
    lst_token = map(str.lower, a_review.split(' '))
    count_words(lst_token, test_cnt_all_words)
    review_dict = {}
    for token in lst_token:
        if token in review_dict:
            review_dict[token] += 1
        else:
            review_dict[token] = 1
    return review_dict


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

            if which_dict =='truthful':
                cond_truthful[key] = float (curr[1])
                continue
            elif which_dict =='deceptive':
                cond_deceptive[key] = float(curr[1])
                continue
            elif which_dict == 'positive':
                cond_positive[key] = float(curr[1])
                continue
            elif which_dict == 'negative':
                cond_negative[key] = float(curr[1])
                continue


def compute_probability(a_id, a_review, a_class_dict):
    prob = 0.0
    a_review_dict = test_review[a_id]
    for key in a_review_dict.keys():
        cnt_key = a_review_dict[key]
        if key in a_class_dict:
            prob = prob + (cnt_key * a_class_dict[key])
        else:
            continue
    return prob


def classify_sentiment(a_id, a_review):
    # positive
    prior_positive = prior['positive']
    rev_cond_positive = compute_probability(a_id, a_review, cond_positive)
    positive_score = prior_positive + rev_cond_positive
    # negative
    prior_negative = prior['negative']
    rev_cond_negative = compute_probability(a_id, a_review, cond_negative)
    negative_score = prior_negative + rev_cond_negative
    if positive_score > negative_score:
        return 'positive'
    else:
        return 'negative'
    # return ''


def classify_trust(a_id, a_review):
    # truthful
    prior_truthful = prior['truthful']
    rev_cond_truthful = compute_probability(a_id, a_review, cond_truthful)
    truthful_score = prior_truthful + rev_cond_truthful
    # deceptive
    prior_deceptive = prior['deceptive']
    rev_cond_deceptive = compute_probability(a_id, a_review, cond_deceptive)
    deceptive_score = prior_deceptive + rev_cond_deceptive
    if truthful_score > deceptive_score:
        return 'truthful'
    else:
        return 'deceptive'
    # return ''

def read_output_labels():



def main():
    nm_test_text = sys.argv[1]
    global test_review
    # nm_test_text = 'test_data.txt'
    read_model()
    read_test(nm_test_text)
    read_output_labels()
    # read_test_remove(nm_test_text)
    nboutput = open('nboutput.txt', 'w')
    cnt = 1
    for key in test_review.keys():
        str_trust = classify_trust(key, test_review[key])
        str_sentiment = classify_sentiment(key, test_review[key])

        if cnt < len(test_review.keys()):
            nboutput.write(key + ' ' + str_trust + ' ' + str_sentiment + '\n')
        else:
            nboutput.write(key + ' ' + str_trust + ' ' + str_sentiment)
        cnt += 1
    nboutput.close()


# python nbclassify.py test_data.txt
if __name__ == '__main__':
    main()
