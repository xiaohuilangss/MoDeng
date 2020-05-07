# encoding=utf-8

"""
本脚本主要实现利用利用多核cpu对pandas进行计算的目的

在对pandas的行进行apply函数时，实现多进程并行计算的目的！

注意，使用该函数前需要关闭相关连接，因为多进程会创建多个网络连接！
"""
import multiprocessing
import math


class ParallelCalculateDf:
    def __init__(self, df, obj, process_amount=10):
        """
        :param df: 将要被并行计算的df
        :param lmd_str: apply中的lambda函数
        :param process_amount:进程数
        :param obj: 有时候进行apply处理是，需要用到一些对象，比如某些类
        """
        self.obj = obj
        self.process_amount = process_amount
        self.df = df
        
        # 创建进程池
        self.pool = multiprocessing.Pool(process_amount)
        self.log = ''
    
    def reset_df(self):
        """
        对df设置索引，用于等分数据
        :return:
        """
        try:
            self.df['idx'] = list(range(len(self.df)))
            self.df = self.df.set_index(keys='idx')
        except Exception as _e:
            self.log = self.log + '函数reset_df出错！原因：\n%s\n' % str(_e)

    def splice_index(self):
        """
        对index进行等分，返回各个等分段的起始index和理论等分长度（最后一部分可能会短一些）
        :return:
        """
        # 处理df数据行数小于进程数的情况（无妨)
        seg_len = int(math.ceil(len(self.df)/self.process_amount))
        seg_start = range(0, len(self.df), seg_len)
        
        seg = [(x, x+seg_len-1) for x in seg_start]
        
        # 处理尾部，一般会出现尾部超出实际的情况
        seg[-1] = (seg[-1][0], len(self.df)-1)
        
        return seg

    # 进入线程池进行计算
    @staticmethod
    def seg_process(df, seg, obj):
        def lmd(x):
            """
            重现此函数实现并行计算
            :param x:
            :return:
            """
            return None
        return df.loc[seg[0]:seg[1], :].apply(lambda x: lmd(x), axis=1)
        
    def apply_pl(self):
        
        # 空值判断
        if self.df.empty:
            self.log = self.log + '函数apply_pl:输入df为空！函数返回！\n'
            return None
        
        # 重置索引
        self.reset_df()
        
        # 分割index，获取段信息
        seg_list = self.splice_index()
        
        r = [self.pool.apply_async(self.seg_process, (self.df, s, self.obj, )).get() for s in seg_list]
        self.pool.close()
        self.pool.join()
        
        # 汇总结果
        r_sum = []
        for r_sig in r:
            r_sum = r_sum + list(r_sig.values)
            
        return r_sum
        
        
if __name__ == '__main__':
    
    # 使用范例
    class MyPc(ParallelCalculateDf):
        def __init__(self, df, obj):
            super().__init__(df, obj)
        
        @staticmethod
        def seg_process(df, seg, obj):
            def lmd(x):
                """
                重现此函数实现并行计算
                :param x:
                :return:
                """
                return obj[0].predict_my([x[obj[1].feature_col].values], debug=True)
            
            return df.loc[seg[0]:seg[1], :].apply(lambda x: lmd(x), axis=1)

