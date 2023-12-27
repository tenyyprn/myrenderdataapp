import dash
# import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import dash_table
from dash import html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output
from tkinter import Tk, filedialog
from pandas import to_datetime
import datetime
from datetime import datetime

date_string = "12/03/2021"  # DD/MM/YYYY format
date_object = datetime.strptime(date_string, "%d/%m/%Y")

# app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])



# ファイル選択ダイアログを表示
root = Tk()
root.withdraw()
file_path = filedialog.askopenfilename()

# 選択されたExcelファイルからデータを読み込む
df = pd.read_excel(file_path)



# 必要なカラムを抽出
columns = ['JOB_NO','JOB_DATE', 'ORG_ID','CUSTOMER', 'SALES_AMT', 'BALANCE','FL','JOBTYPE','TEU','TTL_CM3','C_WT','DEST_PORT_CD','DEPT_PRT_CD','DEST_PRT_CD', 'ETD','CARRIER_NAME', 'CNTR20', 'CNTR40', 'CNTR40HQ']
# columns = ['JOB_DATE', 'ORG_ID','CUSTOMER', 'SALES_AMT', 'BALANCE','FL','TEU','TTL_CM3','C_WT','DEST_PORT_CD','DEPT_PRT_CD','DEST_PRT_CD','CARRIER_NAME']
# df['JOB_DATE'] = pd.to_datetime(df['JOB_DATE'])
df['JOB_DATE'] = pd.to_datetime(df['JOB_DATE'], dayfirst=True)
df = df[columns]

# ORG_IDがPE3, PE4, PE5, PE6, PE7のデータを除外
df = df[~df['ORG_ID'].isin(['PE3', 'PE4', 'PE5', 'PE6', 'PE7'])]


# 1. JOB_DATEで最も多いmonth/yearの組み合わせを取得
most_common_date = df['JOB_DATE'].dt.strftime('%Y-%m').value_counts().idxmax()

# 2. もっとも古いJOB_DATEともっとも新しいJOB_DATEを取得
oldest_date = df['JOB_DATE'].min().strftime('%Y-%m-%d')
newest_date = df['JOB_DATE'].max().strftime('%Y-%m-%d')



# ダッシュボードアプリを作成
app = dash.Dash(__name__)
server = app.server


# SIAM NISTRANS CO.,LTD.のデータを除外
df = df[df['CUSTOMER'] != 'SIAM NISTRANS CO.,LTD.']


##############################################################################
import plotly.express as px
filtered_df = df 

# データフレームから棒グラフを作成
bar_fig_sales = px.bar(filtered_df, x='CUSTOMER', y='SALES_AMT', title='Sales Amount by Customer')
bar_fig_balance = px.bar(filtered_df, x='CUSTOMER', y='BALANCE', title='Balance Amount by Customer')
pie_fig_sales = px.pie(filtered_df, names='CUSTOMER', values='SALES_AMT', title='Sales Amount by Customer')
pie_fig_balance = px.pie(filtered_df, names='CUSTOMER', values='BALANCE', title='Balance by Customer')

# ORG_IDがPE1のデータをフィルタリング
pe1_df = df[df['ORG_ID'] == 'PE1']

# DEST_PORT_CD別のTEUを集計
teu_by_dest_port = pe1_df.groupby('DEST_PORT_CD')['TEU'].sum().reset_index()

#########################################################################

# テーブルを作成
# import dash_table
from dash import dash_table
from dash import html


teu_table = dash_table.DataTable(
    id='teu-table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),  # 初期値を設定
    style_cell={
        'textAlign': 'right',  # テキストを右寄せに設定
        'font-family': 'Hiragino Maru Gothic Pro, sans-serif',  # フォントを丸ゴシックに設定
        'font-size': '12px'  # 文字の大きさを変更
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
        'font-family': 'Hiragino Maru Gothic Pro, sans-serif',  # ヘッダーのフォントも丸ゴシックに設定
        'font-size': '12px',  # ヘッダーの文字の大きさも変更
        'textAlign': 'right'  # ヘッダーのテキストも右寄せに設定
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        },
        {
            'if': {'column_id': 'DEST_PORT_CD'},  # DEST_PORT_CDカラムのみ指定
            'textAlign': 'left'  # テキストを左寄せに設定
        }
    ],
    style_table={
        'maxHeight': '50ex',
        'overflowY': 'scroll',
        'width': '100%',
        'minWidth': '100%',

    }
)


############################################
import plotly.graph_objects as go

# ETDに基づいてデータをグループ化し、各日付のTEUの合計を計算
teu_sum = df.groupby('ETD')['TEU'].sum().reset_index(name='TEU合計')

# 折れ線グラフを作成
fig = go.Figure(data=go.Scatter(x=teu_sum['ETD'], y=teu_sum['TEU合計'], mode='lines+markers'))

# グラフのレイアウトを設定
fig.update_layout(title='ETD毎のTEU', xaxis_title='ETD', yaxis_title='TEU合計')

# # グラフを表示
# fig.show()

############################################

##################################################

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import dash_table
from dash import html

app = dash.Dash(external_stylesheets=[dbc.themes.ZEPHYR])



##############################
# ここから下がスライダー
#
##############################


