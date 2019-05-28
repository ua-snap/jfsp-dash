'''
Template for SNAP Dash apps.
'''

import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html as ddsih
import pandas as pd

app = dash.Dash(__name__)
# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = 'SNAP Dash Template'

plottype = dcc.Dropdown(
    id='plottype',
    options=[
        {'label': 'Annual Area Burned', 'value': 'AAB'},
        {'label': 'Cumulative Area Burned', 'value': 'CAB'},
        {'label': 'Vegetation', 'value': 'VEG'}
    ],
    value='AAB'
)
regions = dcc.Dropdown(
    id='region',
    options=[
        {'label': 'Northwestern Interior Forest LCC', 'value': 'Northwestern_Interior_Forest_LCC'},
        {'label': 'Western Alaska LCC', 'value': 'Western_Alaska_LCC'},
        {'label': 'AIEM Domain', 'value': 'AIEM_Domain'},
        {'label': 'Arctic LCC', 'value': 'Arctic_LCC'},
        {'label': 'North Pacific LCC', 'value': 'North_Pacific_LCC'}
    ],
    value='AIEM_Domain'
)

gcms = dcc.Dropdown(
    id='gcm',
    options=[
        {'label': 'GFDL-CM3', 'value': 'GFDL-CM3'},
        {'label': 'GISS-E2-R', 'value': 'GISS-E2-R'},
        {'label': 'IPSL-CM5A-LR', 'value': 'IPSL-CM5A-LR'},
        {'label': 'MRI-CGCM3', 'value': 'MRI-CGCM3'},
        {'label': 'NCAR-CCSM4', 'value': 'NCAR-CCSM4'}
    ],
    value='GFDL-CM3'
)
rcps = dcc.Dropdown(
    id='rcp',
    options=[
        {'label': 'RCP 4.5', 'value': 'rcp45'},
        {'label': 'RCP 6.0', 'value': 'rcp60'},
        {'label': 'RCP 8.5', 'value': 'rcp85'}
    ],
    value='rcp60'
)

reps = range(1,200)
replicates = dcc.Dropdown(
    id='replicate',
    options=[{'label':rep, 'value':rep} for rep in reps],
    value='1'
)
plot_field = html.Div(
    className='field',
    children=[
        html.Label('Plot Type', className='label'),
        html.Div(className='control', children=[plottype])
    ]
)
region_field = html.Div(
    className='field',
    children=[
        html.Label('Region', className='label'),
        html.Div(className='control', children=[regions])
    ]
)
gcm_field = html.Div(
    className='field',
    children=[
        html.Label('GCM', className='label'),
        html.Div(className='control', children=[gcms])
    ]
)
rcp_field = html.Div(
    className='field',
    children=[
        html.Label('Scenario', className='label'),
        html.Div(className='control', children=[rcps])
    ]
)
replicates_field = html.Div(
    className='field',
    children=[
        html.Label('Replicates', className='label'),
        html.Div(className='control', children=[replicates])
    ]
)
radios = dcc.RadioItems(
    labelClassName='radio',
    className='control',
    options=[
        {'label': ' New York City ', 'value': 'NYC'},
        {'label': ' Montréal ', 'value': 'MTL'},
        {'label': ' San Francisco ', 'value': 'SF'}
    ],
    value='MTL'
)
form_elements_section = html.Div(
    className='section',
    children=[
        html.H2('ALFRESCO Post Processing', className='title is-2'),
        html.H4('These plots can be used for the calibration of ALFRESCO', className='subtitle is-4'),
        html.Div(
            className='columns',
            children=[
                html.Div(
                    className='column',
                    children=[
                        plot_field
                    ]
                ),
                html.Div(
                    className='column',
                    children=[
                        region_field
                    ]
                )
            ]
        ),
        html.Div(
            className='columns',
            children=[
                html.Div(
                    className='column',
                    children=[
                        gcm_field
                    ]
                ),
                html.Div(
                    className='column',
                    children=[
                        rcp_field
                    ]
                ),
                html.Div(
                    className='column',
                    children=[
                        replicates_field
                    ]
                )
            ]
        )
    ]
)

footer = html.Footer(
    className='footer',
    children=[
        html.Div(
            className='content has-text-centered',
            children=[
                dcc.Markdown("""
This is a page footer, where we'd put legal notes and other items.
                    """)
            ]
        )
    ]
)

graph_layout = html.Div(
    className='container',
    children=[
        dcc.Graph(id='alfplots')
    ]
)

app.layout = html.Div(
    className='container',
    children=[
        form_elements_section,
        graph_layout,
        footer
    ]
)

