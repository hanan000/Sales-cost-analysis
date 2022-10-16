import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_table as dt

sales = pd.read_csv('concat_all_files_.csv')

sales['Başlangıç Tarihi'] = pd.to_datetime(sales['Başlangıç Tarihi'])
sales['Yıl'] = sales['Başlangıç Tarihi'].dt.year
sales['Ay'] = sales['Başlangıç Tarihi'].dt.month_name()
print(sales['Yıl'].max())
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('Satış Maliyet Analizi', style={'margin-bottom': '4px', 'color': 'white'})

        ], className='one-third column', id = 'title1'),

        html.Div([
            html.P('Yıllar', className='fix_label', style= {'color': 'white'}),
            dcc.Slider(id = 'select_years',
                       included=False,
                       updatemode='drag',
                       tooltip={'always_visible': True},
                       min = 2019,
                       max = 2021,
                       step = 1,
                       value=2021,
                       marks={str(yr): str(yr) for yr in range(2019, 2021)},
                       className='dcc_compon'),

        ], className='one-half column', id = 'title2'),

html.Div([
            html.P('Lokasyon', className='fix_label', style= {'color': 'white'}),
            dcc.RadioItems(id = 'radio_items',
                       labelStyle = {'display': 'inline-block'},

                        value='Tüm Lokasyonlar',
                       options = [{'label': i, 'value': i} for i in sales['Lokasyon'].unique()],
                           style={'text-align': 'center', 'color': 'white'},
                       className='dcc_compon'),

        ], className='one-third column', id = 'title3')

    ], id='header', className='row flex-display', style={'margin-bottom': '25px'}),

 html.Div([
        html.Div([
dcc.RadioItems(id = 'radio_items1',
                       labelStyle = {'display': 'inline-block'},
                       value='Ürün Grup',
                       options = [{'label': 'Ürün Grup', 'value': 'Ürün Grup'},
                                  {'label': 'Üretici Adı', 'value': 'Üretici Adı'}],
                           style={'text-align': 'center', 'color': 'white'},
                       className='dcc_compon'),

            dcc.Graph(id = 'bar_chart_1', config={'displayModeBar': 'hover'},
                      style={'height': '350px'})

        ], className='create_container2 three columns', style={'height': '400px'}),

 html.Div([

            dcc.Graph(id = 'donut_chart', config={'displayModeBar': 'hover'},
                      style={'height': '350px'})

        ], className='create_container2 three columns', style={'height': '400px'}),

html.Div([

            dcc.Graph(id = 'line_chart', config={'displayModeBar': 'hover'},
                      style={'height': '350px'})

        ], className='create_container2 four columns', style={'height': '400px'}),

html.Div([

            html.Div(id = 'text1'),
            html.Div(id = 'text2'),
            html.Div(id = 'text3'),

        ], className='create_container2 two columns'),

    ], className='row flex-display'),

 html.Div([
        html.Div([
            dt.DataTable(id = 'my_datatable',
                         columns=[{'name': i, 'id': i} for i in
                                  sales.loc[:, ['Üretici Adı', 'Ürün Grubu', 'Ürün Açıklama',
                                  'Ürün Grup','Birim','Satış Miktarı','Satış Fiyatı','Satış Tutarı',
                                  'Birim Maliyeti','Maliyet Tutar','Kar Oranı','Kar Tutar','Tarih',
                                  'Lokasyon','Başlangıç Tarihi','Bitiş Tarihi','Maliyet Yöntemi','KDV Durumu']]],
                         virtualization=True,
                         style_cell={'textAlign': 'left',
                                     'min-width': '100px',
                                     'backgroundColor': '#1f2c56',
                                     'color': '#FEFEFE',
                                     'border-bottom': '0.01rem solid #19AAE1'},
                         style_header={'backgroundColor': '#1f2c56',
                                       'fontWeight': 'bold',
                                       'font': 'Lato, sans-serif',
                                       'color': 'orange',
                                       'border': '#1f2c56'},
                         style_as_list_view=True,
                         style_data={'styleOverflow': 'hidden', 'color': 'white'},
                         fixed_rows={'headers': True},
                         sort_action='native',
                         sort_mode='multi')


        ], className='create_container2 three columns'),


        html.Div([

dcc.RadioItems(id = 'radio_items2',
                       labelStyle = {'display': 'inline-block'},
                       value='Ürün Grubu',
                       options = [{'label': 'Ürün Grubu', 'value': 'Ürün Grubu'},
                                  {'label': 'Birim', 'value': 'Birim'}],
                           style={'text-align': 'center', 'color': 'white'},
                       className='dcc_compon'),

            dcc.Graph(id = 'bar_chart_2', config={'displayModeBar': 'hover'},
                      ),

        ], className='create_container2 three columns'),

html.Div([

            dcc.Graph(id = 'bubble_chart', config={'displayModeBar': 'hover'},
                      )

        ], className='create_container2 six columns'),

    ], className='row flex-display')

], id = 'mainContainer', style={'display': 'flex', 'flex-direction': 'column'})

