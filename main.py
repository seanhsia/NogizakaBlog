# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 18:25:09 2020

@author: Sean Hsia
"""
from BlogProcesser import BlogProcesser
from DataManager import DataManager

import argparse

def main(mode):
    #init or update
    
    
    blogporcesser = BlogProcesser()
    datamanager = DataManager()
    
    if mode == "update":
        blogporcesser.updateSavedBlogData()
        src_df = datamanager.loadCSVtoDataFrame()
        src_df = datamanager.addGenerationFeatures(src_df)
        new_df = datamanager.toDataFrame(blogporcesser.feature_list)
        new_df = datamanager.addGenerationFeatures(new_df)
        datamanager.addDataFrametoDataBase(new_df)
        df = datamanager.appendRowstoDataFrame(src_df, new_df)
        
        datamanager.toCSV( df.to_dict('records'))
        datamanager.toJSON(  df.to_dict('records'))
    
    elif mode == "init":
        blogporcesser.crawling()
        df = datamanager.addGenerationFeatures(
                datamanager.toDataFrame(blogporcesser.feature_list))
        datamanager.addDataFrametoDataBase(df, mode="replace")        
        datamanager.toCSV(df.to_dict('records'))
        datamanager.toJSON(df.to_dict('records'))
        
        

if __name__ == '__main__':
    #Create Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode','-m', help="update or init", type=str, default="init")
    args = parser.parse_args()
    main(args.mode)