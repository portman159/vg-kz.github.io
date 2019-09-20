import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
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

# transforming the dfs to include only relevant consolidated columns ('Tech' and 'Others')
technology_list_full = ['Тех.откачная', 'Тех.закачная','Тех.наблюдательная N',
                    'Гидрогеология с керном', 'Гидрогеология без керна', 'Откачная перебур',
                    'Закачная перебур', 'Инж.-гидрогеол. с керном','Тех.наблюдательная',
                    'Тех.наблюдательная S', 'Откачная добур','Закачная добур']
technology_list_short = ['тех. ', 'п/бур техн.', 'г/г']

    
others_list_full = ['Развед. с керном', 'Развед. без керна','Контрольная',
                    'Эксразведка без керна','Эксразведка с керном']
others_list_short = ['э.р. б/к','э.р. с/к', 'разв. с/к', 'разв. б/к', 'кон.']

df_fact_since_jan2018['Прочие_факт_снг'] = df_fact_since_jan2018[others_list_short].sum(axis = 1)
df_fact_since_jan2018.drop(others_list_short, axis = 1, inplace = True)
df_fact_since_jan2018['Технология_факт_снг'] = df_fact_since_jan2018[technology_list_short].sum(axis = 1)
df_fact_since_jan2018.drop(technology_list_short, axis = 1, inplace = True)

df_fact_dec2018["Прочие_факт_дек2018"] = df_fact_dec2018[others_list_full].sum(axis = 1)
df_fact_dec2018.drop(others_list_full, axis = 1, inplace = True)
df_fact_dec2018["Технология_факт_дек2018"] = df_fact_dec2018[technology_list_full].sum(axis = 1)
df_fact_dec2018.drop(technology_list_full, axis = 1, inplace = True)

df_plan_2018["Прочие_план_2018"] = df_plan_2018[others_list_short].sum(axis = 1)
df_plan_2018.drop(others_list_short, axis = 1, inplace = True)
df_plan_2018["Технология_план_2018"] = df_plan_2018[technology_list_short].sum(axis = 1)
df_plan_2018.drop(technology_list_short, axis = 1, inplace = True)

df_plan_dec2018["Прочие_план_дек2018"] = df_plan_dec2018[others_list_short].sum(axis = 1)
df_plan_dec2018.drop(others_list_short, axis = 1, inplace = True)
df_plan_dec2018["Технология_план_дек2018"] = df_plan_dec2018[technology_list_short].sum(axis = 1)
df_plan_dec2018.drop(technology_list_short, axis = 1, inplace = True)

# simplifying the main dataframe
df_month = df_fact_dec2018

# modifying indices of dataframes
df_month.set_index('Дата', inplace = True)

# BLOCK WITH SLIDER(S)
dashboard_plan_sliders = html.Div(children = [
    html.Div(
        dcc.DatePickerRange(
            id = 'date-picker-range-plan',
            month_format = 'DD.MM.YYYY',
            display_format = 'DD.MM.YYYY', 
            with_portal = True,
            first_day_of_week = 1,
            min_date_allowed = df_month.index.min(),
            max_date_allowed = df_month.index.max(),
            initial_visible_month = df_month.index.max(),
            start_date = df_month.index.min(),
            end_date = df_month.index.max(),
        ), className = 'flex items-center justify-center w-third ma0'
    ),
    html.Div(
        dcc.Dropdown(
            id = 'period-choice-plan',
            options = [
                {'label': "Месяц", 'value': "dashplan_month"},
                {'label': 'Год', 'value': 'dashplan_year'},
            ],
            value = 'dashplan_year',
            className = 'flex pa0 w-100 justify-center',
            clearable = False,
            searchable = False,
            style = {'minWidth': '16rem'}
        ),
        className = 'flex flex-grow-1 justify-center items-center w-third ma0 ',
    ),
    html.Div(
        dcc.Dropdown(
            id = 'type-choice-plan',
            options = [
                {'label': 'Всего', 'value': 'total'},
                {'label': "Технология" , 'value': "tech"},
                {'label': "Прочие", 'value': 'others'}
            ], 
            value = 'total',
            className = 'flex pa0 w-100 justify-center',
            clearable = False,
            searchable = False,
            style = {'minWidth': '16rem'}
        ),
        className = 'flex flex-grow-1 justify-center items-center w-third ma0 '
    ),
], className = 'flex justify-around items-stretch pl1 mt1 mr2 h-auto')

# BLOCK WITH LAYERS
dashboard_plan_layer = html.Div(children = [
    html.Div(children = [
        html.H4('Итоговый факт/план', style = {'backgroundColor': '#77a7ae'}),
        dcc.Graph(
            id = 'total-fact-plan', 
            className = 'css_figure',
            config = {
                    'displaylogo': False,
                    'displayModeBar': 'hover', # default: 'hover'
                    'scrollZoom': False, # default: False
                    'showTips': True,
                    'showLink': False,
                    'modeBarButtonsToRemove': ['toggleSpikelines', 'lasso2d', 'select2d','sendDataToCloud']
            }
        ),
    ], className = 'css_cell w-50'),
    html.Div(children = [
        html.H4('Факт/план по участкам', style = {'backgroundColor': '#77a7ae'}),
        dcc.Graph(
            id = 'area-fact-plan',
            className = 'css_figure',
            config = {
                    'displaylogo': False,
                    'displayModeBar': 'hover', # default: 'hover'
                    'scrollZoom': False, # default: False
                    'showTips': True,
                    'showLink': False,
                    'modeBarButtonsToRemove': ['toggleSpikelines', 'lasso2d', 'select2d','sendDataToCloud']
            }
        )
    ], className = 'css_cell w-50'),
], className = 'flex flex-auto justify-between pa1 vh-100', style = {'maxHeight': '80vh'})

reference = '''

#### Справка: типы скважин, входящие в "Технология" и "Прочие"

>

#### Технология
>
> **Cокр.**: *тех., п/бур техн., 'г/г'*
>
> **Полн.**: *Тех.откачная, Тех.закачная, Тех.наблюдательная N, Гидрогеология с керном, Гидрогеология без керна, Откачная перебур, Закачная перебур, Инж.-гидрогеол. с керном, Тех.наблюдательная, Тех.наблюдательная S, Откачная добур, Закачная добур*
>

#### Прочие
>
> **Сокр.**: *э.р. б/к, э.р. с/к, разв. с/к, разв. б/к, кон.*
>
> **Полн.**: *Развед. с керном, Развед. без керна, Контрольная, Эксразведка без керна, Эксразведка с керном*
>
'''
# FINAL LAYOUT
layout = html.Div([
    dashboard_plan_sliders,
    dcc.Markdown(children = '---'),
    dashboard_plan_layer,
    dcc.Markdown(children = '---'),
    dcc.Markdown(reference)
], className = 'flex flex-grow-1 flex-column')