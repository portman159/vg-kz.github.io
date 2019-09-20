# -- PART 1: SETUP -- #
# IMPORTING MUST-HAVE PYTHON / DASH MODULES  
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as ff
from dash.dependencies import Input, Output, State
import pandas as pd
import json
from datetime import datetime as dt

# IMPORTING INTERNAL FILES
from dashboard_tabs import dashboard_downtime, dashboard_plan, dashboard_reference, dashboard_repair, dashboard_status, dashboard_r2
from generate_figure_module import *

app = dash.Dash(__name__)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>R2 / ГРЭ-7 </title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
server = app.server

# BASIC AUTHENTICATION
auth = dash_auth.BasicAuth(
    app,  
    [
        ['KAP', 'R2'],
        ['agaparov@kazatomprom.kz', 'K@P2019!']
    ]
)

# CODE TO SUPPRESS EXCEPTIONS
app.config.suppress_callback_exceptions = True

# [OPTIONAL] IN ORDER TO LOAD OFFLINE
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True


# GETTING DATA

full_list = lambda random_list, target_list: len(random_list) == len(target_list)

# dashboard_downtime
df_downtime = dashboard_downtime.df
areas_downtime = list(dashboard_downtime.areas)
types_downtime = list(dashboard_downtime.types)
colors_types = {k:v for k,v in zip(types_downtime, diff_20_colors[:len(types_downtime)])}
jsonified_types = json.dumps(types_downtime, ensure_ascii = False)

# dashboard_plan
df_dashplan_month_fact = dashboard_plan.df_month
df_dashplan_sng_fact = dashboard_plan.df_fact_since_jan2018
df_dashplan_month_planned = dashboard_plan.df_plan_dec2018
df_dashplan_year_planned = dashboard_plan.df_plan_2018

# dashboard_repair
df_repair = dashboard_repair.df
equipments_repair = list(dashboard_repair.equipments)

# dashboard_status
df_status = dashboard_status.df

# dashboard_r2
a_df = dashboard_r2.a_df
p_df = dashboard_r2.p_df
q_df = dashboard_r2.q_df
table_df = dashboard_r2.table_df


# -- PART 2: LAYOUT --  #
app.layout = html.Div([
    html.H1(children = 'ПРИБОРНАЯ ПАНЕЛЬ: ГРЭ-7', className = 'flex items-center bg-near-black gray ma0 pa2 h-auto flex-grow-0 f4'), 
    html.Div([
        dcc.Tabs(id = 'tabs', value = 'dashboard_r2', vertical = 'vertical', className = 'flex-grow-0 mr3 pa0 bg-mid-gray gray w-auto f7',
            children = [
                dcc.Tab(label = 'R2', value = 'dashboard_r2', className = 'flex pa0 h-auto', selected_className = 'css_tab_selected'),                
                dcc.Tab(label = 'ПРОСТОИ', value = 'dashboard_downtime', className = 'flex pa0 h-auto', selected_className = 'css_tab_selected'),
                dcc.Tab(label = 'ПЛАН', value = 'dashboard_plan', className = 'flex pa0 h-auto', selected_className = 'css_tab_selected'), 
                dcc.Tab(label = 'СПРАВКА', value = 'dashboard_reference', className = 'flex pa0 h-auto', selected_className = 'css_tab_selected'),
                dcc.Tab(label = 'БУР. УСТАНОВКИ', value = 'dashboard_status', className = 'flex pa0 h-auto', selected_className = 'css_tab_selected'),
                dcc.Tab(label = 'ТОиР', value = 'dashboard_repair', className = 'flex pa0 h-auto', selected_className = 'css_tab_selected')
            ], colors = {
                'border': '#111111',
                'primary': '#FFB700',
                'background': '#000000'
            }
        ),
        html.Div(id = 'tab-content', className = 'flex flex-grow-1 flex-shrink-1 ma0', style = {'width': '97vw'}),
    ], className = 'flex flex-grow-1 pa0'),

    # hidden divs inside the app that stores  diate values
    html.Div(id = 'intermediate-value-downtime', style = {'display': 'none'}),
    html.Div(id = 'intermediate-var-storage', children = jsonified_types, style = {'display': 'none'}),
    html.Div(id = 'intermediate-value-plan', style = {'display':'none'}),
    html.Div(id = 'intermediate-value-repair', style = {'display': 'none'})
 
], className = 'flex flex-column min-vh-100 ma0')

# -- PART 3: INTERACTION -- #

