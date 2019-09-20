import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from import_dataset import excel_file_repair
from datetime import datetime as dt
import pandas as pd
import numpy as np
import os 


# GETTING AND CLEANING DATA
df = pd.read_excel(excel_file_repair, sheet_name = 'Свод ТОиР')
df = df[df['Затрачено времени, часов'].notnull()]
df.set_index('Дата', inplace = True)

# EXTRACTING VARIABLES FOR SIMPLICITY

# defining variables for convenience
time_spent = 'Затрачено времени, часов'
key_metric_type = 'Тип оборудования'
key_metric_location = 'Локация поломки 1'
key_metric_id = "Боротовой № оборудования"
key_metric_status = 'Статус ремонта'

equipments = df['Тип оборудования'].unique()
equipments.sort()


# BLOCK WITH SLIDERS
dashboard_repair_sliders = html.Div(children = [
    html.Div(
        dcc.DatePickerRange(
            id = 'date-picker-range-repair',
            month_format = 'DD.MM.YYYY',
            display_format = 'DD.MM.YYYY', 
            with_portal = True,
            first_day_of_week = 1,
            min_date_allowed = df.index.min(),
            max_date_allowed = df.index.max(),
            initial_visible_month = df.index.max(),
            start_date = dt(2018, 11, 1),
            end_date = df.index.max(),
        ), className = 'flex items-center justify-center w-third ma0 '
    ),
    html.Div(
        dcc.Dropdown(
            id = 'equipment-choice-repair',
            options = [{'label': equipment, 'value': equipment} for equipment in equipments],
            value = equipments,
            multi = True,
            placeholder = 'Выберите тип',
            className = 'flex pa0 w-100',
            style = {'minWidth': '32rem'},
        ), className = 'flex flex-grow-1 items-center justify-center w-two-thirds ma0'
    ),
], className = 'flex justify-around items-stretch h-auto pl1 mt1 mr2')


dashboard_repair_layer1 = html.Div(children = [
    dcc.Graph(id = 'table-statistics-repair', className = 'css_figure pa0 ma0', style = {'maxHeight': '15vh'}, config = {'displaylogo': False, 'showLink': False}),
])

dashboard_repair_layer2 = html.Div(children = [
    html.Div(children = [
        html.Div(children = [
            html.Div(children = [
                html.H4('Затрачено времени на тип оборудования,[час]', style = {'backgroundColor': '#77a7ae'}),
                dcc.Graph(
                    id = 'pie-type-repair',
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
            ], className = 'css_cell w-third '),
            html.Div(children = [
                html.H4('Затрачено времени на статус ремонта, [час]', style = {'backgroundColor': '#77a7ae'}),
                dcc.Graph(
                    id = 'waterfall-status-repair', 
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
            ], className = 'css_cell w-two-thirds '),
        ], className = 'flex flex-auto justify-between pa1 h-75'),
        html.Div(children = [
            html.H4('Динамика ремонтов в течение периода, [час]', style = {'backgroundColor': '#ffebae'}),
            dcc.Graph(
                id = 'line-dynamics-repair', 
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
        ], className = 'css_cell h-25')
    ], className = 'css_stack w-two-thirds'),
    html.Div(children = [
        html.Div(children = [
            html.H4('Затрачено времени на локацию поломки', style = {'backgroundColor':'#ffadc1'}),
            dcc.Graph(id = 'table-location-repair', className = 'css_figure', config = {'showLink': False, 'displaylogo': False}),
        ], className = 'css_cell h-auto', style = {'maxHeight': '34%'}), 
        html.Div(children = [
            html.H4('Затрачено времени на уникальное оборудование', style = {'backgroundColor':'#ffadc1'}),
            dcc.Graph(id = 'table-equipment-repair', className = 'css_figure', config = {'showLink': False, 'displaylogo': False}),
        ], className = 'css_cell h-auto', style = {'maxHeight': '66%'}),
    ], className = 'css_stack w-third')
], className = 'flex flex-auto justify-between pa1', style = {'maxHeight': '95vh', 'minHeight': '30rem'})

# FINAL LAYOUT
layout = html.Div([
    dashboard_repair_sliders,
    dcc.Markdown(children = '---'),
    dashboard_repair_layer1,
    dcc.Markdown(children = '---'),
    dashboard_repair_layer2,
    dcc.Markdown(children = '---')
], className = 'flex flex-grow-1 flex-column')