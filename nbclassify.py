import re
prior = {}
cond_truthful = {}
cond_deceptive = {}
cond_positive = {}
cond_negative = {}
cnt_all_words = {}
review = {}


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


def read_test(nm_test_text):
    fl_test_text = open(nm_test_text, 'r')
    ln_test_text = fl_test_text.readlines()
    #        test_text = {}
    for line in ln_test_text:
        temp = line.strip().split(' ', 1)
        review[temp[0]] = tokenize(temp[1].strip())
        # review[temp[0]] = temp[1].strip()

    return 0


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


def main():
    #  nm_train_text = sys.argv[2]

    nm_test_text = 'test_data.txt'
    read_model()


if __name__ == '__main__':
    main()