sidebar = html.Div(
        
    [
        
        html.Div(
        className="app-header",
        children=[
            html.Div('Plotly Dash-SNC', className="app-header--title")
        ]
    ),
        
        
        html.Div([
        dcc.Dropdown(
            id='customer-dropdown',
            options=[{'label': 'ALL', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df['CUSTOMER'].unique() if i != 'SIAM NISTRANS CO.,LTD.'],
            value='ALL',
            multi=True
        ),
        
# ##########################        

html.Div([
    html.Div('YEAR', style={'color': 'white'}),  # 'YEAR'というテキストを追加し、文字色を白に設定
    dcc.Checklist(
        id='year-checkbox',
        options=[
            {'label': ' 2021 ', 'value': '2021'},
            {'label': ' 2022 ', 'value': '2022'},
            {'label': ' 2023 ', 'value': '2023'},
            {'label': ' 2024 ', 'value': '2024'}
        ],
        value=['2023'],
        inline=True,
        style={'font-size': '18px', 'margin-right': '18px', 'color': 'white'}
    ),
    html.Button('Clear all', id='clear-year', style={'font-size': '14px', 'color': 'black'}),
], style={'display': 'inline-block', 'margin-bottom': '16px'}),
html.Div([
    html.Div('month', style={'color': 'white'}),  # 'month'というテキストを追加し、文字色を白に設定
    dcc.Checklist(
        id='month-checkbox',
        options=[
            {'label': ' 01 ', 'value': '01'},
            {'label': ' 02 ', 'value': '02'},
            {'label': ' 03 ', 'value': '03'},
            {'label': ' 04 ', 'value': '04'},
            {'label': ' 05 ', 'value': '05'},
            {'label': ' 06 ', 'value': '06'},
            {'label': ' 07 ', 'value': '07'},
            {'label': ' 08 ', 'value': '08'},
            {'label': ' 09 ', 'value': '09'},
            {'label': ' 10 ', 'value': '10'},
            {'label': ' 11 ', 'value': '11'},
            {'label': ' 12 ', 'value': '12'}
        ],
        value=[],
        inline=True,
        style={'font-size': '18px', 'margin-right': '18px', 'color': 'white'}
    ),
html.Button('Clear all', id='clear-month', style={'font-size': '14px', 'color': 'black'}),
], style={'display': 'inline-block', 'margin-bottom': '16px'}),
    html.Div([
        html.Div(f"最も多い月/年の組み合わせ: {most_common_date}", style={'color': 'white'}),
        html.Div(f"最も古いJOB_DATE: {oldest_date}", style={'color': 'white'}),
        html.Div(f"最も新しいJOB_DATE: {newest_date}", style={'color': 'white'}),
]),


#####################
        dcc.Dropdown(
            id='org-dropdown',
            options=[{'label': 'ALL', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df['ORG_ID'].unique()],
            value=['ALL', 'PE1'],
            multi=True
        ),
        
        dcc.Dropdown(
            id='carrier-dropdown',
            options=[{'label': 'ALL', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df['CARRIER_NAME'].dropna().unique()],
            value='ALL',
            multi=True
# )
        ),
        dcc.Dropdown(
            id='dest-port-dropdown',
            options=[{'label': 'ALL', 'value': 'ALL'}] + [{'label': i, 'value': i} for i in df['DEST_PRT_CD'].unique()],
            value='ALL',
            multi=True
        ),

        
        
        # html.Div([
        dcc.Checklist(
        id='fl-checkbox',
        options=[
            {'label': 'FCL', 'value': 'FCL'},
            {'label': 'LCL', 'value': 'LCL'},
            {'label': 'OTH', 'value': 'OTH'}
        ],
        inline=True,
        value=['FCL', 'LCL','OTH'],
        labelStyle={'color': 'white'}
        ),
        
        
        
        html.Div([
        dcc.DatePickerRange(
        id='date-picker-range',
        start_date_placeholder_text="Start Period",
        end_date_placeholder_text="End Period",
        calendar_orientation='vertical',
    ),
    html.Button('All Clear', id='all-clear-button', n_clicks=0)
    ]),
 
        
        dcc.Graph(id='pie-chart3',style={'fontSize': '10px'}),
        
        
        
        
        html.Div([
            # html.H3('TEU by DEST_PORT_CD for ORG_ID PE1'),
            html.H3('TEU by DEST_PORT_CD for ORG_ID PE1', style={'fontSize': '12px'}),
            
            html.Div(id='teu-table-container', children=teu_table),
        ],
        ),
        
    ]),

    ]
)


df['SALES_AMT'] = df['SALES_AMT'].astype(int)  # SALES_AMTを整数型に変換
df['BALANCE'] = df['BALANCE'].astype(int)  # BALANCEを整数型に変換
df['JOB_DATE'] = df['JOB_DATE'].dt.date  # JOB_DATEから時間を削除

#####################################################
#
# ここから下がコンテンツ
#  
###################################################


content = html.Div(
   
    [     
        
        
        
        html.Div(
        className="app-header",
        children=[
            html.Div('Plotly Dash　 version : main9.py', className="app-header--title")
        ]
    ),
        
        
        html.Div(
        children=html.Div([
            html.H1('Overview'),
    
        ])
    ),
        
        
        
        
        
        html.Div(
            dcc.Graph(
            id='map',
            style={'height': '65vh', 'width': '72vw'},
            config={'displayModeBar': False}
            ),
            style={'backgroundColor': '#1F5869', 'padding': '20px'}
        ),
        
        
        
        
        html.Div([
            
            html.Div(id='output-container-date-picker-range'),
            html.Div(id='fl-total'),          
            dcc.Graph(id='bar-chart-sales', figure=bar_fig_sales, style={'width': '40%', 'display': 'inline-block'}),
            dcc.Graph(id='pie-chart-sales', figure=pie_fig_sales, style={'width': '60%', 'display': 'inline-block'})
        ]),
        html.Div([
            dcc.Graph(id='bar-chart-balance', figure=bar_fig_balance, style={'width': '40%', 'display': 'inline-block'}),
            dcc.Graph(id='pie-chart-balance', figure=pie_fig_balance, style={'width': '60%', 'display': 'inline-block'})
        ]),

        
        html.Div([
            dcc.Graph(id='sales-balance-conbine', style={'display': 'inline-block', 'width': '100%'}),
                ]),
        
        
        html.Div([
            dcc.Graph(id='line-graph', style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(id='teu-graph', figure=fig, style={'display': 'inline-block', 'width': '50%'}),
        ]),
        
        html.Div([
            dcc.Graph(id='carrier-name-graph', style={'display': 'inline-block', 'width': '100%'}),
                ]),
        
        
        html.Div([
            dcc.Graph(id='monthly-profit-history-graph', style={'display': 'inline-block', 'width': '100%'}),
                ]),
        
        html.Div([
            dcc.Graph(id='monthly-ballance-history-graph', style={'display': 'inline-block', 'width': '100%'}),
                ]),
        
        
        html.Div([
            dcc.Graph(id='monthly-Teu-history-graph', style={'display': 'inline-block', 'width': '100%'}),
                ]),
        
        html.Div([
            dcc.Graph(id='monthly-Dest-history-graph', style={'display': 'inline-block', 'width': '100%'}),
                ]),
        
        html.Div([
            dcc.Graph(id='the-numbers-of-job', style={'display': 'inline-block', 'width': '100%'}),
                ]),
        
        
        # html.Div([
        #     dcc.Graph(id='sales-balance-conbine', style={'display': 'inline-block', 'width': '100%'}),
        #         ]),
        
        html.Div(id='table-container', children=[
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                style_cell={
                    'textAlign': 'left',
                    'font-family': 'Hiragino Maru Gothic Pro, sans-serif',  # フォントを丸ゴシックに設定
                    'font-size': '12px'  # 文字の大きさを変更
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'font-family': 'Hiragino Maru Gothic Pro, sans-serif',  # ヘッダーのフォントも丸ゴシックに設定
                    'font-size': '14px',  # ヘッダーの文字の大きさを変更
                },
        
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_table={
                    'maxHeight': '50ex',
                    'overflowY': 'scroll',
                    'width': '100%',
                    'minWidth': '100%',
                },
                    filter_action='native',  # フィルタリングを有効にする
                    sort_action='native'  # ソートを有効にする
            ),
        
        

        ])
    ]              
)

#############################################
##
##  HTML レイアウト構成
##
##############################################


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, style={'position': 'fixed', 'height': '100%', 'overflow': 'auto', 'background-color': '#1F5869'}),
                dbc.Col(content, width={'offset': 3}, style={'marginLeft': '25%', 'overflow': 'auto', 'height': '100vh', 'background-color': '#1F5869'})
            ]
        ),
    ],
    fluid=True
)


#####################
#
# app callback date picker
####################
@app.callback(
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    [Input('all-clear-button', 'n_clicks')]
)
def clear_datepicker(n_clicks):
    if n_clicks > 0:
        return None, None
    else:
        raise dash.exceptions.PreventUpdate

########################################
#  MAP LOCATION DATA
#######################################
import pandas as pd

# 初期データ
data = {
    'UNLOCODE': ['JPTYO', 'USNYC', 'GBLON', 'CNSHA', 'SGSIN'],
    'lat': [35.6762, 40.7128, 51.5074, 31.2304, 1.3521],
    'lon': [139.6503, -74.0060, -0.1278, 121.4737, 103.8198]
}

location_df = pd.DataFrame(data)

