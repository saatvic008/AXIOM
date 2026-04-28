import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import networkx as nx

app = dash.Dash(__name__)

# Layout with dark theme
app.layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("AXIOM — Live Simulation Dashboard", style={'textAlign': 'center', 'color': '#7C4DFF'}),
    
    html.Div(className='row', style={'display': 'flex'}, children=[
        html.Div(style={'width': '50%'}, children=[
            dcc.Graph(id='price-chart'),
        ]),
        html.Div(style={'width': '50%'}, children=[
            dcc.Graph(id='wealth-histogram'),
        ]),
    ]),
    
    html.Div(className='row', style={'display': 'flex', 'marginTop': '20px'}, children=[
        html.Div(style={'width': '50%'}, children=[
            dcc.Graph(id='gini-chart'),
        ]),
        html.Div(style={'width': '50%'}, children=[
            dcc.Graph(id='trade-network'),
        ]),
    ]),
    
    dcc.Interval(
        id='interval-component',
        interval=2*1000, # 2 seconds
        n_intervals=0
    )
])

@app.callback(
    [Output('price-chart', 'figure'),
     Output('wealth-histogram', 'figure'),
     Output('gini-chart', 'figure'),
     Output('trade-network', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    # Load data
    try:
        trades_df = pd.read_csv("data/logs/trades_latest.csv")
        agents_df = pd.read_csv("data/logs/agents_latest.csv")
    except Exception as e:
        # Return empty figures if files not found yet
        return [go.Figure()]*4

    # 1. Price Chart
    # Use agents_df to derive price per step or trade history
    price_fig = px.line(trades_df, x='step', y='price', title='Market Price Discovery')
    price_fig.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

    # 2. Wealth Histogram
    latest_step = agents_df['step'].max()
    latest_agents = agents_df[agents_df['step'] == latest_step]
    wealth_fig = px.histogram(latest_agents, x='wealth', color='type', title='Wealth Distribution')
    wealth_fig.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

    # 3. Gini Chart
    # Calculate Gini for each step
    def calculate_gini_simple(wealths):
        sorted_wealths = np.sort(wealths)
        n = len(wealths)
        index = np.arange(1, n + 1)
        return (np.sum((2 * index - n - 1) * sorted_wealths)) / (n * np.sum(sorted_wealths))

    gini_data = agents_df.groupby('step')['wealth'].apply(calculate_gini_simple).reset_index()
    gini_fig = px.line(gini_data, x='step', y='wealth', title='Gini Coefficient (Inequality)')
    gini_fig.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

    # 4. Trade Network
    G = nx.Graph()
    # Sample last 50 trades
    recent_trades = trades_df.tail(50)
    for _, row in recent_trades.iterrows():
        buyer = row['buyer_id']
        seller = row['seller_id']
        if G.has_edge(buyer, seller):
            G[buyer][seller]['weight'] += 1
        else:
            G.add_edge(buyer, seller, weight=1)
    
    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(showscale=True, colorscale='Viridis', size=10, color=[], line_width=2))
    
    network_fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='Live Trade Network',
                    template='plotly_dark',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

    return price_fig, wealth_fig, gini_fig, network_fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
