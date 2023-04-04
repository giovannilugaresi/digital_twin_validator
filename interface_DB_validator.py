# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 11:14:15 2021

@author: franc
"""
import paho.mqtt.client as mqtt
import json
import pandas as pd
import pickle

#import datetime
import time
import datetime
from time import sleep
import numpy as np



from influxdb import InfluxDBClient
from influxdb import DataFrameClient


class interface_DB():
    
    def __init__(self,ip,DB_name,port):
        self.ip=ip
        self.DB_name=DB_name
        self.port=port
        self.client = InfluxDBClient(host=self.ip, port=self.port)
        self.client_df=DataFrameClient(host=self.ip, port=self.port)
        
                
                
    def queryData(self,measures_name,measurement_name,t_query=None,activity=None):
              
        
        self.client.switch_database(self.DB_name)
        
            
        if measurement_name =='history_validation_validator':
          if measures_name=='logic':
           data_logic = self.client.query("SELECT result FROM history_validation WHERE type='" +measures_name+"' ORDER by time DESC LIMIT 2" ,
                  epoch='s')
           data = data_logic.raw
           df = pd.DataFrame(data['series'][0]['values'], columns=['time', 'result'])
           df=df.drop('time', axis='columns')
           logic_results=df.to_numpy()
           
           return logic_results
       
        if measurement_name =='history_validation_validator':
          if measures_name=='input':
           data_input = self.client.query("SELECT result FROM history_validation WHERE type='" +measures_name+"' ORDER by time DESC LIMIT 2" ,
                  epoch='s')
           data = data_input.raw
           df = pd.DataFrame(data['series'][0]['values'], columns=['time', 'result'])
           df=df.drop('time', axis='columns')
           input_results=df.to_numpy()
           
           return input_results
          
            
          
        if measurement_name == 'eventlog_validator':
            eventlog = self.client.query("SELECT * FROM eventlog WHERE time >now()-"+t_query  , epoch='s')
            data = eventlog.raw
            df = pd.DataFrame(data['series'][0]['values'], columns=['time', 'activity', 'id', 'type'])  # Dataframe
            df['activity'] = df['activity'].astype(int)  # conversion of activity column from string to integer
            df['id'] = df['id'].astype(int)  # conversion of id column from string to integer
            df_c = df.drop_duplicates(subset=['activity', 'id', 'type'],   keep='first')  # elimination of duplicates for column 'type' ovvero le letture doppie di start e finish, OCCHIO CHE é UNA COSA MOLTO GREZZA
            eventlog_NP=df_c.to_numpy()
            s=eventlog_NP[:,3]+eventlog_NP[:,1].astype(str)
            string_events_real=s.astype(str)
            time_events_real_=eventlog_NP[:,0]
            time_events_real=time_events_real_.astype(float)
            data_events_real=np.stack((string_events_real,time_events_real),axis=1)
            return data_events_real,df_c
            
        
        if measurement_name == 'distributions_validator':
            if measures_name == 'processing_time_1':
                distribution = self.client.query("SELECT * FROM distributions WHERE measures='" +measures_name+"' ORDER by time DESC LIMIT 1" ,
                                                epoch='s')
                
        
                distribution = pd.DataFrame(distribution.raw['series'][0]['values'],columns=['time', 'measures','type','value'])
                distribution = distribution.drop('time', axis='columns')
                distribution = distribution.drop('measures', axis='columns')
                dist_=str(distribution['type'].to_numpy())
                parameters_=str(distribution['value'].to_numpy())
                dist=dist_[2:-2]
                parameters__=parameters_[3:-3]
                parameters=parameters__.split(',')
                
                return dist, parameters
            
            if measures_name == 'processing_time_2':
                distribution = self.client.query("SELECT * FROM distributions WHERE measures='" +measures_name+"' ORDER by time DESC LIMIT 1",
                                                epoch='s')
               
                distribution = pd.DataFrame(distribution.raw['series'][0]['values'],columns=['time', 'measures','type','value'])
                distribution = distribution.drop('time', axis='columns')
                distribution = distribution.drop('measures', axis='columns')
                dist_=str(distribution['type'].to_numpy())
                parameters_=str(distribution['value'].to_numpy())
                dist=dist_[2:-2]
                parameters__=parameters_[3:-3]
                parameters=parameters__.split(',')
                
                return dist, parameters
        
        
    def writeData(self,measures_name,measurement_name,data):
        self.client.switch_database(self.DB_name)
        data=data
        
        if measurement_name == "history_validation_validator":
            if measures_name == "logic":
               
                json_res=[{"measurement":"history_validation","tags":{"type":"logic"},"fields":{"result":float(data[0]),"value":data[1],"information_type":data[2],"method":data[3]}}]
                self.client.write_points(json_res)
                
            if measures_name == "input":
           
                json_res=[{"measurement":"history_validation","tags":{"type":"input"},"fields":{"result":float(data[0]),"value":data[1],"information_type":data[2],"method":data[3]}}]
                self.client.write_points(json_res)
                
