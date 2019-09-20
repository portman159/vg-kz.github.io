import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from generate_figure_module import generate_table
from dashboard_tabs import dashboard_downtime
from import_dataset import excel_file_dec2018, excel_file_winter
from datetime import datetime as dt
import pandas as pd
import numpy as np
import os



# GETTING AND CLEANING DATA

# getting data for the period 14 Nov 2018 - 3 Feb 2019
df = pd.read_excel(excel_file_winter, sheet_name = 'SVODJORNAL' )

# cleaning both dfs
job_list_simple = ["Скважина сооружена (пробурена)", "Скважина сооружена", "Скважина пробурена"]
job_list = ['21. Скважина сооружена', '9. Скважина пробурена']
columns_list = ['Дата', "Участок", "Номер буровой установки", "Номер скважины", "Тип скважины", "Статус", "Наименование выполненных работ"]

df = df[columns_list]
df = df[df['Наименование выполненных работ'].isin(job_list)]

df.drop_duplicates(inplace = True)
df = df.fillna('')

# modifying indices of dataframes
df.set_index('Дата', inplace = True)

# creating variables for convenience
drilling_rigs = df['Номер буровой установки'].unique()
drilling_rigs.sort()

# BLOCK WITH SLIDERS
dashboard_status_sliders = html.Div(children = [
    html.Div(
        dcc.DatePickerRange(
            id = 'date-picker-range-status',
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
            id = 'drillingrig-choice-status',
            options = [{'label': rig, 'value': rig} for rig in drilling_rigs],
            value = '',
            className = 'flex pa0 w-100 justify-center',
            clearable = False,
            searchable = False,
            placeholder = 'Номер БУ',
            style = {'minWidth': '16rem'}
        ),
        className = 'flex flex-grow-1 justify-center items-center w-third ma0 ',
    ),
    html.Div(
        dcc.Dropdown(
            id = 'job-choice-status',
            options = [{'label': job, 'value': job} for job in job_list_simple], 
            value = '',
            className = 'flex pa0 w-100 justify-center',
            clearable = False,
            searchable = False,
            placeholder = 'Выполненная работа',
            style = {'minWidth': '16rem'}
        ),
        className = 'flex flex-grow-1 justify-center items-center w-third ma0 '
    ),
], className = 'flex justify-around items-stretch pl1 mt1 mr2 h-auto')


# BLOCK WITH LAYERS
dashboard_status_layer1 = html.Div(
    dcc.Graph(id = 'table-overview-status', className = 'css_figure mr3', config = {'displaylogo': False, 'showLink': False}),
)

# FINAL LAYOUT
layout = html.Div([
    dashboard_status_sliders,
    dcc.Markdown(children = '---'),
    dashboard_status_layer1,
], className = 'flex flex-grow-1 flex-column')