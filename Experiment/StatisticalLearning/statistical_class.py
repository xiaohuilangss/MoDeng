# encoding=utf-8

"""
class about statistical learning
"""

from DataSource.auth_info import jq_login
from DataSource.stk_data_class import StkData


class AverageStatics(StkData):
    def __init__(self, stk_code):
        super().__init__(stk_code)
        self.down_day_data()
        
    def add_average_line(self):
        pass
    

if __name__ == '__main__':
    
    jq_login()
    self = AverageStatics('000001')
    self.down_day_data(count=1000)
    
    self.data
    end = 0