@app.callback(Output('bar_chart_1', 'figure'),
              [Input('select_years','value')],
              [Input('radio_items','value')],
              [Input('radio_items1','value')])
def update_graph(select_years, radio_items, radio_items1):
    sales1 = sales.groupby(['Yıl', 'Ürün Grup', 'Lokasyon'])['Satış Tutarı'].sum().reset_index()
    sales2 = sales1[(sales1['Yıl'] == select_years) & (sales1['Lokasyon'] == radio_items)].sort_values(by = ['Satış Tutarı'], ascending = False).nlargest(5, columns = ['Satış Tutarı'])
    sales3 = sales.groupby(['Yıl', 'Üretici Adı', 'Lokasyon'])['Satış Tutarı'].sum().reset_index()
    sales4 = sales3[(sales3['Yıl'] == select_years) & (sales3['Lokasyon'] == radio_items)].sort_values(by=['Satış Tutarı'],ascending=False).nlargest(5, columns = ['Satış Tutarı'])

    if radio_items1 == 'Ürün Grup':


     return {
        'data': [
            go.Bar(
                x=sales2['Satış Tutarı'],
                y=sales2['Ürün Grup'],
                text = sales2['Satış Tutarı'],
                texttemplate= 'TL' + '%{text:,.2s}',
                textposition='auto',
                orientation= 'h',
                marker=dict(color='#19AAE1'),
                hoverinfo='text',
                hovertext=
                '<b>Yıl</b>: ' + sales2['Yıl'].astype(str) + '<br>' +
                '<b>Lokasyon</b>: ' + sales2['Lokasyon'].astype(str) + '<br>' +
                '<b>Ürün Grup</b>: ' + sales2['Ürün Grup'].astype(str) + '<br>' +
                '<b>Satış</b>: TL' + [f'{x:,.0f}' for x in sales2['Satış Tutarı']] + '<br>'

            ),

        ],


        'layout': go.Layout(
            title={'text': 'Satışlar' + ' ' + str((select_years)),
                   'y': 0.99,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 12},
            font=dict(family='sans-serif',
                      color='white',
                      size=15),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#010915',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(t = 40, r=0),
            xaxis=dict(title='<b></b>',
                       color = 'orange',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )),
            yaxis=dict(title='<b></b>',
                       color='orange',
                       autorange = 'reversed',
                       showline=False,
                       showgrid=False,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )
                       )


        )
    }

    elif radio_items1 == 'Üretici Adı':


     return {
        'data': [
            go.Bar(
                x=sales4['Satış Tutarı'],
                y=sales4['Üretici Adı'],
                text = sales4['Satış Tutarı'],
                texttemplate= 'TL' + '%{text:,.2s}',
                textposition='auto',
                orientation= 'h',
                marker=dict(color='#19AAE1'),
                hoverinfo='text',
                hovertext=
                '<b>Yıl</b>: ' + sales4['Yıl'].astype(str) + '<br>' +
                '<b>Lokasyon</b>: ' + sales4['Lokasyon'].astype(str) + '<br>' +
                '<b>Üretici Adı</b>: ' + sales4['Üretici Adı'].astype(str) + '<br>' +
                '<b>Satış</b>: TL' + [f'{x:,.0f}' for x in sales4['Satış Tutarı']] + '<br>'

            ),

        ],


        'layout': go.Layout(
            title={'text': 'Satışlar' + ' ' + str((select_years)),
                   'y': 0.99,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 12},
            font=dict(family='sans-serif',
                      color='white',
                      size=15),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#010915',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(t = 40, r=0),
            xaxis=dict(title='<b></b>',
                       color = 'orange',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )),
            yaxis=dict(title='<b></b>',
                       color='orange',
                       autorange = 'reversed',
                       showline=False,
                       showgrid=False,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )
                       )


        )
    }

@app.callback(Output('donut_chart', 'figure'),
              [Input('select_years','value')],
              [Input('radio_items','value')])