# callback to render tab content
@app.callback(Output('tab-content', 'children'), [Input('tabs', 'value')])
def render_tab_content(tab):
    if tab == 'dashboard_downtime':
        return dashboard_downtime.layout
    elif tab == 'dashboard_plan':
        return dashboard_plan.layout
    elif tab == 'dashboard_reference':
        return dashboard_reference.layout
    elif tab == 'dashboard_repair':
        return dashboard_repair.layout
    elif tab == 'dashboard_status':
        return dashboard_status.layout
    elif tab == 'dashboard_r2':
        return dashboard_r2.layout

# dashboard_downtime CALLBACKS

# callback for updating the dropdown values based on the clicked / unclicked data
@app.callback(Output('area-choice-downtime', 'value'), 
[Input('pie-area-downtime', 'clickData')],
[State('area-choice-downtime','value')]
)
def update_area_choice(clicked_area, chosen_area):
    clicked = clicked_area is not None
    full = full_list(chosen_area, areas_downtime)
    if clicked:
        new_area = clicked_area['points'][0]['customdata']
        if new_area not in chosen_area:
            chosen_area.append(new_area)
        elif full:
            chosen_area = [new_area]
        elif (new_area in chosen_area) and (len(chosen_area) == 1):
            chosen_area = areas_downtime
        elif (new_area in chosen_area):
            chosen_area.remove(new_area)
    return chosen_area

# callback for storing the information about clicked types of downtime (to enable unclick functionality)
@app.callback(Output('intermediate-var-storage', 'children'), 
[Input('pie-type-downtime', 'clickData')],
[State('intermediate-var-storage','children')]
)
def update_intermediate_var_storage(clicked_type, stored_data):
    clicked = clicked_type is not None
    types_list = json.loads(stored_data)
    full = full_list(types_list, types_downtime)
    if clicked:
        new_type = clicked_type['points'][0]['customdata']
        if new_type not in types_list:
            types_list.append(new_type)
        elif full:
            types_list = [new_type]
        elif (new_type in types_list) and (len(types_list) == 1):
            types_list = types_downtime
        elif new_type in types_list:
            types_list.remove(new_type)
    new_stored_data = json.dumps(types_list, ensure_ascii = False)
    return new_stored_data 

# callback for preparing the dataframes to be used by plots
@app.callback(Output('intermediate-value-downtime', 'children'), [
    Input('date-picker-range-downtime', 'start_date'),
    Input('date-picker-range-downtime','end_date'),
    Input('area-choice-downtime', 'value'),
    Input('intermediate-var-storage', 'children'),
])
def prepare_intermediate_value_downtime(start_date, end_date, areas_list, jsonified_types_list):
    # uploading json data
    types_list = json.loads(jsonified_types_list)
    
    # selecting dataframe for the specific date
    dff = df_downtime[start_date:end_date]
    
    # creating the copy of cleaned full dataframe
    dff_area = dff
    
    # implementing the area filtering
    dff = dff[dff["Участок"].isin(areas_list)]
    
    # defining variables for convenience
    time_spent = dashboard_downtime.time_spent
    key_metric_type = dashboard_downtime.key_metric_type
    key_metric_area = dashboard_downtime.key_metric_area
    key_metric_drilling = dashboard_downtime.key_metric_drilling
    
    # creating the copy of dataframe, filtered by area
    dff_type = dff
    
    # filtering dataframes based on the clicked type
    if len(types_list):
        dff_area = dff_area[dff_area[key_metric_type].isin(types_list)]
        dff = dff[dff[key_metric_type].isin(types_list)]
    
    # creating aggregated dataframes
    dff_type = dff_type.groupby(key_metric_type)[time_spent].sum().reset_index()
    dff_area = dff_area.groupby(key_metric_area)[time_spent].sum().reset_index()
    dff_dynamics = dff.groupby(dff.index)[time_spent].sum().reset_index()
    dff_drilling = dff.groupby([key_metric_drilling, key_metric_type])[time_spent].sum().reset_index()
    dff_drilling = dff_drilling.pivot(index = key_metric_drilling, columns = key_metric_type, values = time_spent)
    
    # sorting dataframes
    dff_type.sort_values(time_spent, ascending = False, inplace = True)
    dff_type = dff_type.reset_index(drop = True)
    dff_area.sort_values(time_spent, ascending = False, inplace = True)
    dff_area = dff_area.reset_index(drop = True)
    dff_drilling['ВСЕГО'] = dff_drilling.sum(axis = 1)
    dff_drilling.sort_values("ВСЕГО", ascending = False, inplace = True)

    # creating additional rows and columns [total percentage]
    total_by_type = dff_type[time_spent].sum()
    dff_type = dff_type.append({key_metric_type: 'ВСЕГО', time_spent: total_by_type}, ignore_index = True)
    dff_type['%'] = dff_type[time_spent] / total_by_type * 100
    dff_type['%'] = dff_type['%'].map('{:,.1f}%'.format)
    if full_list(types_list, types_downtime):
        dff_type['pull'] = 0
    elif len(types_list):
        dff_type['pull'] = (dff_type[key_metric_type].isin(types_list)) * 0.1
    else:
        dff_type['pull'] = 0.1

    total_by_area = dff_area[time_spent].sum()
    dff_area = dff_area.append({key_metric_area: 'ВСЕГО', time_spent: total_by_area}, ignore_index = True)
    dff_area['%'] = dff_area[time_spent] / total_by_area * 100
    dff_area['%'] = dff_area['%'].map('{:,.1f}%'.format)
    if full_list(areas_list, areas_downtime):
        dff_area['pull'] = 0
    elif len(areas_list):
        dff_area['pull'] = (dff_area[key_metric_area].isin(areas_list)) * 0.1
    else:
        dff_area['pull'] = 0.1

    # preparing dataframes for export
    datasets_downtime = {
        'dff_type': dff_type.to_json(orient = 'split', date_format = 'iso'),
        'dff_area': dff_area.to_json(orient = 'split', date_format = 'iso'),
        'dff_dynamics': dff_dynamics.to_json(orient = 'split', date_format = 'iso'),
        'dff_drilling': dff_drilling.to_json(orient = 'split', date_format = 'iso')
    }
    return json.dumps(datasets_downtime)

