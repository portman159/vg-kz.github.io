import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff
import pandas as pd
from datetime import datetime as dt

# COLORS
seaborn_deep_colors = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3',
 '#8c8c8c', '#ccb974', '#64b5cd', '#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', 
 '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd', '#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', 
 '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd', '#4c72b0', '#dd8452', '#55a868', '#c44e52', 
 '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd', '#4c72b0', '#dd8452', '#55a868', 
 '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd']

diff_20_colors = ['#e6194b','#3cb44b','#ffe119','#4363d8','#f58231','#911eb4','#46f0f0','#f032e6','#bcf60c',
'#fabebe','#008080','#e6beff','#9a6324','#fffac8','#800000','#aaffc3','#808000','#ffd8b1','#000075',
'#808080','#ffffff','#000000']

seaborn_bright_colors = ['#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2', '#9f4800', '#f14cc1',
 '#a3a3a3', '#ffc400', '#00d7ff', '#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2', '#9f4800', 
 '#f14cc1', '#a3a3a3', '#ffc400', '#00d7ff']

# FUNCTION FOR GENERATING STATIC TABLE
def generate_table(dataframe, max_rows = 15):
    if 'pull' in dataframe.columns:
        dataframe.drop(['pull'], axis = 1, inplace = True)
    return html.Table( 
        # Header 
        [html.Tr([html.Th(col) for col in dataframe.columns])] + 

        # Body
        [html.Tr([html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])
        for i in range(min(len(dataframe), max_rows))]
    )

# FUNCTION FOR GENERATING GO TABLE
def generate_go_table(dataframe, headers_list, values_list):
    return {
        'data': [go.Table(
            header = dict(
                values = headers_list,
                fill = dict(color = 'grey'),
                line = dict(color = '#506784'),
                font = dict(color = 'white'),
            ), 
            cells = dict(
                values = values_list,
                align = ['left', 'right'],
                line = dict(color = '#506784')
            )
        )],
        'layout': {
            'margin': {'t': 0, 'r': 0, 'b': 0, 'l': 0}
        }
    }

# FUNCTION FOR GENERATING PIE CHART
def generate_pie(dataframe, values_column, labels_column, colors):
    return {
        'data': [go.Pie(
            labels = dataframe[labels_column],
            values = dataframe[values_column],
            customdata = dataframe[labels_column],
            #textfont = {'size': 8},
            textinfo = 'percent',
            textposition = 'auto',
            showlegend = False,
            sort = False,
            pull = dataframe['pull'],
            direction = 'clockwise',
            marker = {'colors': colors}
        )],
        'layout': {
            'hovermode': 'closest',
            'clickmode': 'select',
            'margin': {'t': 40, 'r': 40, 'b':40, 'l': 40}
        }
    }

# FUNCTION FOR GENERATING LINE CHART
def generate_line(dataframe, x_column, y_column):
    if len(dataframe) == 0:
        return {
            'data': [go.Scatter(
                x = dt.now(),
                y = [0],
                mode = 'lines+markers+text',
                line = {'color': seaborn_deep_colors[0]}
            )],
            'layout': {
                'margin': {'t': 20, 'r': 20, 'b': 35, 'l': 30},
            }
        }
    return {
        'data': [go.Scatter(
            x = dataframe[x_column],
            y = dataframe[y_column],
            mode = 'lines+markers+text',
            line = {'color': seaborn_deep_colors[0]},
        )],
        'layout': {
            'margin': {'t': 20, 'r': 20, 'b': 35, 'l': 30},
            'clickmode': 'select',
            'hovermode': 'closest',
            'xaxis': {
                'tickformat': '%d-%m<br>%Y',
                'tickmode':'auto',
                'nticks':10,
            }
        }
    }

# FUNCTION FOR GENERATING STACKED BAR CHARTS
def generate_bar_stacked(dataframe, y_columns, colors):
    return {
        'data': [
            go.Bar(
                x = dataframe.index,
                y = dataframe[y_column],
                marker = {'color': colors[index]},
                hoverinfo = 'text+y',
                hovertext = "Тип простоя: {}.".format(y_column),
                name = y_column,
                showlegend = True,
                textposition = 'auto'
            ) for index, y_column in enumerate(y_columns)
        ],
        'layout': {
            'barmode': 'stack',
            'margin': {'t': 20, 'r': 20, 'b': 40,'l': 30},
            'hovermode': 'closest',
            'clickmode': 'select'
        }
    }

# FUNCTION FOR GENERATING WATERFALL CHART
def generate_waterfall(x_data, base, y_data):
    return {
        'data': [
            #base
            go.Bar(
                x = x_data,
                y = base,
                marker = dict(color = 'rgba(1,1,1, 0.0)'),
                hoverinfo = 'none',
                showlegend = False,
            ),
            # first layer
            go.Bar(
                x = x_data,
                y = y_data,
                #marker = dict(color = '#4363d8'),
                showlegend = False,
                hoverinfo = 'text+y',
                hovertext = 'Количество часов'
            ),
        ],
        'layout': {
            'barmode': 'stack',
            'margin': {'t': 20, 'r': 20,'b': 70,'l':30},
            'hovermode': 'closest',
            'clickmode': 'select',
            'font': {'size': 8}
        }
    }

# FUNCTION FOR GENERATING GROUPED BAR CHART
def generate_bar_grouped(x, y1, y2,names,title):
    return {
        'data': [
            go.Bar(
                x = x,
                y = y1,
                name = names[0],
                text = y1,
                textposition = 'auto',
            ),
            go.Bar(
                x = x,
                y = y2,
                name = names[1],
                text = y2,
                textposition = 'auto',
            ),
        ],
        'layout': {
            'barmode': 'group',
            'margin': {'t': 45, 'r': 20, 'b': 20, 'l': 60},
            'hovermode': 'closest',
            'clickmode': 'select',
            'title': title
        }
    }

# FUNCTION FOR GENERATING HORIZONTAL BAR CHART
def generate_horizontal_bar(y_data, values, styling_dict):
    return {
        'data': [
            go.Bar(
                y = y_data,
                x = values ,
                showlegend = False,
                text = ['{} %'.format(value) for value in values],
                textposition= 'auto',
                #marker = dict(color = styling_dict['colors']),
                orientation = 'h',
                hoverinfo = 'text+x',
                hovertext = styling_dict['hovertext'],
            )
        ],
        'layout': {
            'margin': {'t': 50, 'r': 20,'b': 60,'l':95},
            'hovermode': 'closest',
            'clickmode': 'select',
            'title': styling_dict['title'],
            'xaxis': {
                'title': 'Процент выполнения плана (%)'
            }
        }
    }
