from dash import Dash, dcc, html, Input, Output, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
import dash_bootstrap_components as dbc
import json
import pickle

pio.templates.default = "plotly_dark"

# initialize the Dash app
app = Dash(external_stylesheets=[dbc.themes.CYBORG], update_title=None)
app.config.suppress_callback_exceptions=True

# define layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# define page layouts
index_page = html.Div([
    html.H1('BTC Live Price Prediction - MLOps Project'),
    html.Br(),
    dcc.Link('Live Price Prediction', href='/page-1'),
    html.Br(),
    dcc.Link('Model Performance', href='/page-2'),
    html.Br(),
    dcc.Link('Server Performance', href='/page-3'),
    html.Br(),
    html.A('Database (PG Admin)', href='http://104.197.97.55:80', target='_blank')
])

# initialize page_1 dataframe reference
df_table_predict = pd.read_csv("dashboard_predict_price_df.csv")
df_table_predict['Time Period (min)'] = df_table_predict.index
df_table_predict['Difference'] = df_table_predict['actual_price'] - df_table_predict['predict_price']

df_table_predict = df_table_predict.drop(['predict_datetime'], axis=1)
df_table_predict = df_table_predict.rename(columns={'actual_price': 'Actual Price', 'predict_price': 'Predicted Price'})
df_table_predict = df_table_predict[['Time Period (min)', 'Actual Price', 'Predicted Price', 'Difference']]
df_table_predict = df_table_predict.round(2)

page_1_layout = html.Div([
    html.Div([
        html.H2('Live Price Prediction'),
        html.Br(),
        dcc.Link('Go back to home', href='/'),
        html.Br(),
        html.Span("Current Price: ", style={'fontSize': 24}),
        html.Span(id='current-price', style={'fontSize': 24}),
        html.Br(),
        html.Span("Mean Prediction Price: ", style={'fontSize': 24}),
        html.Span(id='average-prediction', style={'fontSize': 24}),
        html.Br(),
        html.Span("Difference: ", style={'fontSize': 24}),
        html.Span(id='average-prediction-diff', style={'fontSize': 24}),
        html.Br(),
        dcc.Graph(id='live-graph'),
        html.Br(),
        html.Span("Date: ", style={'fontSize': 24}),
        html.Span(id='current-date', style={'fontSize': 24}),
        html.Br(),
        html.Span("Current Time: ", style={'fontSize': 24}),
        html.Span(id='current-time', style={'fontSize': 24}),
        html.Br(),
        html.Span("Start Time: ", style={'fontSize': 24}),
        html.Span(id='predict-start-time', style={'fontSize': 24}),
        html.Br(),
        html.Span("End Time: ", style={'fontSize': 24}),
        html.Span(id='predict-end-time', style={'fontSize': 24}),
        html.Br(),
        html.Span("Next prediction : ", style={'fontSize': 24}),
        html.Span(id='predict-next-time', style={'fontSize': 24})
    ], style={'flex': '9'}),
    html.Div([
        html.H2("Price Table"),
        dash_table.DataTable(
            id='live-table',
            columns=[{"name": i, "id": i} for i in df_table_predict.columns],
            data=df_table_predict.to_dict('records'),
            style_cell={
            'backgroundColor': 'darkgrey',
            'color': 'black',
            'border': '1px solid grey',
            },
            style_header={
            'fontWeight': 'bold'
            }
        )
    ], style={'flex': '3'}),
    dcc.Interval(
        id='predict-update',
        interval=1*1000,
        n_intervals=0
    )
], style={'display': 'flex'})

