#!/usr/bin/env python
# coding: utf-8
import os
import re
import jieba
from sklearn import svm
from sklearn import linear_model
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from ..model import Sample
from ..utils import mappings

# 小广告的特点
# 1. 生僻字，根据所有字的 unicode 编码，转数字，再做一次平均数
# 2. 标点多会导致碎词多，可以用单词比例来衡量
# 3. 长度。评论的长度不回特别长，小广告的话很少有短的
# 4. 单词个数
# 5. 贝叶斯的结果
# 6. 数字的比例

# 中文标点
chineses_punct = re.compile(r'[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]')
# 非 数字、中文和英文
useless_char = re.compile(r'[^0-9a-zA-Z\u4E00-\u9FA5]')
# 阿拉伯数字，简体数字，繁体数字
numbers_re = re.compile(r'[0-9\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u96f6\u58f9\u8d30\u53c1\u8086\u4f0d\u9646\u67d2\u634c\u7396\u62fe]')
# bayes pipeline
bayes_pipeline = Pipeline([
    ('vectorizer',  CountVectorizer()),
    ('classifier',  MultinomialNB()) ]
)

svc = linear_model.SGDClassifier()

def read_data_from_file():
    ''' read and make a list of critiques'''
    sentences = []
    with open(os.path.join(os.path.dirname(__file__), 'negative.txt'), 'r') as f:
        for row in f.readlines():
            sentences.append([row, mappings.TYPE['negative']]);

    with open(os.path.join(os.path.dirname(__file__), 'positive.txt'), 'r') as f:
        for row in f.readlines():
            sentences.append([row, mappings.TYPE['positive']]);
    return sentences

def read_data():
    '''
    reads data from database
    '''
    sentences = []
    samples = Sample.query.all()
    return [[x.content, x.type] for x in samples]

def chinese_preprocess(sample_list):
    result = []
    for sample in sample_list:
        sample = chineses_punct.sub('', sample)
        sample = useless_char.sub('', sample)
        cutted = jieba.cut(sample)
        result.append(' '.join(cutted))
    return result

def seprate_value_result(input_set):
    # [['aa', 1], ['bb', 0]] to ['aa', 'bb'], [1, 0]
    values = []
    results = []
    for item in input_set:
        values.append(item[0])
        results.append(item[1])
    return values, results

def number_of_chars(s):
    return len(s)

def number_of_words(s):
    cutted = jieba.cut(s)
    return len(list(cutted))

def average_char_ord(s):
    '''
    平均字符 unicode 数值
    '''
    total = 0
    for c in s:
        total += ord(c)
    return total / 1000 / number_of_chars(s)

def word_percentage(s):
    '''
    单词比例，词数／字数
    '''
    return number_of_words(s) / number_of_chars(s)

def bayes_judgement(s):
    # clean puncts will help bayes to judge better
    cleaned = chinese_preprocess([s])
    results = bayes_pipeline.predict(cleaned)
    return results[0]

def numbers_count(s):
    n = numbers_re.findall(s)
    return len(n)

def make_feature_vector(sample_set):
    feature_vector = []
    for sample in sample_set:
        feature = []
        # caculate features
        # feature.append(number_of_chars(sample))
        feature.append(number_of_words(sample))
        feature.append(average_char_ord(sample))
        feature.append(word_percentage(sample))
        feature.append(numbers_count(sample))
        feature.append(bayes_judgement(sample))

        feature_vector.append(feature)
    return feature_vector

def learn_sample(from_file=False):
    if from_file:
        # first load two files into program [['sentence', 0], ['sentence 2', 1]]
        # 0 is negatve and 1 is positive
        sentences = read_data_from_file()
    else:
        sentences = read_data()
    train_value, train_result = seprate_value_result(sentences)
    clean_train_value = chinese_preprocess(train_value)
    bayes_pipeline.fit(clean_train_value, train_result)
    train_vector = make_feature_vector(train_value)
    svc.fit(train_vector, train_result)
    return True

def judge(case_list):
    # cases is list
    if not isinstance(case_list, list):
        case_list = [case_list]
    v = make_feature_vector(case_list)
    return svc.predict(v)
