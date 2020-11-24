# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 18:25:09 2020

@author: Sean Hsia
"""
from BlogProcesser import BlogProcesser
from DataManager import DataFrameManager, CSVManager, DataBaseManager, JsonManager

import argparse

def main(mode):
    #init or update
    
    
    blogporcesser = BlogProcesser()
    df_manager = DataFrameManager()
    csv_manager = CSVManager()
    db_manager = DataBaseManager()
    json_manager = JsonManager()
    
    if mode == "update":
        blogporcesser.updateSavedBlogData()
        src_df = csv_manager.loadCSVtoDataFrame()
        src_df = df_manager.addGenerationFeatures(src_df)
        new_df = df_manager.toDataFrame(blogporcesser.feature_list)
        new_df = df_manager.addGenerationFeatures(new_df)
        db_manager.addDataFrametoDataBase(new_df)
        df = df_manager.appendRowstoDataFrame(src_df, new_df)
        
        csv_manager.toCSV( df.to_dict('records'))
        json_manager.toJSON(  df.to_dict('records'))
    
    elif mode == "init":
        blogporcesser.crawling()
        df = df_manager.addGenerationFeatures(
                df_manager.toDataFrame(blogporcesser.feature_list))
        db_manager.addDataFrametoDataBase(df, mode="replace")        
        csv_manager.toCSV(df.to_dict('records'))
        json_manager.toJSON(df.to_dict('records'))
        
        

if __name__ == '__main__':
    #Create Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode','-m', help="update or init", type=str, default="init")
    args = parser.parse_args()
    main(args.mode)