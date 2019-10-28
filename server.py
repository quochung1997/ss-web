from flask import request, url_for, render_template
from flask_api import FlaskAPI, status, exceptions

app = FlaskAPI(__name__)


import pickle
loaded_model = pickle.load(open('finalized_model_svm_2.sav', 'rb'))

# calculate TF
def compute_TF(word_dict, bow):
    tf_dict = {}
    bow_count = len(bow)
    for word in word_dict:
        tf_dict[word] = word_dict[word] / (float(bow_count)+1)

    return tf_dict


def compute_IDF(doc_list):
    import math
    idf_dict = {}
    N = len(doc_list)

    # count number of documents that contain this word
    idf_dict = dict.fromkeys(doc_list[0].keys(), 0)
    for doc in doc_list:
        for word in doc:
            if doc[word] > 0:
                idf_dict[word] += 1

    for word in idf_dict:
        idf_dict[word] = math.log(N / float(idf_dict[word]))

    return idf_dict


def compute_TFIDF(tf_bow, idfs):
    tfidf = {}
    for word in tf_bow:
        tfidf[word] = tf_bow[word]*idfs[word]
    return tfidf


def check_if_number(s):
    return '0' in s or '1' in s or '2' in s or '3' in s or '4' in s or '5' in s or '6' in s or '7' in s or '8' in s or '9' in s


class DataWord():
    def __init__(self):
        self.bow = ""
        self.word_dict = {}
        self.tf_bow = {}
        self.idfs = {}
        self.tfidf = {}
        self.label = ""


f_m = open('metrix.txt', 'r', encoding='utf-8')

word_set = set()
for line in f_m:
    tm = line.replace('\n', '')
    #print(tm)
    word_set.add(tm)


def read_file(fn):
    f = open(fn+'.txt', 'r', encoding='utf-8')
    arr = []
    for line in f:
        line = line.lower()
        line = line.replace('\n', ' ').strip()
        arr.append(line)
    return arr


filename_nat = 'Nat'
filename_neg = 'Neg'
filename_pos = 'Pos'

nat = read_file(filename_nat)
neg = read_file(filename_neg)
pos = read_file(filename_pos)


def detect(s):
    if s in nat:
        return 'nat'

    if s in pos:
        return 'pos'

    if s in neg:
        return 'neg'

    dw = DataWord()
    line = s.lower()
    line = line.replace('\n', ' ')
    arr = line.split(' ')
    new_arr = []
    for a in arr:
        if a.isalpha():
            new_arr.append(a)
    dw.bow = new_arr
    f_idfs = open('idfs_2.txt', 'r', encoding='utf-8')
    idfs = {}
    for i in f_idfs:
        i = i.replace('\n', '')
        i = i.split(' ')
        idfs[i[0]] = float(i[1])
    dw.word_dict = dict.fromkeys(word_set, 0)
    for word in dw.bow:
        if word in dw.word_dict:
            dw.word_dict[word] += 1
    dw.tf_bow = compute_TF(dw.word_dict, dw.bow)
    dw.tfidf = compute_TFIDF(dw.tf_bow, idfs)

    data = []

    for i in dw.tfidf:
        data.append(dw.tfidf[i])

    import numpy as np
    res = loaded_model.predict([np.array(data)])[0]
    if res == 1:
        res = 'Positive'
    elif res == 0:
        res = 'Natural'
    else:
        res = 'Negative'
    return res


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/api", methods=[ 'POST'])
def detect_api():
    if request.method == 'POST':
        a = request.get_json()

        print(a)

        res = {
            "data": detect(a['data'])
        }

        return res, status.HTTP_200_OK


if __name__ == "__main__":
    app.run(debug=True)
