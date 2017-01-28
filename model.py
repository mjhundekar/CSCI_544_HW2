# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 18:06:28 2017

@author: mjhundekar
"""
class Review:
    def __init__(self, text, sentiment, trust):
        self.review = tokenize(text)
        self.sentiment = False
        self.trust = False
        if sentiment == 'deceptive':
            self.trust = False
        else:
            self.trust = True

        if trust == 'negative':
            self.trust = False
        else:
            self.trust = True


# class Reviews:
#     def __init__(self, nm_train_label, nm_train_text):
#         #        self.id = ''
#         self.review = {}
#         self.sentiment = {True: [], False: []}
#         self.trust = {True: [], False: []}
#
#         fl_train_label = open(nm_train_label, 'r')
#         fl_train_text = open(nm_train_text, 'r')
#
#         ln_train_text = fl_train_text.readlines()
#         #        train_text = {}
#         for line in ln_train_text:
#             temp = line.strip('\n\r').split(' ', 1)
#             self.review[temp[0]] = tokenize(temp[1])
#         # train_text[temp[0]] = map(str.lower, temp[1].split(' '))
#
#         ln_train_label = fl_train_label.readlines()
#         #        train_label = {}
#         for line in ln_train_label:
#             temp = line.strip('\n\r').split(' ')
#             if temp[1] == 'deceptive':
#                 self.trust[temp[0]] = False
#             else:
#                 self.trust[temp[0]] = True
#
#             if temp[2] == 'negative':
#                 self.sentiment[temp[0]] = False
#             else:
#                 self.sentiment[temp[0]] = True


def tokenize(review):
    lst_token = []
    lst_token = map(str.lower, review.split(' '))
    return lst_token


# fl_train_label = open('train-labels.txt','r')
# fl_train_text = open('train-text.txt','r')
#
# ln_train_label = fl_train_label.readlines()
# train_label = {}
# for line in ln_train_label:
#    temp = line.strip('\n\r').split(' ',1)
#    train_label[temp[0]] = temp[1].split(' ',1)




def main():
    #    file_name = sys.argv[2]
    # all_reviews = Reviews('train-labels.txt', 'train-text.txt')
    # print all_reviews.review.get('yQBISMl7HLyFhtIhQGVn')

    fl_train_label = open('train-labels.txt','r')
    fl_train_text = open('train-text.txt','r')
    ln_train_text = fl_train_text.readlines()

    train_text = {}
    for line in ln_train_text:
        temp = line.strip('\n\r').split(' ', 1)
        train_text[temp[0]] = temp[1]
    # train_text[temp[0]] = map(str.lower, temp[1].split(' '))

    ln_train_label = fl_train_label.readlines()
    train_label = {}
    for line in ln_train_label:
        temp = line.strip('\n\r').split(' ')
        train_label[temp[0]] = temp[1:]
        # if temp[1] == 'deceptive':
        #     trust[temp[0]] = False
        # else:
        #     trust[temp[0]] = True
        #
        # if temp[2] == 'negative':
        #     sentiment[temp[0]] = False
        # else:
        #     sentiment[temp[0]] = True
    all_reviews = {}
    for key in train_text.keys():
        all_reviews[key] = Review(train_text[key],train_label[key][0], train_label[key][1])

if __name__ == '__main__':
    #   python hw3cs561s16.py -i sample01.txt
    main()