def update_graph(select_years, radio_items):
    sales5 = sales.groupby(['Yıl', 'Ürün Grubu', 'Lokasyon'])['Satış Tutarı'].sum().reset_index()
    sales_f = sales5[(sales5['Yıl'] == select_years) & (sales5['Lokasyon'] == ' Tüm Lokasyonlar') & (sales5['Ürün Grubu'] == 'GIDA')]['Satış Tutarı'].sum()
    sales_O = sales5[(sales5['Yıl'] == select_years) & (sales5['Lokasyon'] == ' Tüm Lokasyonlar') & (sales5['Ürün Grubu'] == 'GIDA DIŞI')]['Satış Tutarı'].sum()
    sales_T = sales5[(sales5['Yıl'] == select_years) & (sales5['Lokasyon'] == ' Tüm Lokasyonlar') & (sales5['Ürün Grubu'] == 'KOZMETIK')]['Satış Tutarı'].sum()
    colors = ['#30C9C7', '#7A45D1', 'orange']



    return {
            'data': [go.Pie(
                labels=['GIDA', 'GIDA DIŞI', 'KOZMETIK'],
                values=[sales_f, sales_O, sales_T],
                marker=dict(colors=colors),
                hoverinfo='label+value+percent',
                textinfo='label+value',
                texttemplate='%{label} <br>TL%{value:,.2f}',
                textposition='auto',
                textfont=dict(size=13),
                hole=.7,
                rotation=160,
                # insidetextorientation= 'radial'

            )],

            'layout': go.Layout(
                title={'text': 'satışlar' + ' ' + str((select_years)),
                       'y': 0.93,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                titlefont={'color': 'white',
                           'size': 15},
                font=dict(family='sans-serif',
                          color='white',
                          size=12),
                hovermode='closest',
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                legend={'orientation': 'h',
                        'bgcolor': '#1f2c56',
                        'xanchor': 'center', 'x': 0.5, 'y': -0.7}

            )
        }


@app.callback(Output('line_chart', 'figure'),
              [Input('select_years','value')],
              [Input('radio_items','value')])
def update_graph(select_years, radio_items):
    sales6 = sales.groupby(['Yıl', 'Ay', 'Lokasyon'])['Satış Tutarı'].sum().reset_index()
    sales7 = sales6[(sales6['Yıl'] == select_years) & (sales6['Lokasyon'] == radio_items)]



    return {
        'data': [
            go.Scatter(
                x=sales7['Ay'],
                y=sales7['Satış Tutarı'],
                text = sales7['Satış Tutarı'],
                texttemplate= 'TL' + '%{text:,.2s}',
                textposition='bottom left',
                mode='markers+lines+text',
                line=dict(width=3, color='orange'),
                marker=dict(color='#19AAE1', size=10, symbol='circle',
                            line=dict(color='#19AAE1', width=2)),
                hoverinfo='text',
                hovertext=
                '<b>Yıl</b>: ' + sales7['Yıl'].astype(str) + '<br>' +
                '<b>Ay</b>: ' + sales7['Ay'].astype(str) + '<br>' +
                '<b>Lokasyon</b>: ' + sales7['Lokasyon'].astype(str) + '<br>' +
                '<b>Satış</b>: TL' + [f'{x:,.0f}' for x in sales7['Satış Tutarı']] + '<br>'

            ),

        ],


        'layout': go.Layout(
            title={'text': 'satış Trende' + ' ' + str((select_years)),
                   'y': 0.99,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 12},
            font=dict(family='sans-serif',
                      color='white',
                      size=12),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#010915',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(t = 5, l = 0, r=0),
            xaxis=dict(title='<b></b>',
                       color = 'orange',
                       showline=True,
                       showgrid=False,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )),
            yaxis=dict(title='<b></b>',
                       color='orange',
                       showline=False,
                       showgrid=True,
                       showticklabels=False,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )
                       )


        )
    }
    
@app.callback(Output('text1', 'children'),
              [Input('select_years','value')])
def update_graph(select_years):
    sales8 = sales.groupby(['Yıl'])['Satış Tutarı'].sum().reset_index()
    current_year = sales8[(sales8['Yıl'] == select_years)]['Satış Tutarı'].sum()

    return [

        html.H6(children='Bu yıl',
                style={'textAlign': 'center',
                       'color': 'white'}),

        html.P('TL{0:,.2f}'.format(current_year),
               style={'textAlign': 'center',
                      'color': '#19AAE1',
                      'fontSize': 15,
                      'margin-top': '-10px'})

    ]
    