# 追加データ
additional_data_list = [
    {
        'UNLOCODE': ['JPYOK', 'JPOSA', 'JPNGO', 'JPUKB', 'JPHIJ', 'JPHTD', 'JPOTR', 'CNTAG', 'DEHAM', 'INPAV', 
                     'USLAX', 'USLGB', 'USTIW', 'CNSSH', 'IDJKT', 'JPSMZ', 'MXZLO', 'PHMNL', 'VNHPH', 'BDCGP', 
                     'CNDOX', 'CNHUA', 'CNSHK', 'CNTAG', 'HKHKG', 'INGHR', 'MMRGN', 'VNHCM', 'JPMOJ', 'USNYC', 
                     'JPMYJ', 'MYWSP', 'JPTMK', 'INNSA', 'CNSHK', 'SGSIN'],
        'lat': [35.4437, 34.6937, 35.1815, 33.5904, 34.3853, 33.8704, 43.1948, 38.2807, 53.5511, 21.1702, 
                34.0522, 33.7701, 47.2529, 31.2304, -6.2088, 35.4437, 19.1738, 14.5995, 20.8561, 23.8103, 
                22.5211, 30.5928, 22.3193, 38.2807, 22.3193, 16.8531, 16.8661, 10.7626, 33.9481, 40.7128, 
                35.6895, 3.139, 42.6350, 19.075, 22.3193, 1.3521],
        'lon': [139.6380, 135.5023, 136.9066, 130.4017, 132.4553, 132.4553, 141.002088, 117.2295, 9.9937, 72.8311, 
                -118.2437, -118.1937, -122.4443, 121.4737, 106.8456, 139.6380, -104.3332, 120.9842, 106.6839, 90.4125, 
                113.3824, 114.3055, 114.1694, 117.2295, 114.1694, 74.8599, 96.1951, 106.6602, 130.9417, -74.0060, 
                139.6917, 101.6869, 141.6033, 72.8777, 114.1694, 103.8198]
    }
]

# 追加データを既存のデータフレームに追加
for additional_data in additional_data_list:
    additional_df = pd.DataFrame(additional_data)
    location_df = pd.concat([location_df, additional_df], ignore_index=True)


################
## call back MAP 
##
#############
@app.callback(
    Output('map', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('carrier-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value')]
)
def update_map(selected_org, selected_customer, selected_carrier, selected_fl, selected_year, selected_month):
    filtered_df = df

########################################################
#エラーメッセージによると、update_map関数とupdate_pie_chart関数でエラーが発生しています。
# #これらの関数内でfiltered_df['JOB_DATE']とstart_date、end_dateを比較している部分が問題となっています。
#しかし、エラーメッセージによると、filtered_df['JOB_DATE']はすでに日付型（datetime.date）に変換されているようです。
# そのため、start_dateとend_dateがタイムスタンプ型（Timestamp）である可能性があります。
#これらの変数も日付型に変換することでエラーを解消できるはずです。以下に修正例を示します。
##########################################################
    # update_map関数とupdate_pie_chart関数内
#     if start_date is not None:
#         start_date = pd.to_datetime(start_date).date()
#     if end_date is not None:
#         end_date = pd.to_datetime(end_date).date()

#     if start_date is not None and end_date is not None:
#         filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
# ############################################################
    
    
    
    
    
    
    
    
    
    
    
#コードを確認しましたが、大きな問題は見つかりませんでした。ただし、日付の比較に関するエラーが以前発生していたため、
# 以下の部分を確認してみてください。
  
    if selected_year:
        start_date = pd.to_datetime(f'{selected_year[0]}-01-01')
        end_date = pd.to_datetime(f'{selected_year[0]}-12-31')
        year_filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
  #######################
  
  
#ここでは、start_dateとend_dateをタイムスタンプ型（Timestamp）として作成し、
# それらをfiltered_df['JOB_DATE']（おそらく日付型）と比較しています。
# これがエラーの原因である可能性があります。

# 以下のように修正してみてください。
    
    
    # if selected_year:
    #     start_date = pd.to_datetime(f'{selected_year[0]}-01-01').date()
    #     end_date = pd.to_datetime(f'{selected_year[0]}-12-31').date()
    #     year_filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
   
