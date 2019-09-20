import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from generate_figure_module import generate_table, generate_go_table
from dashboard_tabs import dashboard_downtime
from import_dataset import excel_file_dec2018
from datetime import datetime as dt
import pandas as pd
import numpy as np
import os



# GETTING AND CLEANING DATA

# getting data for the period 26 Nov - 25 Dec 2018
df_fact_dec2018 = pd.read_excel(excel_file_dec2018, sheet_name = 'Факт (скв) М')
df_fact_since_jan2018 = pd.read_excel(excel_file_dec2018, sheet_name = 'Факт (скв) с н.г.')
df_plan_dec2018 = pd.read_excel(excel_file_dec2018, sheet_name = 'План (скв) М')
df_plan_since_jan2018 = pd.read_excel(excel_file_dec2018, sheet_name = 'План (скв) с н.г.')
df_plan_2018 = pd.read_excel(excel_file_dec2018, sheet_name = 'План (скв) Г')

df_plan_2018 = df_plan_2018.fillna(0)
df_plan_dec2018 = df_plan_dec2018.fillna(0)
df_plan_since_jan2018 = df_plan_since_jan2018.fillna(0)
df_fact_since_jan2018 = df_fact_since_jan2018.fillna(0)
df_fact_dec2018 = df_fact_dec2018.fillna(0)

df = df_fact_dec2018

areas = dashboard_downtime.areas

# modifying monthly fact dataframe to have the same columns as monthly plan df
df.set_index('Дата', inplace = True)
df['Всего'] = df.sum(axis = 1)

shortcuts_reference = {
    'тех. ': ['Тех.откачная', 'Тех.закачная','Тех.наблюдательная N','Тех.наблюдательная','Тех.наблюдательная S'],
    'п/бур техн.': ['Откачная перебур','Закачная перебур','Откачная добур','Закачная добур'],
    'г/г': ['Гидрогеология с керном', 'Гидрогеология без керна','Инж.-гидрогеол. с керном'],
    'э.р. б/к': ['Инж.-гидрогеол. с керном'],
    'э.р. с/к': ['Эксразведка с керном'],
    'разв. с/к': ['Развед. с керном'], 
    'разв. б/к': ['Развед. без керна'],
    'кон.': ['Контрольная']
}

technology_list_full = ['Тех.откачная', 'Тех.закачная','Тех.наблюдательная N',
                    'Гидрогеология с керном', 'Гидрогеология без керна', 'Откачная перебур',
                    'Закачная перебур', 'Инж.-гидрогеол. с керном','Тех.наблюдательная',
                    'Тех.наблюдательная S', 'Откачная добур','Закачная добур']
technology_list_short = ['тех. ', 'п/бур техн.', 'г/г']

    
others_list_full = ['Развед. с керном', 'Развед. без керна','Контрольная',
                    'Эксразведка без керна','Эксразведка с керном']
others_list_short = ['э.р. б/к','э.р. с/к', 'разв. с/к', 'разв. б/к', 'кон.']

for k, v in shortcuts_reference.items():
    df[k] = df[v].sum(axis = 1)

df.drop(technology_list_full, axis = 1, inplace = True)
df.drop(others_list_full, axis = 1, inplace = True)

# BLOCK WITH LAYERS

dashboard_reference_layer1 = html.Div(children = [
    html.Div(children = [
        html.Div(
            dcc.DatePickerRange(
                id = 'date-picker-range-reference',
                month_format = 'DD.MM.YYYY',
                display_format = 'DD.MM.YYYY', 
                with_portal = True,
                first_day_of_week = 1,
                min_date_allowed = df.index.min(),
                max_date_allowed = df.index.max(),
                initial_visible_month = df.index.max(),
                start_date = df.index.min(),
                end_date = df.index.max(),
            ), 
            className = 'flex items-center justify-center w-100 ma0'
        ),
        html.Div(
            dcc.Dropdown(
                id = 'area-choice-reference',
                options = [{'label': area, 'value': area} for area in areas],
                value = areas,
                multi = True,
                placeholder = 'Выберите участок',
                className = 'flex pa0 w-100',
                style = {'minWidth': '16rem'}
            ), 
            className = 'flex flex-grow-1 items-center justify-center ma0'
        ),
    ], className = 'css_stack w-50 mt3 mr2'),
    html.Div(children = [
        html.H4('Годовой план', style = {'backgroundColor':'#ffadc1'}),
        dcc.Graph(id = 'table-plan-year-reference', className = 'css_figure', config = {'displaylogo': False, 'showLink': False})
    ], className = 'css_cell w-50')
], className = 'flex flex-auto justify-between pa1 vh-50')

dashboard_reference_layer2 = html.Div(children = [
    html.Div(children  = [
        html.H4('План на месяц', style = {'backgroundColor': '#77a7ae'}),
        dcc.Graph(id = 'table-plan-month-reference', className = 'css_figure', config = {'displaylogo': False, 'showLink': False}),
    ], className = 'css_cell w-50'),
    html.Div(children = [
        html.H4('План с начала года', style = {'backgroundColor': '#d5b8c6'}),
        dcc.Graph(id = 'table-plan-sng-reference', className = 'css_figure', config = {'displaylogo': False, 'showLink': False}),
    ], className = 'css_cell w-50'),
], className = 'flex flex-auto justify-between pa1 vh-50')

dashboard_reference_layer3 = html.Div(children = [
    html.Div(children = [
        html.H4('Факт с начала месяца', style = {'backgroundColor': '#77a7ae'}),
        dcc.Graph(id = 'table-fact-month-reference', className = 'css_figure', config = {'displaylogo': False, 'showLink': False}),
    ], className = 'css_cell w-50'),
    html.Div(children = [
        html.H4('Факт с начала года', style = {'backgroundColor': '#d5b8c6'}),
        dcc.Graph(id = 'table-fact-sng-reference', className = 'css_figure', config = {'displaylogo': False, 'showLink': False})
    ], className = 'css_cell w-50')
], className = 'flex flex-auto justify-between pa1 vh-50')

layout = html.Div([
    dashboard_reference_layer1,
    dashboard_reference_layer2,
    dashboard_reference_layer3
], className = 'flex flex-grow-1 flex-column')