@app.callback(Output('text2', 'children'),
              [Input('select_years','value')])
def update_graph(select_years):
    sales10 = sales.groupby(['Yıl'])['Satış Tutarı'].sum().reset_index()
    sales10['PY'] = sales10['Satış Tutarı'].shift(1)
    previous_year = sales10[(sales10['Yıl'] == select_years)]['PY'].sum()

    return [

        html.H6(children='Geçen yıl',
                style={'textAlign': 'center',
                       'color': 'white'}),

        html.P('TL{0:,.2f}'.format(previous_year),
               style={'textAlign': 'center',
                      'color': '#19AAE1',
                      'fontSize': 15,
                      'margin-top': '-10px'})

    ]

@app.callback(Output('text3', 'children'),
              [Input('select_years','value')])
def update_graph(select_years):
    sales11 = sales.groupby(['Yıl'])['Satış Tutarı'].sum().reset_index()
    sales11['YOY Growth'] = sales11['Satış Tutarı'].pct_change()
    sales11['YOY Growth'] = sales11['YOY Growth'] * 100
    growth_year = sales11[(sales11['Yıl'] == select_years)]['YOY Growth'].sum()

    return [

        html.H6(children='Büyüme',
                style={'textAlign': 'center',
                       'color': 'white'}),

        html.P('{0:,.2f}%'.format(growth_year),
               style={'textAlign': 'center',
                      'color': '#19AAE1',
                      'fontSize': 15,
                      'margin-top': '-10px'})

    ]

@app.callback(Output('my_datatable', 'data'),
              [Input('select_years','value')],
              [Input('radio_items','value')])
def update_graph(select_years, radio_items):
    data_table = sales[(sales['Yıl'] == select_years) & (sales['Lokasyon'] == ' Tüm Lokasyonlar')]
    return data_table.to_dict('records')

@app.callback(Output('bar_chart_2', 'figure'),
              [Input('select_years','value')],
              [Input('radio_items','value')],
              [Input('radio_items2','value')])
def update_graph(select_years, radio_items, radio_items2):
    sales12 = sales.groupby(['Yıl', 'Ürün Grubu', 'Lokasyon'])['Satış Tutarı'].sum().reset_index()
    sales13 = sales12[(sales12['Yıl'] == select_years) & (sales12['Lokasyon'] == ' Tüm Lokasyonlar')].sort_values(by = ['Satış Tutarı'], ascending = False).nlargest(5, columns = ['Satış Tutarı'])
    sales14 = sales.groupby(['Yıl', 'Birim', 'Lokasyon'])['Satış Tutarı'].sum().reset_index()
    sales15 = sales14[(sales14['Yıl'] == select_years) & (sales14['Lokasyon'] == ' Tüm Lokasyonlar')].sort_values(by=['Satış Tutarı'],ascending=False).nlargest(5, columns = ['Satış Tutarı'])

    if radio_items2 == 'Ürün Grubu':


     return {
        'data': [
            go.Bar(
                x=sales13['Satış Tutarı'],
                y=sales13['Ürün Grubu'],
                text = sales13['Satış Tutarı'],
                texttemplate= 'TL' + '%{text:,.2s}',
                textposition='auto',
                orientation= 'h',
                marker=dict(color='#19AAE1'),
                hoverinfo='text',
                hovertext=
                '<b>Yıl</b>: ' + sales13['Yıl'].astype(str) + '<br>' +
                '<b>Lokasyon</b>: ' + sales13['Lokasyon'].astype(str) + '<br>' +
                '<b>Ürün Grubu</b>: ' + sales13['Ürün Grubu'].astype(str) + '<br>' +
                '<b>Satış</b>: TL' + [f'{x:,.0f}' for x in sales13['Satış Tutarı']] + '<br>'

            ),

        ],


        'layout': go.Layout(
            title={'text': 'Satışlar' + ' ' + str((select_years)),
                   'y': 0.99,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 12},
            font=dict(family='sans-serif',
                      color='white',
                      size=15),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#010915',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(t = 40, r=0),
            xaxis=dict(title='<b></b>',
                       color = 'orange',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )),
            yaxis=dict(title='<b></b>',
                       color='orange',
                       autorange = 'reversed',
                       showline=False,
                       showgrid=False,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )
                       )


        )
    }

    elif radio_items2 == 'Birim':


     return {
        'data': [
            go.Bar(
                x=sales15['Satış Tutarı'],
                y=sales15['Birim'],
                text = sales15['Satış Tutarı'],
                texttemplate= 'TL' + '%{text:,.2s}',
                textposition='auto',
                orientation= 'h',
                marker=dict(color='#19AAE1'),
                hoverinfo='text',
                hovertext=
                '<b>Year</b>: ' + sales15['Yıl'].astype(str) + '<br>' +
                '<b>Segment</b>: ' + sales15['Lokasyon'].astype(str) + '<br>' +
                '<b>City</b>: ' + sales15['Birim'].astype(str) + '<br>' +
                '<b>Sales</b>: TL' + [f'{x:,.0f}' for x in sales15['Satış Tutarı']] + '<br>'

            ),

        ],


        'layout': go.Layout(
            title={'text': 'Satışlar' + ' ' + str((select_years)),
                   'y': 0.99,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            titlefont={'color': 'white',
                       'size': 12},
            font=dict(family='sans-serif',
                      color='white',
                      size=15),
            hovermode='closest',
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            legend={'orientation': 'h',
                    'bgcolor': '#010915',
                    'xanchor': 'center', 'x': 0.5, 'y': -0.7},
            margin=dict(t = 40, r=0),
            xaxis=dict(title='<b></b>',
                       color = 'orange',
                       showline=True,
                       showgrid=True,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )),
            yaxis=dict(title='<b></b>',
                       color='orange',
                       autorange = 'reversed',
                       showline=False,
                       showgrid=False,
                       showticklabels=True,
                       linecolor='orange',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Aerial',
                           color='orange',
                           size=12
                       )
                       )


        )
    }