####################################################################################     
    else:
        year_filtered_df = filtered_df

    if selected_month:
        month_filtered_df = pd.DataFrame()
        for month in selected_month:
            month_start = f'{selected_year[0]}-{month}-01'
            month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
            temp_df = year_filtered_df[(year_filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (year_filtered_df['JOB_DATE'] <= month_end)]
            month_filtered_df = pd.concat([month_filtered_df, temp_df]) 
    else:
        month_filtered_df = year_filtered_df

    if selected_carrier != 'ALL':
        month_filtered_df = month_filtered_df[month_filtered_df['CARRIER_NAME'].isin(selected_carrier)]

    month_filtered_df = month_filtered_df[month_filtered_df['FL'].isin(selected_fl)]

    if 'PE1' in selected_org:
        pe1_df = month_filtered_df[month_filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby('DEST_PORT_CD').agg({'TEU': 'sum'}).reset_index()
    else:
        grouped_df = month_filtered_df.groupby('DEST_PORT_CD').agg({'TEU': 'sum'}).reset_index()

    grouped_df = pd.merge(grouped_df, location_df, how='left', left_on='DEST_PORT_CD', right_on='UNLOCODE')

    fig = px.scatter_geo(grouped_df, lat='lat', lon='lon', size='TEU', color='TEU',
                         hover_name='DEST_PORT_CD', projection='natural earth',
                         color_continuous_scale=px.colors.sequential.Plasma,
                         size_max=50,
                         fitbounds="locations")

    lat_thailand = 13.7563
    lon_thailand = 100.5018

    def calculate_linewidth(teu):
        return max(1, teu / 1000)

    for i in range(len(grouped_df)):
        dest_lat = grouped_df.loc[i, 'lat']
        dest_lon = grouped_df.loc[i, 'lon']
        teu = grouped_df.loc[i, 'TEU']
        fig.add_trace(go.Scattergeo(
            lat = [lat_thailand, dest_lat],
            lon = [lon_thailand, dest_lon],
            mode = 'lines',
            line = dict(width = calculate_linewidth(teu), color = 'blue'),
            showlegend=False,
        ))

    fig.update_layout(
        title_text = 'TEU Distribution Map',
        title_font = dict(size=24,color= 'white'),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
        showlegend = True,
    
    )

    fig.update_geos(
        landcolor="rgb(102, 179, 255)",
        oceancolor="rgb(173, 216, 230)",
        projection_rotation=dict(lon=-150),
    )
    
    return fig


# ＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃
###################
# コールバック関数内で棒グラフを生成します。
##################################


from datetime import datetime

date_string = "12/12/2023"
date = datetime.strptime(date_string, "%d/%m/%Y")


######################
# コールバック関数内で棒グラフとpie-chartを作成し、レイアウトに追加する SALESとBALANCEを表示させます。
#######################
@app.callback(
    Output('bar-chart-sales', 'figure'),
    Output('bar-chart-balance', 'figure'),
    Output('pie-chart-sales', 'figure'),
    Output('pie-chart-balance', 'figure'),
    [Input('customer-dropdown', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'), 
     Input('org-dropdown', 'value'),
     Input('carrier-dropdown', 'value'),
     Input('dest-port-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_charts(selected_customer, selected_year, selected_month, selected_org, selected_carrier, selected_dest_port, selected_fl, start_date, end_date):
    # 以下省略
    grouped_df = pd.DataFrame()  # grouped_dfを初期化
    filtered_df = df
    
    filtered_df['JOB_DATE'] = pd.to_datetime(filtered_df['JOB_DATE'])
    
    # if start_date is not None and end_date is not None:
    #     filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    # filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    # filtered_df['YEAR'] = pd.DatetimeIndex(filtered_df['ETD']).year


    if selected_customer and selected_customer != 'ALL':
        filtered_df = filtered_df[filtered_df['CUSTOMER'].isin(selected_customer)]
    
    if selected_year:
        start_date = pd.to_datetime(f'{selected_year[0]}-01-01')
        end_date = pd.to_datetime(f'{selected_year[0]}-12-31')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    else:
        # 年が選択されていない場合、全ての年を対象にする
        start_date = pd.to_datetime('1900-01-01')
        end_date = pd.to_datetime('2099-12-31')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]

    if selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]
    else:
        # 月が選択されていない場合、全ての月を対象にする
        start_date = pd.to_datetime('1900-01-01')
        end_date = pd.to_datetime('2099-12-31')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]

    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    if selected_org:
        filtered_df = filtered_df[filtered_df['ORG_ID'].isin(selected_org)] 
    

    sales_amt_by_customer = filtered_df.groupby('CUSTOMER')['SALES_AMT'].sum().reset_index()
    sales_amt_by_customer['SALES_AMT_PCT'] = sales_amt_by_customer['SALES_AMT'] / sales_amt_by_customer['SALES_AMT'].sum()

    balance_by_customer = filtered_df.groupby('CUSTOMER')['BALANCE'].sum().reset_index()
    balance_by_customer['BALANCE_PCT'] = balance_by_customer['BALANCE'] / balance_by_customer['BALANCE'].sum()

    # 3%未満の割合のカスタマーを'OTHERS'にまとめる
    sales_amt_by_customer['CUSTOMER'] = sales_amt_by_customer.apply(lambda row: row['CUSTOMER'] if row['SALES_AMT_PCT'] >= 0.02 else 'OTHERS', axis=1)
    balance_by_customer['CUSTOMER'] = balance_by_customer.apply(lambda row: row['CUSTOMER'] if row['BALANCE_PCT'] >= 0.02 else 'OTHERS', axis=1)

    # 再度合計を計算
    sales_amt_by_customer = sales_amt_by_customer.groupby('CUSTOMER')['SALES_AMT'].sum().reset_index()
    balance_by_customer = balance_by_customer.groupby('CUSTOMER')['BALANCE'].sum().reset_index()

    # 棒グラフを作成
    bar_fig_sales = px.bar(sales_amt_by_customer, x='CUSTOMER', y='SALES_AMT', title='Sales Amount by Customer')
    bar_fig_balance = px.bar(balance_by_customer, x='CUSTOMER', y='BALANCE', title='Balance by Customer')


    # pie-chartを作成
    pie_fig_sales = px.pie(sales_amt_by_customer, names='CUSTOMER', values='SALES_AMT', title='Sales Amount by Customer')
    pie_fig_balance = px.pie(balance_by_customer, names='CUSTOMER', values='BALANCE', title='Balance by Customer')

    bar_fig_sales.update_layout(
    plot_bgcolor = '#1F5869',
    paper_bgcolor = '#1F5869',
    title_font_color = 'white',
    xaxis=dict(tickfont=dict(color='white')),
    yaxis=dict(tickfont=dict(color='white'))
)

    bar_fig_balance.update_layout(
    plot_bgcolor = '#1F5869',
    paper_bgcolor = '#1F5869',
    title_font_color = 'white',
    xaxis=dict(tickfont=dict(color='white')),
    yaxis=dict(tickfont=dict(color='white'))
)

    pie_fig_sales.update_layout(
    plot_bgcolor = '#1F5869',
    paper_bgcolor = '#1F5869',
    title_font_color = 'white',
    legend=dict(title_font_color="white",font=dict(color="white")),
    xaxis=dict(tickfont=dict(color='white')),
    yaxis=dict(tickfont=dict(color='white'))
    
)

    pie_fig_balance.update_layout(
    plot_bgcolor = '#1F5869',
    paper_bgcolor = '#1F5869',
    title_font_color = 'white',
    legend=dict(title_font_color="white",font=dict(color="white")),
    xaxis=dict(tickfont=dict(color='white')),
    yaxis=dict(tickfont=dict(color='white'))
)
    
    return bar_fig_sales, bar_fig_balance, pie_fig_sales, pie_fig_balance

    
##########################################
# year-checkboxのコールバック
@app.callback(
    Output('year-checkbox', 'value'),
    [Input('clear-year', 'n_clicks')]
)
def clear_year_checkbox(n_clicks):
    if n_clicks:
        return []
    else:
        return dash.no_update

# month-checkboxのコールバック
@app.callback(
    Output('month-checkbox', 'value'),
    [Input('clear-month', 'n_clicks')]
)
def clear_month_checkbox(n_clicks):
    if n_clicks:
        return []
    else:
        return dash.no_update



#########################################
#  call back : fl-total
#
#######################################
#########################################

# import pandas as pd
# from pandas import to_datetime

# @app.callback(
#     [Output('fl-total', 'children'),
#      Output('table', 'data'),  # 'children'を'data'に変更
#      Output('customer-dropdown', 'value'),
#      Output('org-dropdown', 'value'),
#      Output('carrier-dropdown', 'value'),
#      Output('dest-port-dropdown', 'value')],
#     [Input('customer-dropdown', 'value'),
#      Input('org-dropdown', 'value'),
#      Input('carrier-dropdown', 'value'),
#      Input('dest-port-dropdown', 'value'),
#      Input('fl-checkbox', 'value'),
#      Input('date-picker-range', 'start_date'),
#      Input('date-picker-range', 'end_date')]
# )



# def update_fl_total_and_table(selected_customer, selected_org, selected_carrier, selected_dest_port, selected_fl, start_date, end_date):
#     filtered_df = df

#     # 日付範囲に基づいてデータフレームをフィルタリング
#     if start_date is not None and end_date is not None:
#         start_date = to_datetime(start_date)
#         end_date = to_datetime(end_date)
#         filtered_df = filtered_df[(to_datetime(filtered_df['JOB_DATE']) >= start_date) & (to_datetime(filtered_df['JOB_DATE']) <= end_date)]
    
#     # 以下のコードはそのままです...
# # def update_fl_total_and_table(selected_customer, selected_org, selected_carrier, selected_dest_port, selected_fl, start_date, end_date):
# #     filtered_df = df

#     # # 日付範囲に基づいてデータフレームをフィルタリング
#     # if start_date is not None and end_date is not None:
#     #     filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
#     if selected_customer != 'ALL':
#         filtered_df = filtered_df[filtered_df['CUSTOMER'].isin(selected_customer)]
#     if selected_org != 'ALL':
#         filtered_df = filtered_df[filtered_df['ORG_ID'].isin(selected_org)]
#     if selected_carrier != 'ALL':
#         filtered_df = filtered_df[filtered_df['CARRIER_NAME'].isin(selected_carrier)]
#     if selected_dest_port != 'ALL':
#         filtered_df = filtered_df[filtered_df['DEST_PRT_CD'].isin(selected_dest_port)]
        
#     fl_total = filtered_df[filtered_df['FL'].isin(selected_fl)].groupby('FL')['FL'].count()
#     filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]
#     teu_total = filtered_df['TEU'].sum()
#     ttl_cm3_total = "{:,}".format(int(filtered_df['TTL_CM3'].sum()))  # カンマ区切りに変換
#     sales_amt_total = "{:,}".format(int(filtered_df['SALES_AMT'].sum()))  # カンマ区切りに変換
#     balance_total = "{:,}".format(int(filtered_df['BALANCE'].sum()))  # カンマ区切りに変換

#     cntr20_total = "{:,}".format(filtered_df['CNTR20'].sum())  # カンマ区切りに変換
#     cntr40_total = "{:,}".format(filtered_df['CNTR40'].sum())  # カンマ区切りに変換
#     cntr40hq_total = "{:,}".format(filtered_df['CNTR40HQ'].sum())  # カンマ区切りに変換


#     return (html.Div([

#     html.Table([
#     html.Tr([
#         html.Td(f"FCL: {fl_total.get('FCL', 0)}", style={'border': '2px solid white', 'background-color': '#0075a4'}),  # 背景色を赤に設定
#         html.Td(f"LCL: {fl_total.get('LCL', 0)}", style={'border': '2px solid white', 'background-color': '#008bad'}),  # 背景色を赤に設定
#         html.Td(f"OTH: {fl_total.get('OTH', 0)}", style={'border': '2px solid white', 'background-color': '#009fa1'}),  # 背景色を赤に設定
#         html.Td(f"TTL_CM3: {ttl_cm3_total}", style={'border': '2px solid white', 'background-color': '#00af82'}),  # 背景色を赤に設定
#     ]),
#     html.Tr([
#         html.Td(f"TEU: {teu_total}", style={'border': '2px solid white', 'background-color': '#0075a4'}),  # 背景色を緑に設定
#         html.Td(f"CNTR20: {cntr20_total}", style={'border': '2px solid white', 'background-color': '#008bad'}),  # 背景色を緑に設定
#         html.Td(f"CNTR40: {cntr40_total}", style={'border': '2px solid white', 'background-color': '#009fa1'}),  # 背景色を緑に設定
#         html.Td(f"CNTR40HQ: {cntr40hq_total}", style={'border': '2px solid white', 'background-color': '#00af82'}),  # 背景色を緑に設定
    
#     ]),
#     html.Tr([
#         html.Td("SALES_AMT:", style={'border': '2px solid white', 'background-color': '#0075a4', 'width': '50%'}),  # 背景色を青に設定
#         html.Td(f"{sales_amt_total}", style={'border': '2px solid white', 'background-color': '#0075a4', 'width': '50%'}),  # 背景色を青に設定
#         html.Td("BALANCE:", style={'border': '2px solid white', 'background-color': '#009fa1', 'width': '50%'}),  # 背景色を青に設定
#         html.Td(f"{balance_total}", style={'border': '2px solid white', 'background-color': '#009fa1', 'width': '50%'}),  # 背景色を青に設定
#     ])
# ], style={'border': '2px solid white', 'padding': '10px', 'color': 'white', 'font-size': '22px', 'width': '100%', 'table-layout': 'fixed', 'border-collapse': 'collapse'}),
# ]), filtered_df.to_dict('records'), selected_customer, selected_org, selected_carrier, selected_dest_port)
    














# import pandas as pd
# from pandas import to_datetime

# ############################
# @app.callback(
#     [Output('fl-total', 'children')],
#      Output('table', 'data'),
#      Output('customer-dropdown', 'value'),
#      Output('org-dropdown', 'value'),
#      Output('carrier-dropdown', 'value'),
#      Output('dest-port-dropdown', 'value')],
#     [Input('customer-dropdown', 'value'),
#      Input('org-dropdown', 'value'),
#      Input('carrier-dropdown', 'value'),
#      Input('dest-port-dropdown', 'value'),
#      Input('fl-checkbox', 'value'),
#      Input('year-checkbox', 'value'),  # 新たに追加
#      Input('month-checkbox', 'value')]  # 新たに追加
# )
# def update_fl_total(selected_customer, selected_org, selected_carrier, selected_dest_port, selected_fl, selected_year, selected_month):
#     grouped_df = pd.DataFrame()  # grouped_dfを初期化
#     filtered_df = df
#     df['JOB_DATE'] = pd.to_datetime(df['JOB_DATE'], format='%d/%m/%Y')
#     # 'JOB_DATE'列がdatetime.date型でない場合のみ、pd.to_datetimeを適用
#     if not isinstance(df['JOB_DATE'].iloc[0], datetime.date):
#         # df['JOB_DATE'] = pd.to_datetime(df['JOB_DATE'], format='%d/%m/%Y', dayfirst=True)
#         df['JOB_DATE'] = pd.to_datetime(df['JOB_DATE'], format='%d/%m/%Y')

#     # 年と月に基づいてデータフレームをフィルタリング
#     if selected_year:
#         selected_year = [int(year) for year in selected_year]
#         filtered_df = filtered_df[filtered_df['JOB_DATE'].apply(lambda x: x.year).isin(selected_year)]
#     if selected_month:
#         selected_month = [int(month) for month in selected_month]
#         filtered_df = filtered_df[filtered_df['JOB_DATE'].apply(lambda x: x.month).isin(selected_month)]
        
#     # その他のフィルタリング条件に基づいてデータフレームをフィルタリング
#     if selected_customer != 'ALL':
#         filtered_df = filtered_df[filtered_df['CUSTOMER'].isin(selected_customer)]
#     if selected_org != 'ALL':
#         filtered_df = filtered_df[filtered_df['ORG_ID'].isin(selected_org)]
#     if selected_carrier != 'ALL':
#         filtered_df = filtered_df[filtered_df['CARRIER_NAME'].isin(selected_carrier)]
#     if selected_dest_port != 'ALL':
#         filtered_df = filtered_df[filtered_df['DEST_PRT_CD'].isin(selected_dest_port)]
#     filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

#     # 目的地のポートコードごとにTEU、売上額、バランス、総立方メートルを集計
#     grouped_df = filtered_df.groupby('DEST_PRT_CD').agg({'TEU': 'sum', 'SALES_AMT': 'sum', 'BALANCE': 'sum', 'TTL_CM3': 'sum'}).reset_index()

#     # 各列を整数に変換
#     for col in ['TEU', 'SALES_AMT', 'BALANCE', 'TTL_CM3']:
#         grouped_df[col] = grouped_df[col].fillna(0).astype(int)

#     # 各列の合計を計算
#     total_teu = grouped_df['TEU'].sum()
#     total_sales_amt = grouped_df['SALES_AMT'].sum()
#     total_balance = grouped_df['BALANCE'].sum()
#     total_ttl_cm3 = grouped_df['TTL_CM3'].sum()

#     # 合計行を追加
#     total_row = pd.DataFrame([['Total', total_teu, total_sales_amt, total_balance, total_ttl_cm3]], columns=['DEST_PRT_CD', 'TEU', 'SALES_AMT', 'BALANCE', 'TTL_CM3'])
#     grouped_df = pd.concat([grouped_df, total_row])

#     return (html.Div([
#         html.Table([
#             html.Tr([
#                 html.Td(f"FCL: {grouped_df.get('FCL', 0)}", style={'border': '2px solid white', 'background-color': '#0075a4'}),
#                 html.Td(f"LCL: {grouped_df.get('LCL', 0)}", style={'border': '2px solid white', 'background-color': '#008bad'}),
#                 html.Td(f"OTH: {grouped_df.get('OTH', 0)}", style={'border': '2px solid white', 'background-color': '#009fa1'}),
#                 html.Td(f"TTL_CM3: {total_ttl_cm3}", style={'border': '2px solid white', 'background-color': '#00af82'}),
#             ]),
#             html.Tr([
#                html.Td(f"TEU: {total_teu}", style={'border': '2px solid white', 'background-color': '#0075a4'}),
#                 html.Td(f"SALES_AMT: {total_sales_amt}", style={'border': '2px solid white', 'background-color': '#008bad'}),
#                 html.Td(f"BALANCE: {total_balance}", style={'border': '2px solid white', 'background-color': '#009fa1'}),
#                 html.Td(f"TTL_CM3: {total_ttl_cm3}", style={'border': '2px solid white', 'background-color': '#00af82'}),
#             ])
#         ], style={'border': '2px solid white', 'padding': '10px', 'color': 'white', 'font-size': '22px', 'width': '100%', 'table-layout': 'fixed', 'border-collapse': 'collapse'}),
#     # ]), grouped_df.to_dict('records'), selected_customer, selected_org, selected_carrier, selected_dest_port)
#     ]), grouped_df.to_dict('records'), selected_customer, selected_org, selected_carrier, selected_dest_port, None)
    
    

from datetime import datetime

date_string = "12/12/2023"
date = datetime.strptime(date_string, "%d/%m/%Y")
    
##########################
##  call back   teu-table
##
##
######################
@app.callback(
    [Output('teu-table', 'data'),
     Output('teu-table', 'columns')],
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),  # チェックリストの値を取得
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_table(selected_org, selected_customer, selected_fl,  selected_year, selected_month, start_date, end_date):  # selected_flを追加
    grouped_df = pd.DataFrame()  # grouped_dfを初期化
    filtered_df = df

    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['YEAR'] = pd.DatetimeIndex(filtered_df['ETD']).year

    if selected_year:
        start_date = pd.to_datetime(f'{selected_year[0]}-01-01')
        end_date = pd.to_datetime(f'{selected_year[0]}-12-31')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]

    if selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby('DEST_PORT_CD').agg({'TEU': 'sum'}).reset_index()


    # 日付範囲に基づいてデータフレームをフィルタリング
    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    # チェックリストに基づいてデータフレームをフィルタリング
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]  # 新たに追加

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']  # ここをfiltered_dfに変更
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby('DEST_PORT_CD').agg({'TEU': 'sum', 'SALES_AMT': 'sum', 'BALANCE': 'sum', 'TTL_CM3': 'sum'}).reset_index()  # TTL_CM3を追加

    
        # 各列を整数に変換
        for col in ['TEU', 'SALES_AMT', 'BALANCE', 'TTL_CM3']:  # TTL_CM3を追加
            grouped_df[col] = grouped_df[col].fillna(0).astype(int)

        # 各列の合計を計算
        total_teu = grouped_df['TEU'].sum()
        total_sales_amt = grouped_df['SALES_AMT'].sum()
        total_balance = grouped_df['BALANCE'].sum()
        total_ttl_cm3 = grouped_df['TTL_CM3'].sum()  # TTL_CM3の合計を計算

        # 合計行を追加
        total_row = pd.DataFrame([['Total', total_teu, total_sales_amt, total_balance, total_ttl_cm3]], columns=['DEST_PORT_CD', 'TEU', 'SALES_AMT', 'BALANCE', 'TTL_CM3'])  # total_ttl_cm3を追加
        grouped_df = pd.concat([grouped_df, total_row])

    columns = [{"name": i, "id": i} for i in grouped_df.columns]
    return grouped_df.to_dict('records'), columns





from datetime import datetime

date_string = "12/12/2023"
date = datetime.strptime(date_string, "%d/%m/%Y")
#########################################
##    call back pie-chart3
##    
###################################
import plotly.graph_objects as go


@app.callback(
    Output('pie-chart3', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),  # チェックリストの値を取得
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_pie_chart(selected_org, selected_customer, selected_fl, selected_year, selected_month, start_date, end_date):  # selected_flを追加
    grouped_df = pd.DataFrame()  # grouped_dfを初期化
    filtered_df = df


    ########################################################
#エラーメッセージによると、update_map関数とupdate_pie_chart関数でエラーが発生しています。
# #これらの関数内でfiltered_df['JOB_DATE']とstart_date、end_dateを比較している部分が問題となっています。
#しかし、エラーメッセージによると、filtered_df['JOB_DATE']はすでに日付型（datetime.date）に変換されているようです。
# そのため、start_dateとend_dateがタイムスタンプ型（Timestamp）である可能性があります。
#これらの変数も日付型に変換することでエラーを解消できるはずです。以下に修正例を示します。
##########################################################
    # update_map関数とupdate_pie_chart関数内
    if start_date is not None:
        start_date = pd.to_datetime(start_date).date()
    if end_date is not None:
        end_date = pd.to_datetime(end_date).date()

    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
############################################################
    

    # if start_date is not None and end_date is not None:
    #     filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['YEAR'] = pd.DatetimeIndex(filtered_df['JOB_DATE']).year

    if selected_year:
        start_date = pd.to_datetime(f'{selected_year[0]}-01-01')
        end_date = pd.to_datetime(f'{selected_year[0]}-12-31')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]

    if selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby('DEST_PORT_CD').agg({'TEU': 'sum'}).reset_index()




    # 日付範囲に基づいてデータフレームをフィルタリング
    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    # チェックリストに基づいてデータフレームをフィルタリング
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]  # 新たに追加

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']  # ここをfiltered_dfに変更
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby('DEST_PORT_CD').agg({'TEU': 'sum', 'SALES_AMT': 'sum', 'BALANCE': 'sum', 'TTL_CM3': 'sum'}).reset_index()  # TTL_CM3を追加

          # 各列を整数に変換
        for col in ['TEU', 'SALES_AMT', 'BALANCE', 'TTL_CM3']:  # TTL_CM3を追加
            grouped_df[col] = grouped_df[col].fillna(0).astype(int)


    # TEUの合計を計算
    total_teu = grouped_df['TEU'].sum()

    # TEUの割合を計算
    grouped_df['TEU_percentage'] = grouped_df['TEU'] / total_teu * 100

    # 3%以下の割合のものを"OTHERS"にまとめる
    others_df = grouped_df[grouped_df['TEU_percentage'] <= 3]
    others_teu = others_df['TEU'].sum()
    others = pd.DataFrame({'DEST_PORT_CD': ['OTHERS'], 'TEU': [others_teu]})
    grouped_df = grouped_df[grouped_df['TEU_percentage'] > 3]
    grouped_df = pd.concat([grouped_df, others])


    
    # Pie chart
    fig = go.Figure(data=[go.Pie(labels=grouped_df['DEST_PORT_CD'], values=grouped_df['TEU'], hole=.3)])
    fig.update_layout(
    # title_text='TEU by DEST_PORT_CD for ORG_ID PE1',
    title_text='',
    title_font=dict(
        family="Hiragino Maru Gothic Pro, sans-serif",  # タイトルのフォントを丸ゴシックに設定
        size=10,  # タイトルの文字の大きさを変更
        color="black",
  
    ),
    plot_bgcolor = '#1F5869',
    paper_bgcolor = '#1F5869',
    
    
    
    
    font=dict(
        family="Hiragino Maru Gothic Pro, sans-serif",  # フォントを丸ゴシックに設定
        size=10,
        color="white"
    ),
    
    
    legend=dict(
        orientation="h",  # 水平方向に凡例を配置
        yanchor="bottom",  # 凡例の下端を基準に位置を決定
        y=1.02,  # 凡例の位置（チャートの上端からの距離）
        xanchor="right",  # 凡例の右端を基準に位置を決定
        x=1,  # 凡例の位置（チャートの右端からの距離）
        font=dict(
            size=9,
            color="white"# 凡例のフォントサイズを10に設定
        ),
        

    )
)

    return fig




