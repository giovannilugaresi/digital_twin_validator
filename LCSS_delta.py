# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 23:25:09 2021

@author: giuli
"""


import numpy as np

def LCSS(s1,s2,t1,t2,delta):
    matrix_ = np.zeros((len(s1),(len(s2))))
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j] and abs(t1[i]-t2[j])<= delta:
                if i == 0 or j == 0:
                    matrix_[i][j] = 1
                    
                else:
                    matrix_[i][j] = matrix_[i-1][j-1] + 1
            else:
                matrix_[i][j] = max(matrix_[i-1][j], matrix_[i][j-1])

    cs = matrix_[-1][-1]

    return cs


