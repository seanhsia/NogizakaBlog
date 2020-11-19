# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 21:16:43 2020

@author: Sean Hsia
"""
import os

#Data Manage Tools
import pandas as pd
import numpy as np
import json
from sqlalchemy import create_engine



class DataManager():
    def __init__(self, path=''):
        self.path = path
        self.generation_map={'asuka.saito': 1,
             'ayame.tsutsui': 4,
             'ayane.suzuki': 2,
             'ayanochristie.yoshida': 3,
             'erika.ikuta': 1,
             'fourth': 4,
             'haruka.kaki': 4,
             'hazuki.mukai': 3,
             'hina.higuchi': 1,
             'hinako.kitano': 2,
             'junna.itou': 2,
             'kaede.satou': 3,
             'kana.nakada': 1,
             'kazumi.takayama': 1,
             'kenkyusei': 2,
             'maaya.wada': 1,
             'mai.shinuchi': 2,
             'mai.shiraishi': 1,
             'manatsu.akimoto': 1,
             'mayu.tamura': 4,
             'minami.hoshino': 1,
             'minami.umezawa': 3,
             'mio.yakubo': 4,
             'miona.hori': 2,
             'miria.watanabe': 2,
             'mizuki.yamashita': 3,
             'momoko.oozono': 3,
             'newfourth': 4,
             'ranze.terada': 2,
             'rei.seimiya': 4,
             'rena.yamazaki': 2,
             'renka.iwamoto': 3,
             'reno.nakamura': 3,
             'riria.itou': 3,
             'sakura.endou': 4,
             'saya.kanagawa': 4,
             'sayaka.kakehashi': 4,
             'sayuri.matsumura': 1,
             'seira.hayakawa': 4,
             'shiori.kubo': 3,
             'staff': 0,
             'tamami.sakaguchi': 3,
             'third': 3,
             'yuna.shibata': 4,
             'yuri.kitagawa': 4,
             'yuuki.yoda': 3}
    def toDataFrame(self, data_list):
        return pd.DataFrame(data_list).drop_duplicates()
    
    def toCSV(self, data_list):
        print("writing CSV...")
        df = self.toDataFrame(data_list)
        df.to_csv(self.path+'blogdata.csv', index=False, encoding='utf_8_sig')
        
    def toJSON(self, data_list):
        print("writing JSON...")
        with open(self.path+'blogdata.json', 'w', encoding='utf-8') as file:
            json_obj = json.dumps(data_list)
            file.write(json_obj)
            
    def loadCSVtoDataFrame(self):
        print("Loading from CSV file...")
        return pd.read_csv(self.path+'blogdata.csv', encoding='utf_8_sig')
    
    def loadJSONtoDataFrame(self):
        print("Loading from JSON file...")
        with open(self.path+'blogdata.json', 'r', encoding='utf-8') as file:
            feat_list = json.load(file)
        return self.toDataFrame(feat_list)
    
    def appendRowstoDataFrame(self, src_df, new_df):
        return src_df.append(new_df, ignore_index=True).drop_duplicates()
    
    def sortByFeat(self, df , column_names , ascending=False):
        return df.sort_values(column_names, ignore_index=True, ascending=ascending)
    
    def addGenerationFeatures(self, df):
        generation_arr = np.array(list(map(lambda x: self.generation_map[x], df["Author"])))
        df["Generation"] = generation_arr
        return df
        
    
    def createDBEngine(self, db_name='nogizaka'):
        try:
            #Create connection to Mysql database
            host='localhost'                      # server name
            database=db_name                      # database name
            user=os.environ.get("DB_USER")        # user name
            password=os.environ.get("DB_PASSWD")   # password
            

            engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:3306/{database}')

            test = engine.connect()
            test.close()
            return engine
            
        except Exception as e:
            print("Database connection failure：", e)
    
    def addDataFrametoDataBase(self, df, mode="append"):
        engine = self.createDBEngine()
        df.to_sql("blogs", engine, index=False, if_exists=mode)
        print("Dataframe was written into database successfully")
        
    
    def loadDataBasetoDataFrame(self):
        engine = self.createDBEngine()
        return pd.read_sql("blogs", engine)
        
        

    
    
        