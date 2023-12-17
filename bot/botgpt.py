# -*- coding: cp1251 -*-
import re
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class BotGTP:
    """
    Класс для работы с языковой моделью
    """
    def __init__(self):
        self.modelname = "sberbank-ai/rugpt3large_based_on_gpt2" 
        self.system = "Вы помощник главы города Мирный (региона Саха-Якутия) с искусственным интеллектом, языковая модель обученная помогать пользователям, внимательно читайте вопросы и давайте ответы на них. "
        self.tok = GPT2Tokenizer.from_pretrained(self.modelname)
        self.model = GPT2LMHeadModel.from_pretrained(self.modelname).cuda()

        
    def generate(self, text):
        text = self.system + text
        input_ids = self.tok.encode(text, return_tensors="pt").cuda()
        out = text

        for it in range(2):
            generated = self.model.generate(
                input_ids.cuda(),
                max_length=len(text) + 100 * (it + 1),
                repetition_penalty=2.0,
                do_sample=True,
                top_k=3, 
                top_p=0.95, 
                temperature=0.8,
                num_beams=10, 
                no_repeat_ngram_size=3, 
                num_return_sequences=1)

            input_ids = generated

            out = self.tok.decode(generated[0])

            m = re.search('<.{1,10}>', out)


            if m:
                out = out[: m.start()]
                return out[len(text) :]

        return out[len(text) :]


