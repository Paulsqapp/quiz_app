'''
user answers are stored here before being sent to database
'''

import pandas as pd
import random
class Answer_basket:

    def __init__(self, request):
        self.session = request.session
        self.answer_basket = self.session.get('answers', pd.DataFrame(columns=['number','answers'], index=[0]))

    def add():
        x = 20*random.int()
        y = 10*random.int()
        self.re

        pass

    def __str__(self):
        return f'{self.answer_basket}'
