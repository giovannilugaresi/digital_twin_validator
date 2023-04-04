# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 11:34:08 2021

@author: giuli
"""



import time
from class_validator import validator
import numpy as np
from interface_DB_validator import interface_DB
import pandas as pd

#Edo's libraries
from DigitalModel import DigitalModel

#Fra's libraries
from init_position import init_position
from simulator import simulator
from processing_time import processing_time
from system_time_real import system_time_real
from interdeparture_time_real import interdeparture_time_real
from p_time_transform import p_time_transform

#initial parameters settings
t_query="10m"
frequency=60
simulator_type="Manpy"
information_type='kpi'
kpi='system_time'
method='DTW'

epsilon=None
delta=None
n_pallet=12
source_type="sensors"
#threshold setting
if information_type=='events':
    threshold_logic=0.5
    threshold_input=0.5
    
if information_type=='kpi':
    threshold_logic=0.95
    threshold_input=0.92

#objects
l=validator('logic',threshold_logic)
inp=validator('input',threshold_input)
db= interface_DB('192.168.0.50', "RTSimulatorDB", port=8086)


condition_validation = True
condition_logic = True

while condition_validation == True:
    
    # logic validation
    
    # query history validation
    logic_res=interface_DB.queryData(db,'logic','history_validation_validator',None,None)
    
    # query eventlog real
    er,eventlog_real=interface_DB.queryData(db,None,'eventlog_validator',t_query,None)

    # input simulation
    p_timereal=processing_time(eventlog_real)
    p_timesimul_input=p_time_transform(p_timereal,simulator_type)
    init_pos= init_position(source_type,n_pallet,eventlog_real) 
  
    # call simulation
    sys,_,_,es,interdep=simulator(
                    db=db,
                    simulator_type =simulator_type,
                    t_horizon=None,
                    p_timesimul_input = p_timesimul_input,
                    init_pos = init_pos,
                    use_type = "logic_validation", 
                    n_pallet=n_pallet,
                    source_type=source_type,
                    )
    
    
    # check logic with events
    if information_type == 'events':
        
        for i in range(np.size(es[:,1])):
            
#sinchronization adjustments for current model
         if es[i,0]=='f1' or es[i,0]=='f2':
           es[i,1]=float(es[i,1])-3.22
    
        es=es[(es[:,1].astype(float)).argsort()]
        a_=np.where(er[:,0]=='s1')
        a=a_[0][0]
        tstart=(er[a,1]).astype(float)
        
        data_l=validator.event_v(l,er[a:,0],es[:,0],er[a:,1].astype(float)-tstart,es[:,1].astype(float),delta,method)

    # check logic with KPIs
    if information_type=='kpi':
        if kpi=='system_time':
            sys_real_=system_time_real(n_pallet,eventlog_real)
            sys_sim=np.array([])
            for i in range (len(sys)):
                sys_sim=np.append(sys_sim,sys[i][2])
            sys_real=sys_real_.to_numpy()
            sys_real=sys_real[:,1]
            data_l=l.kpi_v(sys_real,sys_sim,method,epsilon)
            
        if kpi=='interdeparture_time':
           interdep_real_=interdeparture_time_real(eventlog_real)
           interdep_sim=np.array([])
           for i in range (len(interdep)):
             interdep_sim=np.append(interdep_sim,interdep[i][2])
           interdep_real=interdep_real_.to_numpy()
           interdep_real=interdep_real[:,1] 
           data_l=l.kpi_v(interdep_real,interdep_sim,method,epsilon)
  
    
   
    # write results on DB
    if data_l[0]==1:
        print(data_l)
        interface_DB.writeData(db,'logic','history_validation_validator',data_l)
        print('model logic is valid')
        condition_logic = True
        
    elif (data_l[0]==0 and int(sum(logic_res))!=0 and int((logic_res[0]))!=2):
        print(data_l)
        interface_DB.writeData(db,'logic','history_validation_validator',data_l)
        print('warning: model logic to be monitored')
        condition_logic = True
        
    elif data_l[0]==0 and( int(sum(logic_res))==0 or int((logic_res[0]))==2):
        data_l[0]=2
        print(data_l)
        interface_DB.writeData(db,'logic','history_validation_validator',data_l)
        print('model logic is not valid-->model has to be generated again')
        condition_logic = False

   # input validation
   
    if condition_logic == True:
        input_res=interface_DB.queryData(db,'input','history_validation_validator',None,None)
        
        # query distributions
        dist1, parameters1=interface_DB.queryData(db,'processing_time_1','distributions_validator',t_query,None)
        dist2, parameters2=interface_DB.queryData(db,'processing_time_2','distributions_validator',t_query,None)
        
        # inputs correlation
        processing=p_timesimul_input.to_numpy()
        P1=processing[:,0]
        P2=processing[:,1]
        corr_P1=inp.input_trace(P1,dist1,parameters1)
        corr_P2=inp.input_trace(P2,dist2,parameters2)
        
        if simulator_type=='Manpy':
          dict_DF_corr = {
            "M1": pd.Series(corr_P1.tolist()),
            "M2": pd.Series(corr_P2.tolist())
            }
          processing_corr = pd.DataFrame(dict_DF_corr)
          
        if simulator_type=='Arena':
          dict_DF_corr = {
            "1": pd.Series(corr_P1.tolist()),
            "2": pd.Series(corr_P2.tolist()),
            "3": pd.Series(corr_P2.tolist())
            }
          processing_corr = pd.DataFrame(dict_DF_corr)
        
        # call simulation
        sys_corr,_,_,es_corr,interdep_corr=simulator(
                        db=db,
                        simulator_type =simulator_type,
                        t_horizon=None,
                        p_timesimul_input = processing_corr,
                        init_pos = init_pos,
                        use_type = "input_validation", 
                        n_pallet=n_pallet,
                        source_type=source_type,
                        )
        
        # check input with events
        if information_type=='events':
#sinchronization adjustments for current model
            for i in range(np.size(es_corr[:,1])):
             if es_corr[i,0]=='f1' or es_corr[i,0]=='f2':
               es_corr[i,1]=float(es_corr[i,1])-3.22
        
            es_corr=es_corr[(es_corr[:,1].astype(float)).argsort()]
            data_i=validator.event_v(inp,er[a:,0],es_corr[:,0],er[a:,1].astype(float)-tstart,es_corr[:,1].astype(float),delta,method)
            
        # check input with KPIs  
        if information_type=='kpi':
            if kpi=='system_time':
                sys_sim_corr=np.array([])
                for i in range (len(sys_corr)):
                    sys_sim_corr=np.append(sys_sim_corr,sys_corr[i][2])
                data_i=inp.kpi_v(sys_real,sys_sim_corr,method,epsilon)
             
             
            if kpi=='interdeparture_time': 
                interdep_sim_corr=np.array([])
                for i in range (len(interdep_corr)):
                    interdep_sim_corr=np.append(interdep_sim_corr,interdep_corr[i][2])
                data_i=inp.kpi_v(interdep_real,interdep_sim_corr,method,epsilon)
       
            
    # write results on DB
        if data_i[0]==1:
            print(data_i)
            interface_DB.writeData(db,'input','history_validation_validator',data_i)
            print('model inputs are valid')
            condition_input = True
            
        elif (data_i[0]==0 and int(sum(input_res))!=0 and int((input_res[0]))!=2):
            print(data_i)
            interface_DB.writeData(db,'input','history_validation_validator',data_i)
            print('warning: model inputs to be monitored')
            condition_input = True
            
        elif data_i[0]==0 and( int(sum(input_res))==0 or int((input_res[0]))==2):
            data_i[0]=2
            print(data_i)
            interface_DB.writeData(db,'input','history_validation_validator',data_i)
            print('model inputs are not valid-->distributions have to be generated again')
            condition_input = False
    
    time.sleep(frequency)
    
    
    
