# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 15:12:14 2022

@author: giuli
"""


import numpy as np
from LCSS_delta import LCSS
from dtw import dtw
from LCSSR import LCSSR


class validator():

  
   def __init__(self,type_validation,threshold):
       self.type_validation=type_validation
       self.threshold=threshold

        
          
   def event_v(self,data_real,data_sim,time_real,time_sim,delta,method):
                information_type="Events"    
            
                
                if  method=='LCSS':
      
            
                    ind= LCSS(data_real[:],data_sim[:],time_real[:],time_sim[:],delta)/min(len(data_real[:]),len(data_sim[:]))     ### LCSS with delta
                    if ind>= self.threshold:
                        value=1
                    else:
                        value=0
                    
                    data=[value,ind,information_type,method]
                   
                return data
            
   def kpi_v(self,data_real,data_sim,method,epsilon):
              information_type="KPI"    
 
              if method== 'DTW':
                 ind= 1- dtw(data_real[:]/max(max(data_real[:]),max(data_sim[:])),data_sim[:]/max(max(data_real[:]),max(data_sim[:])))
                 if ind >= self.threshold:
                     value=1
                 else:
                     value=0
                
                 data=[value,ind,information_type,method]
               
              
              if method== 'LCSSR':
                 ind= LCSSR(data_real[:],data_sim[:],epsilon)/max(len(data_real[:]),len(data_sim[:]))
                 if ind >= self.threshold:
                     value=1
                 else:
                     value=0
                
                 data=[value,ind,information_type,method]
               
              return data
                      
   def input_trace(self,processing_times_real,dist,param):
        
        from ecdf import ecdf
        import scipy.stats
        from scipy.stats import norm
        from scipy.stats import beta
        from scipy.stats import gamma
        from scipy.stats import lognorm
        from scipy.stats import pareto
        from scipy.stats import logistic
        from scipy.stats import rayleigh
        from scipy.stats import uniform
        from scipy.stats import triang
     
         
        n_parts=np.size(processing_times_real)
        u_p=np.array([])
        X_p,F_p = ecdf(processing_times_real)
        for ii in range(n_parts):
          u_p = np.append(u_p,F_p[np.asarray(np.where(X_p == processing_times_real[ii]))])

        """Distributions"""

        
        #  1. Uniform Distribution
        if dist=='uniform':
            y_p = uniform.ppf(u_p,float(param[0]),float(param[1])) 
            
        #  2. Triangular Distribution
        if dist=='triang':
            y_p = triang.ppf(u_p,float(param[0]),float(param[1]),float(param[2])) 
        
        #  3. Normal Distribution
        if dist=='norm':
            y_p = norm.ppf(u_p,float(param[0]),float(param[1])) 
        
        #  4. Beta Distribution
        if dist=='beta':
            y_p =beta.ppf(u_p,float(param[0]),float(param[1]),float(param[2]),float(param[3]))
        
        #  5. Gamma Distribution
        if dist=='gamma':
            y_p = gamma.ppf(u_p,float(param[0]),float(param[1]),float(param[2])) 
            
        #  6. Lognormal Distribution
        if  dist=='lognorm':
            y_p = lognorm.ppf(u_p,float(param[0]),float(param[1]),float(param[2])) 
                 
        #  7. Pareto Distribution
        if  dist=='pareto':
            y_p = pareto.ppf(u_p,float(param[0]),float(param[1]),float(param[2])) 
            
        #  8. Logistic Distribution
        if dist=='logistic':
            y_p = logistic.ppf(u_p,float(param[0]),float(param[1])) 
            
        #  9. Rayleigh Distribution
        if dist=='rayleigh':
            y_p = rayleigh.ppf(u_p,float(param[0]),float(param[1])) 




        if max(y_p) == np.inf:
            pos = np.where(y_p==np.inf)
            pos=np.asarray(pos)
            y_p[pos] = processing_times_real[pos]

        correlated_processing_time=y_p

         
        return correlated_processing_time
       
            
 