@app.callback(
    Output('alfplots', 'figure'),
    inputs=[
        Input('plottype', 'value'),
        Input('region', 'value'),
        Input('gcm', 'value'),
        Input('rcp', 'value'),
        Input('replicate', 'value')
    ]
)

def runplots(plottype, region, gcm, rcp, replicate):
    filename = 'data/AR5_2015_' + gcm + '_' + rcp + '.json'
    din = pd.read_json(filename)
    data = din['_default']
    hin = pd.read_json('data/AR5_2015_Observed.json')
    hist = hin['_default']

    figure = {}
    if (plottype == 'AAB'):
        xar = []
        yar = []
        hxar = []
        hyar = []
        for i in range(1,90):
            hxar.append(hist[i]['fire_year'])
            hyar.append(hist[i]['total_area_burned'][region])

        for i in range(1,data.size+1):
            if (int(data[i]['replicate']) == int(replicate)):
                xar.append(data[i]['fire_year'])
                yar.append(data[i]['total_area_burned'][region])
        layout = {
                'barmode': 'grouped',
                'title': 'AR5 ' + gcm + ' ' + rcp,
                'xaxis': {
                        'range': [1950,2010]
                }
        }
        figure = {
                'data': [{
                    'x': xar,
                    'y': yar,
                    'type': 'bar',
                    'marker': {
                        'color': '#999999'
                    },
                    'name': 'Replicate: ' + str(replicate)
                },
                {
                    'x': hxar,
                    'y': hyar,
                    'type': 'bar',
                    'marker': {
                        'color': '#ff6666'
                    },
                    'name': 'Historical '
                }]
            }
        figure['layout'] = layout
    elif (plottype == 'VEG'):
        xar = []
        yar = []
        vals = {}
        veg = {'Black Spruce': [], 'White Spruce': [], 'Deciduous': [], 'Graminoid Tundra': [], 'Shrub Tundra': [], 'Wetland Tundra': [], 'Temperate Rainforest': [], 'Barren lichen-moss': []}
        for i in range(1,data.size):
            if (int(data[i]['replicate']) == int(replicate)):
                vals[data[i]['av_year']] = data[i]['veg_counts'][region]
        running_total = 0
        for i in sorted(vals.keys()):
            if (int(i) >= 1950):
                xar.append(i)
                veg['Black Spruce'].append(vals[i]['Black Spruce'])
                veg['White Spruce'].append(vals[i]['White Spruce'])
                veg['Deciduous'].append(vals[i]['Deciduous'])
                veg['Graminoid Tundra'].append(vals[i]['Graminoid Tundra'])
                veg['Shrub Tundra'].append(vals[i]['Shrub Tundra'])
                    #veg['Wetland Tundra'].append(vals[i]['Wetland Tundra'])
                    #veg['Temperate Rainforest'].append(vals[i]['Temperate Rainforest'])
                    #veg['Barren lichen-moss'].append(vals[i]['Barren lichen-moss'])
        layout = {
                'title': 'AR5 ' + gcm + ' ' + rcp,
                'xaxis': {
                        'range': [1950,2010]
                },
                'hovermode': 'closest'
        }
        figure = { 'data': []
            }
        for i in veg:
            figure['data'].append({
                'x': xar,
                'y': veg[i],
                'type': 'line',
                'name': i
            })
        figure['layout'] = layout
    elif (plottype == 'CAB'):
        xar = []
        yar = []
        hxar = []
        hyar = []
        vals = {}
        hvals = {}
        for i in range(1,hist.size):
            hvals[hist[i]['fire_year']] = hist[i]['total_area_burned'][region]
        for i in range(1,data.size):
            if (int(data[i]['replicate']) == int(replicate)):
                vals[data[i]['fire_year']] = data[i]['total_area_burned'][region]
        running_total = 0
        for i in sorted(hvals.keys()):
            if (int(i) >= 1950):
                hxar.append(i)
                running_total += hvals[i]
                hyar.append(running_total)
        running_total = 0
        for i in sorted(vals.keys()):
            if (int(i) >= 1950):
                xar.append(i)
                running_total += vals[i]
                yar.append(running_total)
        layout = {
                'title': 'AR5 ' + gcm + ' ' + rcp,
                'xaxis': {
                        'range': [1950,2010]
                },

        }
        figure = {
                'data': [{
                    'x': xar,
                    'y': yar,
                    'type': 'line',
                    'marker': {
                        'color': '#999999'
                    },
                    'name': 'Replicate: ' + str(replicate)
                },
                {
                    'x': hxar,
                    'y': hyar,
                    'type': 'line',
                    'marker': {
                        'color': '#ff6666'
                    },
                    'name': 'Historical '
                }]
            }
        figure['layout'] = layout
    return figure

if __name__ == '__main__':
    application.run(debug=True, port=8080)