# initialize page_2 dataframe reference
df_model_ranking = pd.read_csv("model_ranking_df.csv")
page_2_layout = html.Div([
    html.Div([
        html.H2('Cummulative MSE'),
        html.Br(),
        dcc.Link('Go back to home', href='/'),
        html.Br(),
        dcc.Graph(id='live-graph-page-2'),
        html.Br(),
        html.Span("Current Model ID: ", style={'fontSize': 24}),
        html.Span(id='current-model-id', style={'fontSize': 24}),
        html.Br(),
        html.Span("Train Datetime: ", style={'fontSize': 24}),
        html.Span(id='current-model-train-datetime', style={'fontSize': 24}),
        html.Br(),
        html.Span("Train Score: ", style={'fontSize': 24}),
        html.Span(id='current-model-train-score', style={'fontSize': 24}),
        html.Br(),
        html.Span("Parameters: ", style={'fontSize': 24}),
        html.Span(id='current-model-train-params', style={'fontSize': 24})
    ], style={'flex': '9'}),
    html.Div([
        html.H2("Top Model Performance"),
        dash_table.DataTable(
            id='live-table-page-2',
            columns=[{"name": i, "id": i} for i in df_model_ranking.columns],
            data=df_model_ranking.to_dict('records'),
            style_cell={
            'backgroundColor': 'darkgrey',
            'color': 'black',
            'border': '1px solid grey',
            },
            style_header={
            'fontWeight': 'bold'
            }
        )
    ], style={'flex': '3'}),
    dcc.Interval(
        id='model-performance-update',
        interval=5*1000,
        n_intervals=0
    )
], style={'display': 'flex'})

# initialize page_3 update inputs
cpu_data = []
db_conn_data = []
memory_data = []
time_data = []

page_3_layout = html.Div([
    html.H1("Server Performance"),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    html.Br(),
    dcc.Graph(id='live-cpu'),
    dcc.Graph(id='live-db-conn'),
    dcc.Graph(id='live-memory'),

    dcc.Interval(
        id='interval-update',
        interval=10*1000,
        n_intervals=0
    ),
])

# index callback and update function
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    else:
        return index_page

# page_1 callback and update function
@app.callback(
    Output('live-graph', 'figure'),
    Output('live-table', 'data'),
    Output('current-date', 'children'),
    Output('current-time', 'children'),
    Output('current-price', 'children'),
    Output('predict-start-time', 'children'),
    Output('predict-end-time', 'children'),
    Output('predict-next-time', 'children'),
    Output('average-prediction', 'children'),
    Output('average-prediction-diff', 'children'),
    Input('predict-update', 'n_intervals')
)
def update_page_1(n):
    df_current = pd.read_csv("dashboard_current_price_df.csv")
    fig = px.line(df_current, x='current_datetime', y='current_price')
    df_predict = pd.read_csv("dashboard_predict_price_df.csv")
    fig.add_scatter(x=df_predict['predict_datetime'], y=df_predict['predict_price'], mode='markers', name='prediction')
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None
        )
    
    # initialize df_table_predict
    df_table_predict = pd.read_csv("dashboard_predict_price_df.csv")
    df_table_predict['Time Period (min)'] = df_table_predict.index
    df_table_predict['Difference'] = df_table_predict['actual_price'] - df_table_predict['predict_price']
    avg_predict = df_table_predict['predict_price'].mean()
    avg_predict_str = f"${avg_predict:,.2f}"

    # update graph with average prediction ref line
    fig.add_shape(
        go.layout.Shape(
            type="line",
            x0=df_table_predict['predict_datetime'].head(1).iloc[0],
            x1=df_table_predict['predict_datetime'].tail(1).iloc[0],
            y0=avg_predict,
            y1=avg_predict,
            line=dict(color="blue", width=2)
            )
        )
    
    fig.add_annotation(
        x=df_table_predict['predict_datetime'].tail(1).iloc[0],
        y=1.00025*avg_predict,
        text=f"prediction mean: {avg_predict_str}",
        showarrow=False,
        font=dict(
            size=16,
            color='blue'
            )
        )

    df_table_predict = df_table_predict.drop(['predict_datetime'], axis=1)
    df_table_predict = df_table_predict.rename(columns={'actual_price': 'Actual Price', 'predict_price': 'Predicted Price'})
    df_table_predict = df_table_predict[['Time Period (min)', 'Actual Price', 'Predicted Price', 'Difference']]
    df_table_predict = df_table_predict.round(2)

    # live price read outputs
    with open("live_update_lst.json", "r") as f:
        live_update_lst = json.load(f)

        current_date = live_update_lst[0]
        current_time = live_update_lst[1]
        current_price = live_update_lst[2]
        predict_start_time = live_update_lst[3]
        predict_end_time = live_update_lst[4]
        next_predict_time = live_update_lst[5]
    
    current_price_float = current_price.replace('$', '').replace(',', '')
    current_price_float = float(current_price_float)
    avg_predict_diff = avg_predict - current_price_float
    avg_predict_diff_str = f"${avg_predict_diff:,.2f}"

    return fig, df_table_predict.to_dict('records'), current_date, current_time, current_price, predict_start_time, predict_end_time, next_predict_time, avg_predict_str, avg_predict_diff_str

