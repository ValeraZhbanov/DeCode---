# -*- coding: cp1251 -*-
import re
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class BotGTP:
    def __init__(self):
        self.modelname = "sberbank-ai/rugpt3large_based_on_gpt2"
        self.tok = GPT2Tokenizer.from_pretrained(self.modelname)
        self.model = GPT2LMHeadModel.from_pretrained(self.modelname).cuda()

    def generate(self, texts):
        self.system = """Система: Вы ассистент (чат бот ВКонтакте) главы города Мирный региона Якутия, вы искусственный интеллект, большая языковая модель. Внимательно следуйте инструкциям пользователя. Давайте ответы в официально деловом стиле. Отвечайте с помощью markdown. \n"""

        text = self.system + "\n".join([f"{role[0]}: {role[1]}" for role in texts]) + "\n" + "Ассистент:"

        input_ids = self.tok.encode(text, return_tensors="pt").cuda()

        generated = self.model.generate(
            input_ids.cuda(),
            max_new_tokens=200,
            repetition_penalty=4.0,
            do_sample=True,
            top_k=3,
            top_p=0.99,
            temperature=0.6,
            num_beams=10,
            no_repeat_ngram_size=3,
            num_return_sequences=1).cuda()

        out = generated[0]
        out = out[len(input_ids[0]) :]
        out = self.tok.decode(out)

        m = re.search('(<.{1,10}>)|(\n[А-яA-z ]{1,20}:)', out)

        if m:
            out = out[: m.start()]

        return out


