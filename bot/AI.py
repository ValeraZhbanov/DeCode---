# -*- coding: UTF-8 -*-

import re
import json
import math
import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import losses
from tensorflow.keras import metrics
from tensorflow.keras import activations

from tensorflow.keras import utils

from gensim.models import Word2Vec


class PreTokenizer:
    """
    Класс для работы с токенайзером
    """
    def __init__(self, path2dict):
        self.word2vec = Word2Vec.load(path2dict)


    def __call__(self, x, outlen=50):
        tokens = self.vectorizator(x, outlen)
        vectors = self.embedding(tokens, outlen)
        return vectors
        

    def split(self, input_text, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n', split=' ', outlen=50):
        """
        Удаляет лишние символы и приврошает текст в вектора
        """
        input_text = input_text.lower()

        translate_dict = {c: split for c in filters}
        translate_map = str.maketrans(translate_dict)
        input_text = input_text.translate(translate_map)

        seq = input_text.split(split)
        elem = [i for i in seq if i and i in self.word2vec.wv]
        return (elem + ["" for _ in range(outlen - len(elem))])[:outlen]


    def vectorizator(self, x, outlen=50):
        return np.array([self.split(elem, outlen=outlen) for elem in x], dtype=str)


    def embedding(self, x, maxlen=50):
        result = np.zeros(shape=[x.shape[0], maxlen, self.word2vec.wv.vector_size], dtype=np.float32)

        for i, text in enumerate(x):
        
            index = 0
            for word in text:

                if word in self.word2vec.wv:
                    result[i, index, :] = self.word2vec.wv[word]
                    index += 1

        return result


class ModerationHelper:
    """
    Класс для работы с моделью модерации
    """
    def __init__(self, path2weight, tokenizer):

        unit = 64
        input_size = 50
        output_size = 4
        DIM = 200

        input = layers.Input(shape=(input_size, DIM))

        x = layers.Bidirectional(layers.LSTM(unit))(input)

        output = layers.Dense(output_size, activation=activations.sigmoid)(x)

        model = keras.Model(inputs=input, outputs=output)

        model.compile(optimizer=optimizers.Adam(), loss=losses.binary_crossentropy, metrics=['accuracy'])

        model.load_weights(path2weight)

        self.input_size = input_size 
        self._model = model
        self._tokenizer = tokenizer
        

    def __call__(self, texts):
        """
        Метод для создания таблицы с метриками текстов
        """
        result = []

        for text in texts:
            result += [self._predict(text)]

        return ModerationHelper._get_table_mark(result)


    def normal_text(self, text):
        """
        Метод для оценки строки текста
        """
        return self._predict(text)[0]


    def _predict(self, text):

        texts = [text]

        vectors = self._tokenizer(texts, self.input_size)
        prediction = self._model.predict(vectors, verbose=0)

        return np.mean(prediction, axis=0)


    def _get_table_mark(data, texts=None):
        classes = {
            "__label__NORMAL" :     "Нормальный",
            "__label__INSULT" :     "Оскорбление",
            "__label__THREAT" :     "Угроза",
            "__label__OBSCENITY" :  "Непристойность",
        }

        classes_key = dict([(key, it) for it, key in enumerate(classes.keys())])

        result = []
        for it, row in enumerate(data):
            res = {}

            if not texts is None:
                res["Текст"] = texts[it]


            ss = []
            if (0.50 < row[1]):
                ss += ["оскорбления"]
            if (0.50 < row[2]):
                ss += ["угрозы"]
            if (0.50 < row[3]):
                ss += ["непристойности"]


            res = {"Статус": round(float(row[0])), "Комментарий": "", "Подробно": {}}

            if len(ss) != 0: 
                res["Комментарий"] = "Текст содержит " + ", ".join(ss) + "."

            for key in classes:
                idx = classes_key[key]
                res["Подробно"][classes[key]] = float(row[idx])


            result += [res]

        return result


class QAHelper:
    """
    Класс для определения типа сообщения 
    """
    def __init__(self, path2weight, tokenizer):

        unit = 64
        input_size = 50
        output_size = 2
        DIM = 200

        inp = layers.Input(shape=(input_size, DIM))

        x = layers.Bidirectional(layers.LSTM(unit))(inp)
        out = layers.Dense(output_size, activation=activations.sigmoid)(x)

        model = keras.Model(inputs=inp, outputs=out)

        model.compile(optimizer=optimizers.Adam(), loss=losses.binary_crossentropy, metrics=['binary_accuracy'])

        model.load_weights(path2weight)

        self.input_size = input_size 
        self._model = model
        self._tokenizer = tokenizer
        

    def __call__(self, text):
        return self._predict(text)


    def _predict(self, text):

        texts = [text]

        vectors = self._tokenizer(texts, self.input_size)
        prediction = self._model.predict(vectors, verbose=0)

        return np.mean(prediction, axis=0)







class TransformerBlock(layers.Layer):
    """
    Класс реализующий основной слой архитектуры трансформер
    """
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, **kwords):
        super(TransformerBlock, self).__init__(**kwords)

        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)

        self.ffn = keras.Sequential(
            [
                layers.Dense(ff_dim, activation="relu"),
                layers.Dense(embed_dim),
            ]
        )

        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)

        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)


    def call(self, inputs, training):

        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)

        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


class TokenAndPositionEmbedding(layers.Layer):
    """
    Класс реализующий слой кодирования архитектуры трансформер
    """
    def __init__(self, maxlen, embed_dim, **kwords):
        super(TokenAndPositionEmbedding, self).__init__(**kwords)

        self.pos_emb = layers.Embedding(input_dim=maxlen, output_dim=embed_dim)
        self.maxlen = maxlen

    def call(self, x):
        positions = tf.range(start=0, limit=self.maxlen, delta=1)
        return x + self.pos_emb(positions)

