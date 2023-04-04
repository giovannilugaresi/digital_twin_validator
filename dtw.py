# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 17:36:17 2021

@author: User
"""
import numpy as np


def dtw(s, t):
    n, m = len(s), len(t)
    dtw_matrix = np.zeros((n+1, m+1))
    for i in range(n+1):
        for j in range(m+1):
            dtw_matrix[i, j] = np.inf
    dtw_matrix[0, 0] = 0
    
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = abs(s[i-1] - t[j-1])
            # take last min from a square box
            last_min = np.min([dtw_matrix[i-1, j], dtw_matrix[i, j-1], dtw_matrix[i-1, j-1]])
            dtw_matrix[i, j] = cost + last_min
    return dtw_matrix[-1,-1]/max(m,n)


#adapted from https://gist.github.com/MJeremy2017/a7a666f3b2bfc333c533056a78be0654#file-dtw2-py