# generating table and pie - type of downtime
@app.callback(Output('table-type-downtime', 'figure'), [
    Input('intermediate-value-downtime', 'children')
])
def update_table_type_downtime(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_type'], orient = 'split')

    metric_type = dashboard_downtime.key_metric_type
    metric_time = dashboard_downtime.time_spent

    headers = ['Тип простоя', "Затрачено времени, [час]", "%"]
    values = [dff[metric_type], dff[metric_time], dff['%']]
    return generate_go_table(dff, headers, values)

@app.callback(Output('pie-type-downtime', 'figure'), [
    Input('intermediate-value-downtime', 'children'),
])
def update_pie_type_downtime(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_type'], orient = 'split')
    dff = dff[:-1]
    values_column = dashboard_downtime.time_spent
    labels_column = dashboard_downtime.key_metric_type
    colors = [colors_types[key] for key in dff[labels_column]]
    return generate_pie(dff, values_column, labels_column, colors)

# generating table and pie - area of downtime
@app.callback(Output('table-area-downtime', 'figure'), [
    Input('intermediate-value-downtime', 'children')
])
def update_table_area_downtime(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_area'], orient = 'split')

    metric_area = dashboard_downtime.key_metric_area
    metric_time = dashboard_downtime.time_spent

    headers = ['Участок', "Затрачено времени, [час]", "%"]
    values = [dff[metric_area], dff[metric_time], dff['%']]

    return generate_go_table(dff, headers, values)


@app.callback(Output('pie-area-downtime', 'figure'), [
    Input('intermediate-value-downtime', 'children')
])
def update_pie_area_downtime(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_area'], orient = 'split')
    dff = dff[:-1]
    values_column = dashboard_downtime.time_spent
    labels_column = dashboard_downtime.key_metric_area
    return generate_pie(dff, values_column, labels_column, seaborn_deep_colors[:len(dff.index)])

# generating line - downtime dynamics within time period
@app.callback(Output('line-dynamics-downtime', 'figure'), [
    Input('intermediate-value-downtime', 'children')
])
def update_line_dynamics_downtime(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_dynamics'], orient = 'split')
    x_column = 'Дата'
    y_column = dashboard_downtime.time_spent
    return generate_line(dff, x_column, y_column)

# generating stacked bar - downtime per drilling rig
@app.callback(Output('stacked-bar-drilling-downtime', 'figure'), [
    Input('intermediate-value-downtime', 'children')
])
def update_stacked_bar_drilling_downtime(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_drilling'], orient = 'split')
    dff.drop("ВСЕГО", axis = 1, inplace = True)
    y_columns = dff.columns
    colors = [colors_types[key] for key in y_columns]
    return generate_bar_stacked(dff,y_columns, colors)

# dashboard_plan CALLBACKS

# callback to update intermediate value 
@app.callback(Output('intermediate-value-plan', 'children'),[
    Input('date-picker-range-plan', 'start_date'),
    Input('date-picker-range-plan', 'end_date'),
])
def prepare_intermediate_value_plan(start_date, end_date):
    dff = df_dashplan_month_fact[start_date:end_date]
    dff = dff.groupby('Участок').sum().reset_index()

    # creating the monthly dataframe
    dff_dashplan_month = pd.merge(dff, df_dashplan_month_planned, on = 'Участок')
    dff_dashplan_month['Факт всего'] = dff_dashplan_month['Прочие_факт_дек2018'] + dff_dashplan_month['Технология_факт_дек2018']
    dff_dashplan_month.rename(columns = lambda name: name.replace('_дек2018', ''), inplace = True)

    
    # creating the yearly dataframe
    dff_dashplan_year = pd.merge(dff, df_dashplan_sng_fact, on = 'Участок')
    dff_dashplan_year['Технология_факт'] = dff_dashplan_year['Технология_факт_дек2018']+dff_dashplan_year['Технология_факт_снг']
    dff_dashplan_year['Прочие_факт'] = dff_dashplan_year['Прочие_факт_дек2018']+dff_dashplan_year['Прочие_факт_снг']
    dff_dashplan_year['Факт всего'] = dff_dashplan_year['Технология_факт']+dff_dashplan_year['Прочие_факт']
    dff_dashplan_year.drop(["Прочие_факт_дек2018", "Технология_факт_дек2018", "Прочие_факт_снг", "Технология_факт_снг"], axis = 1, inplace = True)
    dff_dashplan_year = dff_dashplan_year.merge(df_dashplan_year_planned, on = "Участок")
    dff_dashplan_year.rename(columns = lambda name: name.replace("_2018", ""), inplace = True)

    # adding total numbers for both dataframes
    total_monthly = pd.DataFrame({
        "Участок": ["ВСЕГО"],
        "Прочие_факт": [dff_dashplan_month['Прочие_факт'].sum()],
        "Технология_факт": [dff_dashplan_month["Технология_факт"].sum()],
        "План всего": [dff_dashplan_month['План всего'].sum()],
        "Прочие_план": [dff_dashplan_month['Прочие_план'].sum()],
        "Технология_план": [dff_dashplan_month['Технология_план'].sum()],
        "Факт всего": [dff_dashplan_month['Факт всего'].sum()]
    })

    total_annual = pd.DataFrame({
        "Участок": ["ВСЕГО"],
        "Прочие_факт": [dff_dashplan_year['Прочие_факт'].sum()],
        "Технология_факт": [dff_dashplan_year["Технология_факт"].sum()],
        "План всего": [dff_dashplan_year['План всего'].sum()],
        "Прочие_план": [dff_dashplan_year['Прочие_план'].sum()],
        "Технология_план": [dff_dashplan_year['Технология_план'].sum()],
        "Факт всего": [dff_dashplan_year['Факт всего'].sum()]
    })

    dff_month_result = dff_dashplan_month.append(total_monthly, ignore_index = True)
    dff_year_result = dff_dashplan_year.append(total_annual, ignore_index = True)
    print(dff_month_result)
    print(dff_year_result)

    # preparing the jsonified data
    datasets_plan = {
        'dashplan_month': dff_month_result.to_json(orient = 'split', date_format = 'iso'),
        'dashplan_year': dff_year_result.to_json(orient = 'split', date_format = 'iso')
    }
    return json.dumps(datasets_plan)

# callback to update the total chart
@app.callback(Output('total-fact-plan', 'figure'), [
    Input('intermediate-value-plan', 'children'),
    Input('period-choice-plan', 'value')
])
def update_total_fact_plan(jsonified_prepared_data, period_choice):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets[period_choice], orient = 'split')
    dff.set_index("Участок", inplace = True)
    categories = ['Технология', 'Прочие', 'ВСЕГО']
    
    
    tech_completed = dff.loc["ВСЕГО", "Технология_факт"]
    others_completed = dff.loc["ВСЕГО", "Прочие_факт"]
    total_completed = dff.loc["ВСЕГО", "Факт всего"]
    completed = [tech_completed, others_completed, total_completed]

    tech_planned = dff.loc["ВСЕГО", "Технология_план"]
    others_planned = dff.loc["ВСЕГО", "Прочие_план"]
    total_planned = dff.loc["ВСЕГО","План всего"]
    planned = [tech_planned, others_planned, total_planned]

    title = {
        'dashplan_month': 'Период: последний месяц',
        'dashplan_year': "Период: с начала года"
    }

    names = ['План', 'Факт']

    return generate_bar_grouped(categories, planned, completed, names, title[period_choice])


# callback to update the area chart
@app.callback(Output('area-fact-plan', 'figure'), [
    Input('intermediate-value-plan', 'children'),
    Input('period-choice-plan', 'value'),
    Input('type-choice-plan', 'value')
])
def update_area_fact_plan(jsonified_prepared_data, period_choice, type_choice):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets[period_choice], orient = 'split')

    type_choices = {
        'total': ['Факт всего', "План всего"],
        'tech': ["Технология_факт", "Технология_план"],
        'others': ["Прочие_факт", "Прочие_план"]
    }

    title = {
        'dashplan_month': 'Период: последний месяц',
        'dashplan_year': "Период: с начала года"
    }
 
    fact_col = type_choices[type_choice][0]
    plan_col = type_choices[type_choice][1]

    dff['Процент выполнения'] = dff.apply(lambda row: -1 if row[plan_col] == 0 else round((row[fact_col] / row[plan_col])*100,1), axis = 1)
    dff.sort_values('Процент выполнения', ascending = False, inplace = True)
    dff['hover_text'] = dff.apply(lambda row: 'Факт / план = {} / {}'.format(row[fact_col], row[plan_col]), axis = 1)

    styling = {
        'hovertext': dff['hover_text'],
        'title': title[period_choice]
    }
    return generate_horizontal_bar(dff["Участок"], dff["Процент выполнения"], styling)

# dashboard_reference CALLBACKS

@app.callback(Output('table-plan-year-reference', 'figure'), [Input('area-choice-reference', 'value')])
def update_table_plan_total_reference(areas_list):
    dff = dashboard_reference.df_plan_2018
    dff = dff[dff['Участок'].isin(areas_list)]
    dff.set_index('Участок', inplace = True)
    dff.loc['ВСЕГО'] = dff.sum()
    dff = dff.reset_index()

    headers = []
    values = []

    for index, column in enumerate(dff.columns):
        headers.append(column)
        values.append(dff[column])

    return generate_go_table(dff, headers, values)

@app.callback(Output('table-plan-month-reference', 'figure'), [Input('area-choice-reference', 'value')])
def update_table_plan_month_reference(areas_list):
    dff = dashboard_reference.df_plan_dec2018
    dff = dff[dff['Участок'].isin(areas_list)]
    dff.set_index('Участок', inplace = True)
    dff.loc['ВСЕГО'] = dff.sum()
    dff = dff.reset_index()

    headers = []
    values = []

    for index, column in enumerate(dff.columns):
        headers.append(column)
        values.append(dff[column])

    return generate_go_table(dff, headers, values)

@app.callback(Output('table-plan-sng-reference', 'figure'), [Input('area-choice-reference', 'value')])
def update_table_plan_sng_reference(areas_list):
    dff = dashboard_reference.df_plan_since_jan2018
    dff = dff[dff['Участок'].isin(areas_list)]
    dff.set_index('Участок', inplace = True)
    dff.loc['ВСЕГО'] = dff.sum()
    dff = dff.reset_index()

    headers = []
    values = []

    for index, column in enumerate(dff.columns):
        headers.append(column)
        values.append(dff[column])

    return generate_go_table(dff, headers, values)
    
@app.callback(Output('table-fact-sng-reference', 'figure'), [Input('area-choice-reference', 'value')])
def update_table_fact_sng_reference(areas_list):
    dff = dashboard_reference.df_fact_since_jan2018
    dff = dff[dff['Участок'].isin(areas_list)]
    dff.set_index('Участок', inplace = True)
    dff.loc['ВСЕГО'] = dff.sum()
    dff = dff.reset_index()
    
    headers = []
    values = []

    for index, column in enumerate(dff.columns):
        headers.append(column)
        values.append(dff[column])

    return generate_go_table(dff, headers, values)


@app.callback(Output('table-fact-month-reference', 'figure'), [
    Input('date-picker-range-reference', 'start_date'), 
    Input('date-picker-range-reference', 'end_date'),
    Input('area-choice-reference', 'value')])
def update_table_fact_month_reference(start_date, end_date, areas_list):
    dff = dashboard_reference.df
    dff = dff[start_date:end_date]
    dff = dff[dff['Участок'].isin(areas_list)]
    dff = dff.groupby('Участок').sum().reset_index()
    dff.set_index('Участок', inplace = True)
    dff.loc['ВСЕГО'] = dff.sum()
    dff = dff.reset_index()
    
    headers = []
    values = []

    for index, column in enumerate(dff.columns):
        headers.append(column)
        values.append(dff[column])

    return generate_go_table(dff, headers, values)

# dashboard_repair CALLBACKS

# callback for updating the dropdown values based on the clicked / unclicked data
@app.callback(Output('equipment-choice-repair', 'value'), 
[Input('pie-type-repair', 'clickData')],
[State('equipment-choice-repair','value')]
)
def update_equipment_choice(clicked_equipment, chosen_equipment):
    clicked = clicked_equipment is not None
    full = full_list(chosen_equipment, equipments_repair)
    if clicked:
        new_equipment = clicked_equipment['points'][0]['customdata']
        if new_equipment not in chosen_equipment:
            chosen_equipment.append(new_equipment)
        elif full:
            chosen_equipment = [new_equipment]
        elif (new_equipment in chosen_equipment) and (len(chosen_equipment) == 1):
            chosen_equipment = equipments_repair
        elif (new_equipment in chosen_equipment):
            chosen_equipment.remove(new_equipment)
    return chosen_equipment

# callback to prepare dataframes for plots
@app.callback(Output('intermediate-value-repair', 'children'), [
    Input('date-picker-range-repair', 'start_date'),
    Input('date-picker-range-repair','end_date'),
    Input('equipment-choice-repair', 'value')
])
def prepare_intermediate_value_repair(start_date, end_date, equipments_list):
    # filtering dataframe based on date
    dff = df_repair[start_date:end_date]

    # defining variables for convenience
    time_spent = dashboard_repair.time_spent
    key_metric_type = dashboard_repair.key_metric_type
    key_metric_location = dashboard_repair.key_metric_location
    key_metric_id = dashboard_repair.key_metric_id
    key_metric_status = dashboard_repair.key_metric_status

    # implementing filter based on equipment list
    dff_type = dff
    
    if len(equipments_list):
        dff = dff[dff[key_metric_type].isin(equipments_list)]
    
    # creating dataframe for charts and tables
    dff_type = dff_type.groupby(key_metric_type)[time_spent].sum().reset_index()
    dff_location = dff.groupby(key_metric_location)[time_spent].sum().reset_index()
    dff_id = dff.groupby([key_metric_type, key_metric_id])[time_spent].sum().reset_index()
    dff_dynamics = dff.groupby(dff.index)[time_spent].sum().reset_index()
    dff_status = dff.groupby(key_metric_status)[time_spent].sum().reset_index()

    # dataframe for overview table in the layer 1
    current_equipment_list = dff[key_metric_id].unique()
    current_status_list = dff[key_metric_status].unique()
    count_per_status = {status: 0 for status in current_status_list}
    for equipment in current_equipment_list:
        status = dff[dff[key_metric_id] == equipment].iloc[-1][key_metric_status]
        count_per_status[status] += 1
    
    dff_stat = pd.DataFrame([count_per_status])
    total_num_of_equipment = dff_stat.sum(axis = 1)
    dff_stat.insert(loc = 0, column = 'Общее количество оборудования', value = total_num_of_equipment)
    dff_stat.insert(loc = 0, column = 'Статус', value = "№ оборуд.")

    # sorting dataframes
    dff_type.sort_values(time_spent, ascending = False, inplace = True)
    dff_type = dff_type.reset_index(drop = True)
    
    dff_location.sort_values(time_spent, ascending = False, inplace = True)
    dff_location = dff_location.reset_index(drop = True)

    dff_id.sort_values(time_spent, ascending = False, inplace = True)
    dff_id = dff_id.reset_index(drop = True)

    dff_status.sort_values(time_spent, ascending = False, inplace = True)
    dff_status = dff_status.reset_index(drop = True)
    
    # creating additional rows and columns
    total_by_location = dff_location[time_spent].sum()
    total_by_id = dff_id[time_spent].sum()
    total_by_status = dff_status[time_spent].sum()

    if full_list(equipments_list, equipments_repair):
        dff_type['pull'] = 0
    elif len(equipments_list):
        dff_type['pull'] = (dff_type[key_metric_type].isin(equipments_list)) * 0.1
    else:
        dff_type['pull'] = 0.1


    dff_location = dff_location.append({key_metric_location: 'ВСЕГО', time_spent: total_by_location}, ignore_index = True)
    dff_id = dff_id.append({key_metric_type: 'ВСЕГО', key_metric_id: '', time_spent: total_by_id}, ignore_index = True)
    dff_status = dff_status.append({key_metric_status: 'ВСЕГО', time_spent: total_by_status}, ignore_index = True)

    # preparing dataframes for export
    datasets_repair = {
        'dff_type': dff_type.to_json(orient = 'split', date_format = 'iso'),
        'dff_location': dff_location.to_json(orient = 'split', date_format = 'iso'),
        'dff_id': dff_id.to_json(orient = 'split', date_format = 'iso'),
        'dff_dynamics': dff_dynamics.to_json(orient = 'split', date_format = 'iso'),
        'dff_status': dff_status.to_json(orient = 'split', date_format = 'iso'),
        'dff_stat': dff_stat.to_json(orient = 'split', date_format = 'iso')
    }
    return json.dumps(datasets_repair)

# callback for pie chart
@app.callback(Output('pie-type-repair', 'figure'), [
    Input('intermediate-value-repair', 'children')
])
def update_pie_type_repair(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_type'], orient = 'split')
    values_column = dashboard_repair.time_spent
    labels_column = dashboard_repair.key_metric_type
    return generate_pie(dff, values_column, labels_column, seaborn_deep_colors[:len(dff)])

# callback for table per first location of repair
@app.callback(Output('table-location-repair', 'figure'), [
    Input('intermediate-value-repair', 'children')
])
def update_table_location_repair(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_location'], orient = 'split')

    time_spent = dashboard_repair.time_spent
    location = dashboard_repair.key_metric_location

    headers = ["Локация поломки", "Затрачено времени, [час]"]
    values = [dff[location], dff[time_spent]]

    return generate_go_table(dff, headers, values)

# callback for table per id of equipment
@app.callback(Output('table-equipment-repair', 'figure'), [
    Input('intermediate-value-repair', 'children')
])
def update_table_equipment_repair(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_id'], orient = 'split')
    
    time_spent = dashboard_repair.time_spent
    metric_type = dashboard_repair.key_metric_type
    metric_id = dashboard_repair.key_metric_id

    headers = ['Тип оборудования', "Бортовой номер", "Затрачено времени, [час]"]
    values = [dff[metric_type], dff[metric_id], dff[time_spent]]

    return generate_go_table(dff, headers, values)

# callback for line - repair dynamics within time period
@app.callback(Output('line-dynamics-repair', 'figure'), [
    Input('intermediate-value-repair', 'children')
])
def update_line_dynamics_repair(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_dynamics'], orient = 'split')
    x_column = 'Дата'
    y_column = dashboard_repair.time_spent
    return generate_line(dff, x_column, y_column)

# callback for waterfall per repair status within time period
@app.callback(Output('waterfall-status-repair', 'figure'), [
    Input('intermediate-value-repair', 'children')
])
def update_waterfall_status_repair(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_status'], orient = 'split')

    status = dashboard_repair.key_metric_status
    time_spent = dashboard_repair.time_spent

    categories = dff[status]
    values = dff[time_spent]

    base = [0]*len(values)
    for i in range(len(values)):
        base[i+1:-1] += values[i]
    return generate_waterfall(categories, base, values)

# callback for statistics overview table
@app.callback(Output('table-statistics-repair', 'figure'), [
    Input('intermediate-value-repair', 'children')
])
def update_table_statistics_repair(jsonified_prepared_data):
    datasets = json.loads(jsonified_prepared_data)
    dff = pd.read_json(datasets['dff_stat'], orient = 'split')

    headers = []
    values = []

    for index, column in enumerate(dff.columns):
        headers.append(column)
        values.append(dff[column])

    return generate_go_table(dff, headers, values)

# dashboard_status CALLBACKS

@app.callback(Output('table-overview-status', 'figure'), [
    Input('date-picker-range-status', 'start_date'),
    Input('date-picker-range-status', 'end_date'),
    Input('drillingrig-choice-status', 'value'),
    Input('job-choice-status', 'value')
])
def update_table_overview_status(start_date, end_date, drilling_rig, job):
    dff = df_status[start_date:end_date]
    job_choice = []
    if (job == "Скважина сооружена (пробурена)"):
        job_choice = ["21. Скважина сооружена", "9. Скважина пробурена"]
    elif (job == 'Скважина сооружена'):
        job_choice = ["21. Скважина сооружена"]
    elif (job == 'Скважина пробурена'):
        job_choice  = ["9. Скважина пробурена"]
    dff = dff[(dff['Номер буровой установки'] == drilling_rig) & (dff['Наименование выполненных работ'].isin(job_choice))]
    dff = dff.reset_index()
    dff.sort_values("Дата",  ascending = False, inplace = True)

    headers = []
    values = []

    for index, column in enumerate(dff.columns):
        headers.append(column)
        values.append(dff[column])

    return generate_go_table(dff, headers, values)


# R2 main callbacks (draft)


@app.callback(Output('A-r2', 'figure'), [Input('area-choice-r2', 'value')])
def update_availability_r2(areas_list):
    a_dff = a_df[a_df['Участок'].isin(areas_list)]
    return {
        'data': [
                go.Bar(
                    x = a_dff['Участок'],
                    y = a_dff[metric],
                    name = metric,
                    text = ['{} %'.format(value) for value in a_dff[metric]],
                    textposition = 'auto',
                ) for metric in ['КИО Факт', "КИО @Risk", "КТГ Факт", "КТГ @Risk"]
            ],
            'layout': { 
                'barmode': 'group',
                'margin': {'t': 35, 'r': 20, 'b': 20, 'l': 60},
                'hovermode': 'closest',
                'clickmode': 'select',
            }
    }

@app.callback(Output('P-r2', 'figure'), [Input('area-choice-r2', 'value')])
def update_productivity_r2(areas_list):
    p_dff = p_df[p_df['Участок'].isin(areas_list)]
    return {
        'data': [
                go.Bar(
                    x = p_dff['Участок'],
                    y = p_dff[metric],
                    name = metric,
                    text = ['{}'.format(value) for value in p_dff[metric]],
                    textposition = 'auto',
                ) for metric in ['Норма', "Факт", "@Risk", "Тех лимит"]
            ],
            'layout': { 
                'barmode': 'group',
                'margin': {'t': 35, 'r': 20, 'b': 20, 'l': 60},
                'hovermode': 'closest',
                'clickmode': 'select',
            }
    }

@app.callback(Output('Q-r2', 'figure'), [Input('area-choice-r2', 'value')])
def update_quality_r2(areas_list):
    q_dff = q_df[q_df['Участок'].isin(areas_list)]
    return {
        'data': [
                go.Bar(
                    x = q_dff['Участок'],
                    y = q_dff[metric],
                    name = metric,
                    text = ['{}'.format(value) for value in q_dff[metric]],
                    textposition = 'auto',
                ) for metric in ['Факт', "План @Risk", "Факт (Норма)", "План @Risk (Норма)"]
            ],
            'layout': { 
                'barmode': 'group',
                'margin': {'t': 35, 'r': 20, 'b': 20, 'l': 60},
                'hovermode': 'closest',
                'clickmode': 'select',
            }
    }

@app.callback(Output('table-area-stat-r2', 'figure'), [Input('area-choice-r2', 'value')])
def update_table_r2(areas_list):
    columns_list = ["Показатели"] + areas_list
    table_dff = table_df[columns_list]
    return {
        'data': [go.Table(
            header = dict(
                values = table_dff.columns,
                fill = dict(color = 'grey'),
                line = dict(color = '#506784'),
                font = dict(color = 'white'),
            ), 
            cells = dict(
                values = [table_dff[column] for column in table_dff.columns],
                align = ['left', 'center'],
                line = dict(color = '#506784'),
                font = dict(color = ['white', 'black']),
                fill = dict(color = [['#008000', '#008000', '#008000', '#4682B4', '#4682B4', '#4682B4', '#4682B4', '#A0522D','#A0522D','#A0522D']] +
                    [['#90EE90', '#90EE90', '#90EE90', '#ADD8E6', '#ADD8E6', '#ADD8E6', '#ADD8E6', '#F5DEB3','#F5DEB3','#F5DEB3']] * (len(table_dff.columns)-1)
                )
            )
        )],
        'layout': {
            'margin': {'t': 0, 'r': 0, 'b': 0, 'l': 0}
        }
    }

# Code to run the main app

if __name__ == '__main__':
    app.run_server(debug=True)