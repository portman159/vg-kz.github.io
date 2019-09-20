import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from import_dataset import excel_file_dec2018, excel_file_winter
from datetime import datetime as dt
import pandas as pd
import numpy as np
import os 

print(os.getcwd())
print(os.listdir(os.getcwd()))

# GETTING AND CLEANING DATA

# getting data for the period 26 Nov - 25 Dec 2018
df_dec2018 = pd.read_excel(excel_file_dec2018, sheet_name = 'SVODJORNAL')

# getting data for the period 14 Nov 2018 - 3 Feb 2019
df_winter = pd.read_excel(excel_file_winter, sheet_name = 'SVODJORNAL' )

# preparing the main dataframe
df = df_winter

# key columns
time_spent = 'Затрачено времени, час      ВСЕГО'
key_metric_type = "Наименование выполненных работ"
key_metric_area = "Участок" 
key_metric_drilling = "Номер буровой установки"

# keeping only relevant columns
columns_to_keep = ['Дата', key_metric_area, key_metric_drilling, 'Статус', key_metric_type, time_spent]
df = df[columns_to_keep]

# deleting empty rows
df = df[df[time_spent].notnull()]

# filtering data, relevant to downtime
df = df[(df["Статус"] == "Простой/ожидание")]
df.drop('Статус', axis = 1, inplace = True)

# setting index to be datetime-based for convenience
df.set_index("Дата", inplace = True)

# EXTRACTING VARIABLES FOR SIMPLICITY
areas = df[key_metric_area].unique()
areas.sort()
types = df[key_metric_type].unique()
types.sort()


# BLOCK WITH SLIDERS
dashboard_downtime_sliders = html.Div(children = [
    html.Div(
        dcc.DatePickerRange(
            id = 'date-picker-range-downtime',
            month_format = 'DD.MM.YYYY',
            display_format = 'DD.MM.YYYY', 
            with_portal = True,
            first_day_of_week = 1,
            min_date_allowed = df.index.min(),
            max_date_allowed = df.index.max(),
            initial_visible_month = df.index.max(),
            start_date = df.index.min(),
            end_date = df.index.max(),
        ), className = 'flex items-center justify-center w-third ma0'
    ),
    html.Div(
        dcc.Dropdown(
            id = 'area-choice-downtime',
            options = [{'label': area, 'value': area} for area in areas],
            value = areas,
            multi = True,
            placeholder = 'Выберите участок',
            className = 'flex pa0 w-100',
            style = {'minWidth': '32rem'}
        ), className = 'flex flex-grow-1 items-center justify-center w-two-thirds ma0'
    ),
], className = 'flex justify-around items-stretch h-auto pl1 mt1 mr2')

# BLOCK WITH LAYERS
dashboard_downtime_layer1 = html.Div(children = [
    html.Div(children = [
        html.H4('Простои по видам,[час]', style = {'backgroundColor': '#77a7ae'}),
        dcc.Graph(id = 'table-type-downtime', className = 'css_figure', config = {'displaylogo': False, 'showLink': False}),
    ], className = 'css_cell w-25'),
    html.Div(children = [
        html.Div(children = [
            html.H4('Простои по видам, [уд.вес%]', style = {'backgroundColor': '#77a7ae'}),
            dcc.Graph(
                id = 'pie-type-downtime',
                className = 'css_figure', 
                clear_on_unhover = True,
                config = {
                    'displaylogo': False,
                    'displayModeBar': 'hover', # default: 'hover'
                    'autosize': True,
                    'fillFrame': False,
                    'scrollZoom': False, # default: False
                    'showTips': True,
                    'showLink': False,
                    'modeBarButtonsToRemove': ['toggleSpikelines', 'lasso2d', 'select2d','sendDataToCloud']
                }
            )
        ], className = 'css_cell h-auto'),
        html.Div(children = [
            html.H4('Динамика простоев в течение периода, [час]', style = {'backgroundColor': '#ffebae'}),
            dcc.Graph(
                id = 'line-dynamics-downtime', 
                className = 'css_figure',
                config = {
                    'displaylogo': False,
                    'displayModeBar': 'hover', # default: 'hover'
                    'autosize': True,
                    'fillFrame': False,
                    'scrollZoom': False, # default: False
                    'showTips': True,
                    'showLink': False,
                    'modeBarButtonsToRemove': ['toggleSpikelines', 'lasso2d', 'select2d','sendDataToCloud']
                }
            )
        ], className = 'css_cell h-auto')
    ], className = 'css_stack w-50'),
    html.Div(children = [
        html.Div(children = [
            html.H4('Простои по участкам, [час]', style = {'backgroundColor':'#ffadc1'}),
            dcc.Graph(id = 'table-area-downtime', className = 'css_figure', config = {'showLink': False, 'displaylogo': False}),
        ], className = 'css_cell', style = {'maxHeight': '50%'}),
        html.Div(children = [
            html.H4('Простои по участкам, [уд.вес%]', style = {'backgroundColor': '#ffadc1'}),
            dcc.Graph(
                id = 'pie-area-downtime',
                className = 'css_figure',
                clear_on_unhover = True,
                config = {
                    'displaylogo': False,
                    'displayModeBar': 'hover', # default: 'hover'
                    'autosize': True,
                    'fillFrame': False,
                    'scrollZoom': False, # default: False
                    'showTips': True,
                    'showLink': False,
                    'modeBarButtonsToRemove': ['toggleSpikelines', 'lasso2d', 'select2d','sendDataToCloud']
                }
            )
        ], className = 'css_cell h-auto')
    ], className = 'css_stack w-25')
], className = 'flex flex-auto justify-between pa1', style = {'maxHeight': '75vh', 'minHeight': '30rem'})

dashboard_downtime_layer2 = html.Div(children = [
    html.Div(children = [
        html.H4('Простои по БУ, [час]', style = {'backgroundColor': '#d5b8c6'}),
        dcc.Graph(
            id = 'stacked-bar-drilling-downtime', 
            className = 'css_figure',
            config = {
                'displaylogo': False,
                'displayModeBar': 'hover', # default: 'hover'
                'autosize': True,
                'fillFrame': False,
                'scrollZoom': False, # default: False
                'showTips': True,
                'showLink': False,
                'modeBarButtonsToRemove': ['toggleSpikelines', 'lasso2d', 'select2d','sendDataToCloud']
            }
        )
    ], className = 'css_cell')
], className = 'flex flex-auto justify-between pa1', style = {'minHeight': '20rem'})

# FINAL LAYOUT
layout = html.Div([
    dashboard_downtime_sliders,
    dcc.Markdown(children = '---'),
    dashboard_downtime_layer1,
    dashboard_downtime_layer2,
    dcc.Markdown(children = '---')
], className = 'flex flex-grow-1 flex-column')