from datetime import datetime

date_string = "12/12/2023"
date = datetime.strptime(date_string, "%d/%m/%Y")
###########################################
##   call back  : ling-graph　　５番目のグラフ
##
#########################################
@app.callback(
    Output('line-graph', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
##################################






















def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    grouped_df = pd.DataFrame()
    filtered_df = df

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['YEAR'] = pd.DatetimeIndex(filtered_df['ETD']).year

    if selected_year and selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby('DEST_PORT_CD').agg({'TEU': 'sum'}).reset_index()
        
        if 'DEST_PORT_CD' in grouped_df.columns:
            fig = go.Figure(data=go.Bar(x=grouped_df['DEST_PORT_CD'], y=grouped_df['TEU']))
        else:
            fig = go.Figure(data=go.Bar(x=df['DEST_PORT_CD'], y=df['TEU']))

    fig = go.Figure(data=go.Bar(x=grouped_df['DEST_PORT_CD'], y=grouped_df['TEU']))

    fig.update_layout(
        title_text ='PE1: EXPORT DESTINATION',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )

    return fig



# ＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃
    
######################################
from dash.dependencies import Input, Output
import pandas as pd


#######################################
from datetime import datetime

date_string = "12/12/2023"
date = datetime.strptime(date_string, "%d/%m/%Y")
###########################################
##   call back  : teu-graph   6番目のグラフ
##
#########################################
# @app.callback(
#     Output('teu-graph', 'figure'),
#     [Input('org-dropdown', 'value'),
#      Input('customer-dropdown', 'value'),
#      Input('fl-checkbox', 'value'),
#      Input('year-checkbox', 'value'),
#      Input('month-checkbox', 'value'),
#      Input('dest-port-dropdown', 'value'),
#      Input('date-picker-range', 'start_date'),
#      Input('date-picker-range', 'end_date')]
# )    
# def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    
#         grouped_df = pd.DataFrame()
#         filtered_df = df

#         if start_date is not None and end_date is not None:
#             filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
#         filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

#         filtered_df['YEAR'] = pd.DatetimeIndex(filtered_df['ETD']).year

#         if selected_year:
#             start_date = pd.to_datetime(f'{selected_year[0]}-01-01')
#             end_date = pd.to_datetime(f'{selected_year[0]}-12-31')
#             filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]

#         if selected_month:
#             month_start = f'{selected_year[0]}-{selected_month[0]}-01'
#             month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
#             filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]
    
#     # ETDを日付形式に変換し、古い順に並べる
#         filtered_df['ETD'] = pd.to_datetime(filtered_df['ETD'])
#         filtered_df = filtered_df.sort_values('ETD')


#         if selected_customer != 'ALL':
#             filtered_df = filtered_df[filtered_df['CUSTOMER'].isin(selected_customer)]

#     # Create line graph
#     # fig = go.Figure(data=go.Scatter(x=filtered_df['ETD'], y=filtered_df['TEU'], mode='lines+markers'))

#         fig = go.Figure(data=go.Bar(x=filtered_df['ETD'], y=filtered_df['TEU']))



#     # Add title
#         fig.update_layout(
#             title_text ='PE1 : TEU PER ETD',
#             title_font = dict(size=24,color='white'),
#             legend=dict(title_font_color="white",font=dict(color="white")),
#             xaxis=dict(tickfont=dict(color='white')),
#             yaxis=dict(tickfont=dict(color='white')),
#             plot_bgcolor = '#1F5869',
#             paper_bgcolor = '#1F5869',)
    
#         return fig
#########################################
@app.callback(
    Output('teu-graph', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    
    grouped_df = pd.DataFrame()
    filtered_df = df

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['ETD'] = pd.to_datetime(filtered_df['ETD'])
    filtered_df['YEAR'] = filtered_df['ETD'].dt.year
    filtered_df['MONTH'] = filtered_df['ETD'].dt.month
    filtered_df['DAY'] = filtered_df['ETD'].dt.day

    if selected_year:
        start_date = pd.to_datetime(f'{selected_year[0]}-01-01')
        end_date = pd.to_datetime(f'{selected_year[0]}-12-31')
        filtered_df = filtered_df[(filtered_df['ETD'] >= start_date) & (filtered_df['ETD'] <= end_date)]

    if selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['ETD'] >= pd.to_datetime(month_start)) & (filtered_df['ETD'] <= month_end)]
    
    if selected_customer != 'ALL':
        filtered_df = filtered_df[filtered_df['CUSTOMER'].isin(selected_customer)]

    # Group by YEAR, MONTH and DAY, and calculate the sum of TEU
    grouped_df = filtered_df.groupby(['YEAR', 'MONTH', 'DAY']).agg({'TEU': 'sum'}).reset_index()
    grouped_df['YEAR_MONTH_DAY'] = grouped_df['YEAR'].astype(str) + '-' + grouped_df['MONTH'].astype(str) + '-' + grouped_df['DAY'].astype(str)
    grouped_df = grouped_df.sort_values(['YEAR', 'MONTH', 'DAY'])

    # Create line graph
    fig = go.Figure(data=go.Bar(x=grouped_df['YEAR_MONTH_DAY'], y=grouped_df['TEU']))

    # Add title
    fig.update_layout(
        title_text ='PE1 : TEU PER ETD',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',)
    
    return fig

###################################
# 7 番目のグラフ　を生成します。
# CARRIER NAME別のTEU数を棒グラフで表示します。
#######################################

##############################################
@app.callback(
    Output('carrier-name-graph', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    grouped_df = pd.DataFrame()
    filtered_df = df

    # ORG_IDがPE1であるデータのみを抽出
    filtered_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']

    if selected_customer != 'ALL':
        filtered_df = filtered_df[filtered_df['CUSTOMER'].isin(selected_customer)]

    # 日付範囲、FL値、年、月でフィルタリング
    if start_date is not None and end_date is not None:
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['YEAR'] = pd.DatetimeIndex(filtered_df['ETD']).year

    if selected_year:
        start_date = pd.to_datetime(f'{selected_year[0]}-01-01')
        end_date = pd.to_datetime(f'{selected_year[0]}-12-31')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]

    if selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    # CARRIER_NAMEごとにデータをグループ化し、TEUの合計を計算
    grouped_df = filtered_df.groupby('CARRIER_NAME').agg({'TEU': 'sum'}).reset_index()

    # CARRIER_NAMEごとのTEU数を表示するカラフルな棒グラフを作成
    colors = ['rgb(26, 118, 255)', 'rgb(255, 182, 193)', 'rgb(255, 127, 80)', 'rgb(127, 255, 0)', 'rgb(255, 255, 0)'] * 100  # 色のリスト
    fig = go.Figure(data=go.Bar(x=grouped_df['CARRIER_NAME'], y=grouped_df['TEU'], marker_color=colors[:len(grouped_df)]))

    fig.update_layout(
        title_text ='PE1: Carrier Name: TEU',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )

    return fig





##########################
##
##  CALLBACK　８番目のグラフ
##  MONTHLY のSALESを表示します。
###########################

@app.callback(
    Output('monthly-profit-history-graph', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    filtered_df = df

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['JOB_DATE'] = pd.to_datetime(filtered_df['JOB_DATE'], format='%d/%m/%Y')
    filtered_df['YEAR'] = filtered_df['JOB_DATE'].dt.year
    filtered_df['MONTH'] = filtered_df['JOB_DATE'].dt.month
    month_dict = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    filtered_df['MONTH_NAME'] = filtered_df['MONTH'].map(month_dict)
    filtered_df['YEAR_MONTH'] = filtered_df['YEAR'].astype(str) + '-' + filtered_df['MONTH_NAME']

    if selected_year and selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby(['YEAR', 'MONTH', 'YEAR_MONTH', 'CUSTOMER']).agg({'SALES_AMT': 'sum'}).reset_index()
        grouped_df = grouped_df.sort_values(['YEAR', 'MONTH'])
        
        fig = px.bar(grouped_df, x='YEAR_MONTH', y='SALES_AMT', color='CUSTOMER', barmode='group')

    fig.update_layout(
        title_text ='PE1:Monthly Sales History',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )

    return fig
############################################
##
## CALL BACK 9番目のグラフを生成します
############################################

@app.callback(
    Output('monthly-ballance-history-graph', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    filtered_df = df

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['JOB_DATE'] = pd.to_datetime(filtered_df['JOB_DATE'], format='%d/%m/%Y')
    filtered_df['YEAR'] = filtered_df['JOB_DATE'].dt.year
    filtered_df['MONTH'] = filtered_df['JOB_DATE'].dt.month
    month_dict = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    filtered_df['MONTH_NAME'] = filtered_df['MONTH'].map(month_dict)
    filtered_df['YEAR_MONTH'] = filtered_df['YEAR'].astype(str) + '-' + filtered_df['MONTH_NAME']

    if selected_year and selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby(['YEAR', 'MONTH', 'YEAR_MONTH', 'CUSTOMER']).agg({'BALANCE': 'sum'}).reset_index()
        grouped_df = grouped_df.sort_values(['YEAR', 'MONTH'])
        
        fig = px.bar(grouped_df, x='YEAR_MONTH', y='BALANCE', color='CUSTOMER', barmode='group')

    fig.update_layout(
        title_text ='Monthly Profit History',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )

    return fig




##########################################
##
## callback関数で１０番目のグラフを生成します。
## container teuの数をMonthlyで履歴表示させます。
##
############################################
@app.callback(
    Output('monthly-Teu-history-graph', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    filtered_df = df

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['JOB_DATE'] = pd.to_datetime(filtered_df['JOB_DATE'], format='%d/%m/%Y')
    filtered_df['YEAR'] = filtered_df['JOB_DATE'].dt.year
    filtered_df['MONTH'] = filtered_df['JOB_DATE'].dt.month
    month_dict = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    filtered_df['MONTH_NAME'] = filtered_df['MONTH'].map(month_dict)
    filtered_df['YEAR_MONTH'] = filtered_df['YEAR'].astype(str) + '-' + filtered_df['MONTH_NAME']

    if selected_year and selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        grouped_df = pe1_df.groupby(['YEAR', 'MONTH', 'YEAR_MONTH', 'CUSTOMER']).agg({'TEU': 'sum'}).reset_index()
        grouped_df = grouped_df.sort_values(['YEAR', 'MONTH'])
        
        fig = px.bar(grouped_df, x='YEAR_MONTH', y='TEU', color='CUSTOMER', barmode='group')

    fig.update_layout(
        title_text ='月別TEU履歴',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )

    return fig
########################################
##
## 11番目のグラフ　
##
###########################################
@app.callback(
    Output('monthly-Dest-history-graph', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    filtered_df = df

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['JOB_DATE'] = pd.to_datetime(filtered_df['JOB_DATE'], format='%d/%m/%Y')
    filtered_df['YEAR'] = filtered_df['JOB_DATE'].dt.year
    filtered_df['MONTH'] = filtered_df['JOB_DATE'].dt.month
    month_dict = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    filtered_df['MONTH_NAME'] = filtered_df['MONTH'].map(month_dict)
    filtered_df['YEAR_MONTH'] = pd.to_datetime(filtered_df['YEAR'].astype(str) + '-' + filtered_df['MONTH_NAME'], format='%Y-%b')

    if selected_year and selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]

    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        # 行数をカウント
        grouped_df = pe1_df.groupby(['YEAR', 'MONTH', 'YEAR_MONTH', 'DEST_PORT_CD']).size().reset_index(name='Count')
        grouped_df = grouped_df.sort_values(['YEAR', 'MONTH'])
        
        fig = px.bar(grouped_df, x='YEAR_MONTH', y='Count', color='DEST_PORT_CD', barmode='group')


    fig.update_layout(
        title_text ='月別DEST_PORT_CD別TEU履歴',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )

    return fig

########################################
## 12番目のグラフ　
##  jobの数を表示します。
#######################################
@app.callback(
    Output('the-numbers-of-job', 'figure'),  # グラフのIDを 'the-numbers-of-job' に変更
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    filtered_df = df

    # ... (フィルタリングのコードは同じ)

    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['JOB_DATE'] = pd.to_datetime(filtered_df['JOB_DATE'], format='%d/%m/%Y')
    filtered_df['YEAR'] = filtered_df['JOB_DATE'].dt.year
    filtered_df['MONTH'] = filtered_df['JOB_DATE'].dt.month
    month_dict = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    filtered_df['MONTH_NAME'] = filtered_df['MONTH'].map(month_dict)
    filtered_df['YEAR_MONTH'] = pd.to_datetime(filtered_df['YEAR'].astype(str) + '-' + filtered_df['MONTH_NAME'], format='%Y-%b')

    if selected_year and selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]



    if 'PE1' in selected_org:
            pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
            if selected_customer != 'ALL':
                pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        # 'JOB_NO'を集計
            grouped_df = pe1_df.groupby(['YEAR', 'MONTH', 'YEAR_MONTH', 'DEST_PORT_CD']).agg({'JOB_NO': 'count'}).reset_index()
            grouped_df = grouped_df.sort_values(['YEAR', 'MONTH'])
        
            fig = px.bar(grouped_df, x='YEAR_MONTH', y='JOB_NO', color='DEST_PORT_CD', barmode='group')


    fig.update_layout(
        title_text ='月別JOB数履歴',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )




    return fig



########################################
## 13番目のグラフ　
##  sales とbalanceのグラフをコンバインします。
#######################################
@app.callback(
    Output('sales-balance-conbine', 'figure'),
    [Input('org-dropdown', 'value'),
     Input('customer-dropdown', 'value'),
     Input('fl-checkbox', 'value'),
     Input('year-checkbox', 'value'),
     Input('month-checkbox', 'value'),
     Input('dest-port-dropdown', 'value'),  
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)    
def update_graph(selected_org, selected_customer, selected_fl, selected_year, selected_month, selected_dest_port, start_date, end_date):
    filtered_df = df



    if start_date is not None and end_date is not None:
        start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
        end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= start_date) & (filtered_df['JOB_DATE'] <= end_date)]
    
    filtered_df = filtered_df[filtered_df['FL'].isin(selected_fl)]

    filtered_df['JOB_DATE'] = pd.to_datetime(filtered_df['JOB_DATE'], format='%d/%m/%Y')
    filtered_df['YEAR'] = filtered_df['JOB_DATE'].dt.year
    filtered_df['MONTH'] = filtered_df['JOB_DATE'].dt.month
    month_dict = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    filtered_df['MONTH_NAME'] = filtered_df['MONTH'].map(month_dict)
    filtered_df['YEAR_MONTH'] = pd.to_datetime(filtered_df['YEAR'].astype(str) + '-' + filtered_df['MONTH_NAME'], format='%Y-%b')

    if selected_year and selected_month:
        month_start = f'{selected_year[0]}-{selected_month[0]}-01'
        month_end = pd.to_datetime(month_start) + pd.DateOffset(months=1) - pd.DateOffset(days=1)
        filtered_df = filtered_df[(filtered_df['JOB_DATE'] >= pd.to_datetime(month_start)) & (filtered_df['JOB_DATE'] <= month_end)]


    if 'PE1' in selected_org:
        pe1_df = filtered_df[filtered_df['ORG_ID'] == 'PE1']
        if selected_customer != 'ALL':
            pe1_df = pe1_df[pe1_df['CUSTOMER'].isin(selected_customer)]
        # 'SALES_AMT'と'BALANCE'を集計
        grouped_df = pe1_df.groupby(['YEAR', 'MONTH', 'YEAR_MONTH']).agg({'SALES_AMT': 'sum', 'BALANCE': 'sum'}).reset_index()
        grouped_df = grouped_df.sort_values(['YEAR', 'MONTH'])
        
        # 棒グラフを作成
        fig = px.bar(grouped_df, x='YEAR_MONTH', y='SALES_AMT', barmode='group')

        # 線グラフを作成
        line_fig_balance = px.line(grouped_df, x='YEAR_MONTH', y='BALANCE')
        line_fig_balance.update_traces(line=dict(color='white'))  # 線の色を白に設定

        # 線グラフを棒グラフに追加
        fig.add_trace(line_fig_balance.data[0])
        
        fig.update_layout(
            title_text ='Sales & Profit History',
        title_font = dict(size=24,color='white'),
        legend=dict(title_font_color="white",font=dict(color="white")),
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        plot_bgcolor = '#1F5869',
        paper_bgcolor = '#1F5869',
    )

    return fig




########################################

if __name__ == "__main__":
    app.run_server(debug=False, port=1234)