# page_2 callback and update function
@app.callback(
        Output('live-graph-page-2', 'figure'),
        Output('live-table-page-2', 'data'),
        Output('current-model-id', 'children'),
        Output('current-model-train-datetime', 'children'),
        Output('current-model-train-score', 'children'),
        Output('current-model-train-params', 'children'),
        Input('model-performance-update', 'n_intervals')
        )
def update_page_2(n):
    with open("running_mse_lst.json", "r") as f:
        running_mse_lst = json.load(f)

    fig_2 = px.scatter(x=list(range(len(running_mse_lst))), y=running_mse_lst)

    with open("current_model_info_lst.json", "r") as f:
        current_model_info_lst = json.load(f)

    mse_running_avg = current_model_info_lst[-1]

    fig_2.add_shape(
        go.layout.Shape(
            type="line",
            x0=0,
            x1=30,
            y0=mse_running_avg,
            y1=mse_running_avg,
            line=dict(color="red", width=2)
            )
    )

    filtered_list = [x for x in running_mse_lst if x is not None]
    if max(filtered_list) > mse_running_avg:
        mse_running_max = max(filtered_list)
    else:
        mse_running_max = mse_running_avg

    fig_2.update_layout(xaxis_title='time step',
                        yaxis_title='MSE',
                        yaxis={'range': [0, 1.25*mse_running_max]})
    
    fig_2.add_annotation(
        x=25,
        y=1.1*mse_running_avg,
        text=f"Average MSE: {round(mse_running_avg)}",
        showarrow=False,
        font=dict(
            size=16,
            color='Red'
            )
        )

    df_model_ranking = pd.read_csv("model_ranking_df.csv")

    current_model_id = current_model_info_lst[0]
    current_model_train_datetime = current_model_info_lst[1]
    current_model_train_score = current_model_info_lst[2]
    current_model_train_params = current_model_info_lst[3]

    return fig_2, df_model_ranking.to_dict('records'), current_model_id, current_model_train_datetime, current_model_train_score, current_model_train_params

# page_3 callback and update function
@app.callback(
    [
        Output('live-cpu', 'figure'),
        Output('live-db-conn', 'figure'),
        Output('live-memory', 'figure')
    ],
    Input('interval-update', 'n_intervals')
)
def update_page_3(n):
    global cpu_data, db_conn_data, memory_data, time_data

    with open('server_update_lst.pkl', 'rb') as f:
        update_monitoring_lst = pickle.load(f)

        time_data = update_monitoring_lst[0]
        cpu_data = update_monitoring_lst[1]
        db_conn_data = update_monitoring_lst[2]
        memory_data = update_monitoring_lst[3]

    if len(cpu_data) > 300:
        del cpu_data[0]
        del db_conn_data[0]
        del memory_data[0]
        del time_data[0]

    cpu_trace = go.Scatter(x=time_data, y=cpu_data, mode='lines+markers', name='CPU')
    db_conn_trace = go.Scatter(x=time_data, y=db_conn_data, mode='lines+markers', name='Connections')
    memory_trace = go.Scatter(x=time_data, y=memory_data, mode='lines+markers', name='Memory')

    cpu_layout = go.Layout(title='CPU Usage', xaxis=dict(title='Time'), yaxis=dict(title='CPU (%)'), plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
    db_conn_layout = go.Layout(title='Postgres SQL Connections', xaxis=dict(title='Time'), yaxis=dict(title='number of connections (n)'), plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
    memory_layout = go.Layout(title='ML OPs Cluster Memory', xaxis=dict(title='Time'), yaxis=dict(title='Cluster Memory (MB)'), plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))

    return {'data': [cpu_trace], 'layout': cpu_layout}, {'data': [db_conn_trace], 'layout': db_conn_layout}, {'data': [memory_trace], 'layout': memory_layout}

if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8080)