@app.callback(Output('bubble_chart', 'figure'),
                  [Input('select_years', 'value')],
                  [Input('radio_items', 'value')])
def update_graph(select_years, radio_items):
        sales16 = sales.groupby(['Yıl', 'Ay', 'Üretici Adı', 'Ürün Grubu'])['Satış Tutarı'].sum().reset_index()
        sales18 = sales16[(sales16['Yıl'] == select_years) & (sales16['Üretici Adı'] == 'SULTANLAR TIBET*')]

        return {
            'data': [
                go.Scatter(
                    x=sales18['Ay'],
                    y=sales18['Satış Tutarı'],
                    mode='markers',
                    line=dict(width=3, color='orange'),
                    marker=dict(color= sales18['Satış Tutarı'],
                                colorscale = 'HSV',
                                showscale = False,
                                size=sales18['Satış Tutarı'] / 250,
                                symbol='circle',
                                line=dict(color='MediumPurple', width=2)),
                    hoverinfo='text',
                    hovertext=
                    '<b>Yıl</b>: ' + sales18['Yıl'].astype(str) + '<br>' +
                    '<b>Ay</b>: ' + sales18['Ay'].astype(str) + '<br>' +
                    '<b>Lokasyon</b>: ' + sales18['Üretici Adı'].astype(str) + '<br>' +
                    '<b>Ürün Grubu</b>: ' + sales18['Ürün Grubu'].astype(str) + '<br>' +
                    #'<b>Birim</b>: ' + sales18['Ürün Grup'].astype(str) + '<br>' +
                    '<b>Satış Tutarı</b>: TL' + [f'{x:,.0f}' for x in sales18['Satış Tutarı']] + '<br>'

                ),

            ],

            'layout': go.Layout(
                title={'text': 'Satışlar (Üretici Adı)' + ' ' + str((select_years)),
                       'y': 0.99,
                       'x': 0.5,
                       'xanchor': 'center',
                       'yanchor': 'top'},
                titlefont={'color': 'white',
                           'size': 12},
                font=dict(family='sans-serif',
                          color='white',
                          size=12),
                hovermode='closest',
                paper_bgcolor='#1f2c56',
                plot_bgcolor='#1f2c56',
                legend={'orientation': 'h',
                        'bgcolor': '#010915',
                        'xanchor': 'center', 'x': 0.5, 'y': -0.7},
                margin=dict(t=40, l=0, r=0),
                xaxis=dict(title='<b></b>',
                           color='orange',
                           showline=True,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='orange',
                           linewidth=1,
                           ticks='outside',
                           tickfont=dict(
                               family='Aerial',
                               color='orange',
                               size=12
                           )),
                yaxis=dict(title='<b></b>',
                           color='orange',
                           showline=False,
                           showgrid=True,
                           showticklabels=False,
                           linecolor='orange',
                           linewidth=1,
                           ticks='outside',
                           tickfont=dict(
                               family='Aerial',
                               color='orange',
                               size=12
                           )
                           )

            )
        }

if __name__ == '__main__':
    app.run_server(debug=True)