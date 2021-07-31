# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 19:05:28 2020

@author: Sean Hsia
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import argparse

from DataManager import CSVManager, DataBaseManager, JsonManager


#Create Parser
parser = argparse.ArgumentParser()
parser.add_argument('--loadfrom','-l', help="Load from json, csv or db", type=str, default="csv")
parser.add_argument('--port', '-p', help="which port you want this server run on", type=int, default=8900)
args = parser.parse_args()

#Load Data based on argument
csv_manager = CSVManager()
db_manager = DataBaseManager()
json_manager = JsonManager()

if args.loadfrom == 'db':
    df = db_manager.loadDataBasetoDataFrame()

elif args.loadfrom == 'json':
    df = json_manager.loadJSONtoDataFrame()
    
else:
    df = csv_manager.loadCSVtoDataFrame()

#Basic Settings    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
    'background': '#333333',
    'text': '#7FDBFF'
}


app.layout = html.Div([
    html.H1("Nogizaka Blog Data", style={'text-align': 'center'}),
    
    html.Div([
        dcc.Dropdown(
            id='customization_dropdown',
            options=[{'label': 'Yes', 'value':'Yes'},
                     {'label': 'No', 'value':'No'}],
            placeholder="Select member or not"
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Dropdown(
            id='members',
            options=[]
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Dropdown(
            id='feature',
            options=[{'label': 'Number of Comments', 'value':'Number of Comments'},
                     {'label': 'Number of Characters in Title', 'value':'Number of Characters in Title'},
                     {'label': 'Number of Characters in Context', 'value':'Number of Characters in Context'},
                     {'label': 'Number of Images', 'value':'Number of Images'}],
            value='Number of Comments'
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),
    dcc.Graph(id='linegraph')

])

@app.callback(
    [Output('members', 'options'), 
     Output('members', 'multi')],
    [Input('customization_dropdown', 'value')]
)
def updateDropDown(customize):
    if customize == "Yes":
        names = df.sort_values("Author")["Author"].unique()
        return [{'label': name, 'value': name} for name in names], True
    
    else:
        options = [{'label': 'All', 'value': 'All'},
                   {'label': '1st Generation', 'value': 1},
                   {'label': '2nd Generation', 'value': 2},
                   {'label': '3rd Generation', 'value': 3},
                   {'label': '4th Generation', 'value': 4}]
        
        return options, False
    

@app.callback(
    Output('linegraph', 'figure'),
    [Input('members', 'value'),
     Input('feature', 'value')]
)
def updateFigure(slct_mem, feature):
    dfc = df.copy()
    if type(slct_mem) is list and slct_mem != []:
        dfc = dfc[dfc["Author"].isin(slct_mem)].reset_index(drop=True)
    elif type(slct_mem) is int:
        dfc = dfc[dfc["Generation"]==slct_mem].reset_index(drop=True)
    
    elif type(slct_mem) is None :
         return None
    print(slct_mem)
       
    dfc['Date']=dfc['Date'].str.replace('/','-')    
    dfc = dfc.loc[:, ["Author", "Title", "Date", feature]]
    dfc = dfc.sort_values("Date", ignore_index=True, ascending=True)
    
    
    fig = px.line(
            data_frame=dfc,
            x="Date",
            y=feature,
            color="Author",
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
    fig.update_traces(mode="markers+lines")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=args.port)
