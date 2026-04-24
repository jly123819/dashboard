import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats

# ── Load data ──────────────────────────────────────────────────────────────────
box_df  = pd.read_csv('danceability_boxplot.csv')
heat_df = pd.read_csv('heatmap_data.csv')
scat_df = pd.read_csv('scatterplot_data.csv')

box_df['Year']  = box_df['Year'].astype(int)
scat_df['Year'] = scat_df['Year'].astype(int)

years    = [int(y) for y in sorted(box_df['Year'].unique())]
features = ['Danceability', 'Energy', 'Valence', 'Acousticness']

# ── Colors ─────────────────────────────────────────────────────────────────────
BG    = '#0F1117'
CARD  = '#1A1D27'
GREEN = '#1DB954'
MUTED = '#8A8FA8'
WHITE = '#EEEEFF'
GRID  = '#1E2233'
RED   = '#FF6B6B'

# ── App ────────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = 'Spotify Dashboard'

app.layout = html.Div(
    style={'backgroundColor': BG, 'minHeight': '100vh',
           'fontFamily': 'Arial, sans-serif', 'padding': '24px 32px'},
    children=[

    html.H1('Spotify Top 10s  (2010–2019)',
            style={'color': WHITE, 'fontSize': '24px',
                   'fontWeight': '700', 'margin': '0 0 4px 0'}),
    html.P('Interactive audio feature explorer',
           style={'color': MUTED, 'fontSize': '12px', 'margin': '0 0 20px 0'}),

    # ── ROW 1: Compare box (left) + Bump chart (right) ────────────────────────
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[

        # TOP-LEFT: Overall vs Selected Year
        html.Div(style={'flex': '1', 'backgroundColor': CARD, 'borderRadius': '10px',
                        'padding': '20px', 'border': f'1px solid {GRID}'}, children=[
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between',
                            'alignItems': 'flex-start', 'marginBottom': '12px'}, children=[
                html.Div([
                    html.P('OVERALL VS SELECTED YEAR DISTRIBUTION',
                           style={'color': GREEN, 'fontSize': '10px', 'letterSpacing': '2px',
                                  'fontWeight': '700', 'margin': 0}),
                    html.P('Compare the distribution of a selected audio feature across all songs versus one chosen year',
                           style={'color': MUTED, 'fontSize': '11px', 'margin': '4px 0 0 0'}),
                ]),
                html.Div(style={'display': 'flex', 'gap': '8px', 'alignItems': 'center'}, children=[
                    dcc.Dropdown(
                        id='compare-feature',
                        options=[{'label': f, 'value': f} for f in features + ['Popularity']],
                        value='Danceability', clearable=False,
                        style={'width': '145px', 'fontSize': '12px'},
                    ),
                    dcc.Dropdown(
                        id='compare-year',
                        options=[{'label': str(y), 'value': y} for y in years],
                        value=2017, clearable=False,
                        style={'width': '90px', 'fontSize': '12px'},
                    ),
                ]),
            ]),
            dcc.Graph(id='compare-chart', style={'height': '360px'},
                      config={'displayModeBar': False}),
        ]),

        # TOP-RIGHT: Genre Feature Map scatter
        html.Div(style={'flex': '1', 'backgroundColor': CARD, 'borderRadius': '10px',
                        'padding': '20px', 'border': f'1px solid {GRID}'}, children=[
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between',
                            'alignItems': 'flex-start', 'marginBottom': '10px'}, children=[
                html.Div([
                    html.P('HOW TOP GENRES COMPARE ACROSS AUDIO FEATURES',
                           style={'color': GREEN, 'fontSize': '10px', 'letterSpacing': '2px',
                                  'fontWeight': '700', 'margin': 0}),
                    html.P('Position top genres by selected feature pairs, with bubble size showing song count and color showing average popularity',
                           style={'color': MUTED, 'fontSize': '11px', 'margin': '4px 0 0 0'}),
                ]),
                html.Div(style={'display': 'flex', 'gap': '8px', 'alignItems': 'center',
                                'flexWrap': 'wrap', 'justifyContent': 'flex-end'}, children=[
                    html.Span('Top', style={'color': MUTED, 'fontSize': '11px'}),
                    dcc.Dropdown(
                        id='gmap-topn',
                        options=[{'label': str(n), 'value': n} for n in [5, 8, 10, 15, 20]],
                        value=12, clearable=False,
                        style={'width': '65px', 'fontSize': '11px'},
                    ),
                    dcc.Dropdown(
                        id='gmap-highlight',
                        options=[{'label': 'Highlight genre...', 'value': 'none'}],
                        value='none', clearable=False,
                        style={'width': '165px', 'fontSize': '11px'},
                    ),
                ]),
            ]),
            html.Div(style={'display': 'flex', 'gap': '10px', 'marginBottom': '8px',
                            'alignItems': 'center'}, children=[
                html.Span('X:', style={'color': MUTED, 'fontSize': '11px'}),
                dcc.Dropdown(
                    id='gmap-x',
                    options=[{'label': f, 'value': f}
                             for f in ['Danceability','Energy','Valence','Acousticness','Popularity']],
                    value='Energy', clearable=False,
                    style={'width': '148px', 'fontSize': '11px'},
                ),
                html.Span('Y:', style={'color': MUTED, 'fontSize': '11px'}),
                dcc.Dropdown(
                    id='gmap-y',
                    options=[{'label': f, 'value': f}
                             for f in ['Danceability','Energy','Valence','Acousticness','Popularity']],
                    value='Danceability', clearable=False,
                    style={'width': '148px', 'fontSize': '11px'},
                ),
            ]),
            dcc.Graph(id='gmap-chart', style={'height': '310px'},
                      config={'displayModeBar': False}),
        ]),
    ]),

    # ── ROW 2: Heatmap (left) + Scatter (right) ──────────────────────────────
    html.Div(style={'display': 'flex', 'gap': '20px'}, children=[

        # BOTTOM-LEFT: Heatmap
        html.Div(style={'flex': '1', 'backgroundColor': CARD, 'borderRadius': '10px',
                        'padding': '20px', 'border': f'1px solid {GRID}'}, children=[
            html.P('AUDIO FEATURE PROFILES BY GENRE',
                   style={'color': GREEN, 'fontSize': '10px',
                          'letterSpacing': '2px', 'fontWeight': '700', 'margin': '0 0 4px 0'}),
            html.P('Comparing relative audio feature profiles across the top genres',
                   style={'color': MUTED, 'fontSize': '11px', 'margin': '0 0 10px 0'}),
            html.Div(style={'display': 'flex', 'gap': '10px', 'alignItems': 'center',
                            'flexWrap': 'wrap', 'marginBottom': '10px'}, children=[
                dcc.Checklist(
                    id='feature-filter',
                    options=[{
                        'label': html.Span(f, style={'color': '#EEEEFF', 'fontSize': '11px',
                                                     'marginLeft': '5px', 'marginRight': '12px'}),
                        'value': f
                    } for f in features],
                    value=features, inline=True,
                    inputStyle={'accentColor': '#1DB954', 'cursor': 'pointer'},
                ),
                dcc.Dropdown(
                    id='heatmap-sort',
                    options=[{'label': 'Sort: Default', 'value': 'default'}] +
                            [{'label': f'Sort by {f}', 'value': f} for f in features],
                    value='default', clearable=False,
                    style={'width': '145px', 'fontSize': '11px'},
                ),
                dcc.Dropdown(
                    id='genre-highlight',
                    options=[{'label': 'Highlight genre...', 'value': 'none'}] +
                            [{'label': g, 'value': g}
                             for g in sorted(heat_df['Genre'].unique())],
                    value='none', clearable=False,
                    style={'width': '165px', 'fontSize': '11px'},
                ),
            ]),
            dcc.Graph(id='heatmap-chart', style={'height': '340px'},
                      config={'displayModeBar': False}),
        ]),

        # BOTTOM-RIGHT: Scatter
        html.Div(style={'flex': '1', 'backgroundColor': CARD, 'borderRadius': '10px',
                        'padding': '20px', 'border': f'1px solid {GRID}'}, children=[
            html.P('AUDIO FEATURE VS POPULARITY',
                   style={'color': GREEN, 'fontSize': '10px',
                          'letterSpacing': '2px', 'fontWeight': '700', 'margin': '0 0 4px 0'}),
            html.P('Exploring the relationship between popularity and a selected audio feature across songs from 2010 to 2019',
                   style={'color': MUTED, 'fontSize': '11px', 'margin': '0 0 10px 0'}),
            html.Div(style={'display': 'flex', 'gap': '12px',
                            'alignItems': 'center', 'marginBottom': '10px'}, children=[
                dcc.Dropdown(
                    id='feature-select',
                    options=[{'label': f, 'value': f} for f in features],
                    value='Danceability', clearable=False,
                    style={'width': '155px', 'fontSize': '12px'},
                ),
                html.Div(style={'flex': '1'}, children=[
                    dcc.RangeSlider(
                        id='year-slider',
                        min=2010, max=2019, step=1,
                        marks={y: {'label': str(y),
                                   'style': {'color': MUTED, 'fontSize': '9px'}}
                               for y in years},
                        value=[2010, 2019],
                    ),
                ]),
            ]),
            dcc.Graph(id='scatter-chart', style={'height': '330px'},
                      config={'displayModeBar': False}),
        ]),
    ]),

    html.P('DS2003 · Spotify Top Songs Dataset · 2010–2019',
           style={'color': GRID, 'fontSize': '10px',
                  'textAlign': 'center', 'marginTop': '20px'}),
])


# ── Callback 1: Violin/Box ────────────────────────────────────────────────────
@app.callback(Output('violin-chart', 'figure'),
              Input('year-highlight', 'value'))
def update_violin(highlight):
    fig = go.Figure()
    medians = []

    for i, yr in enumerate(years):
        data = box_df[box_df['Year'] == yr]['Danceability'].dropna().values.astype(float)
        if len(data) < 3:
            medians.append(float('nan'))
            continue

        selected = (highlight == 'all' or highlight == str(yr))
        fade  = 1.0 if selected else 0.2
        clr   = GREEN if selected else '#2A5C3A'
        wline = WHITE if selected else MUTED
        ww    = 3.0 if selected else 1.2

        q1  = float(np.percentile(data, 25))
        med = float(np.median(data))
        q3  = float(np.percentile(data, 75))
        iqr = q3 - q1
        w_lo = float(data[data >= q1 - 1.5 * iqr].min())
        w_hi = float(data[data <= q3 + 1.5 * iqr].max())
        medians.append(med)

        # Violin
        try:
            kde  = stats.gaussian_kde(data, bw_method=0.35)
            yv   = np.linspace(data.min() - 2, data.max() + 2, 150)
            dens = kde(yv)
            dens = dens / dens.max() * 0.32 * fade
            xL   = (i - dens).tolist()
            xR   = (i + dens).tolist()
            yv   = yv.tolist()
            fig.add_trace(go.Scatter(
                x=xL + list(reversed(xR)),
                y=yv + list(reversed(yv)),
                fill='toself',
                fillcolor=f'rgba(29,185,84,{round(0.06 * fade, 3)})',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip', showlegend=False,
            ))
        except Exception:
            pass

        bw = 0.28
        fig.add_trace(go.Scatter(
            x=[i-bw, i+bw, i+bw, i-bw, i-bw],
            y=[q1, q1, q3, q3, q1],
            fill='toself',
            fillcolor=f'rgba(29,185,84,{round(0.38 * fade, 3)})',
            line=dict(color=clr, width=1.5),
            hoverinfo='skip', showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=[i - bw, i + bw], y=[med, med],
            mode='lines', line=dict(color=wline, width=ww),
            hovertemplate=f'<b>{yr}</b><br>Median: {med:.1f}<br>Q1: {q1:.1f}  Q3: {q3:.1f}<extra></extra>',
            showlegend=(i == 0), name='Median',
        ))
        for ya, yb in [(w_lo, q1), (q3, w_hi)]:
            fig.add_trace(go.Scatter(
                x=[i, i], y=[ya, yb],
                mode='lines', line=dict(color=clr, width=1.6),
                hoverinfo='skip', showlegend=False,
            ))
        for yc in [w_lo, w_hi]:
            fig.add_trace(go.Scatter(
                x=[i - 0.12, i + 0.12], y=[yc, yc],
                mode='lines', line=dict(color=clr, width=1.6),
                hoverinfo='skip', showlegend=False,
            ))
        out = data[(data < w_lo) | (data > w_hi)]
        if len(out):
            jit = np.random.uniform(-0.07, 0.07, len(out)).tolist()
            fig.add_trace(go.Scatter(
                x=[i + j for j in jit], y=out.tolist(),
                mode='markers',
                marker=dict(color=RED, size=6, opacity=round(0.8 * fade, 2)),
                hovertemplate='Outlier: %{y}<extra></extra>',
                showlegend=(i == 0), name='Outliers',
            ))

    fig.add_trace(go.Scatter(
        x=list(range(len(years))), y=medians,
        mode='lines+markers',
        line=dict(color=GREEN, width=2, dash='dash'),
        marker=dict(color=GREEN, size=7),
        name='Median trend',
        hovertemplate='%{text}: %{y:.1f}<extra></extra>',
        text=[str(y) for y in years],
    ))

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font=dict(color=WHITE),
        margin=dict(l=55, r=20, t=10, b=50),
        xaxis=dict(tickvals=list(range(len(years))),
                   ticktext=[str(y) for y in years],
                   gridcolor=GRID, linecolor=GRID,
                   zerolinecolor=GRID, tickfont=dict(color=MUTED)),
        yaxis=dict(title='Danceability Score', range=[18, 108],
                   gridcolor=GRID, linecolor=GRID,
                   zerolinecolor=GRID, tickfont=dict(color=MUTED)),
        showlegend=True,
        legend=dict(orientation='h', y=-0.18, x=0.5, xanchor='center',
                    bgcolor='rgba(0,0,0,0)', font=dict(size=10, color=MUTED)),
    )
    return fig


# ── Callback 2: Heatmap ───────────────────────────────────────────────────────
@app.callback(Output('heatmap-chart', 'figure'),
              Input('feature-filter', 'value'),
              Input('heatmap-sort', 'value'),
              Input('genre-highlight', 'value'))
def update_heatmap(selected, sort_by, hl_genre):
    if not selected:
        selected = features[:]
    filtered = heat_df[heat_df['Audio Feature'].isin(selected)].copy()
    pivot = filtered.pivot_table(
        index='Genre', columns='Audio Feature',
        values='Relative Level', aggfunc='mean'
    )
    col_order = [f for f in features if f in pivot.columns]
    pivot = pivot[col_order]

    if sort_by != 'default' and sort_by in pivot.columns:
        pivot = pivot.sort_values(sort_by, ascending=True)

    genres_list = pivot.index.tolist()
    z_vals      = pivot.values.tolist()
    zmin        = float(pivot.values.min())
    zmax        = float(pivot.values.max())

    # For highlight: dim non-selected rows by shifting z toward 0
    if hl_genre != 'none' and hl_genre in genres_list:
        z_display = []
        for i, g in enumerate(genres_list):
            if g == hl_genre:
                z_display.append(z_vals[i])
            else:
                # push toward neutral (zmin) so color dims
                z_display.append([v * 0.15 for v in z_vals[i]])
    else:
        z_display = z_vals

    # Build text matrix for hover (real values, not z_display which may be dimmed)
    text_matrix = []
    for i, g in enumerate(genres_list):
        row_texts = []
        for j, col in enumerate(col_order):
            val = round(z_vals[i][j], 3)
            row_texts.append(f'<b>{g}</b><br>{col}: {val}')
        text_matrix.append(row_texts)

    fig = go.Figure(go.Heatmap(
        z=z_display,
        x=col_order,
        y=genres_list,
        text=text_matrix,
        colorscale=[[0, '#0A1A0E'], [0.45, '#1A2D20'], [1, GREEN]],
        zmin=zmin, zmax=zmax,
        hovertemplate='%{text}<extra></extra>',
        colorbar=dict(
            thickness=12, len=0.85,
            tickfont=dict(color=MUTED, size=10),
            outlinecolor=GRID,
            title=dict(text='Relative<br>Level', font=dict(color=MUTED, size=10)),
        ),
    ))

    # Green border around highlighted genre
    if hl_genre != 'none' and hl_genre in genres_list:
        idx = genres_list.index(hl_genre)
        fig.add_shape(
            type='rect',
            x0=-0.5, x1=len(col_order) - 0.5,
            y0=idx - 0.5, y1=idx + 0.5,
            line=dict(color=GREEN, width=2.5),
            fillcolor='rgba(0,0,0,0)',
        )

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font=dict(color=WHITE),
        margin=dict(l=10, r=60, t=10, b=55),
        xaxis=dict(
            side='bottom', gridcolor=GRID, linecolor=GRID,
            tickfont=dict(color=WHITE, size=12),
        ),
        yaxis=dict(
            gridcolor=GRID, linecolor=GRID,
            tickfont=dict(color=WHITE, size=11),
            automargin=True,
        ),
    )
    return fig


# ── Callback 3: Scatter ───────────────────────────────────────────────────────
@app.callback(Output('scatter-chart', 'figure'),
              Input('feature-select', 'value'),
              Input('year-slider', 'value'))
def update_scatter(feature, yr_range):
    lo = int(yr_range[0])
    hi = int(yr_range[1])
    df = scat_df[(scat_df['Year'] >= lo) & (scat_df['Year'] <= hi)].copy()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[feature].tolist(),
        y=df['Popularity'].tolist(),
        mode='markers',
        marker=dict(
            color=df['Year'].tolist(),
            colorscale=[[0, '#158B3E'], [1, '#84EFA8']],
            size=7, opacity=0.72,
            colorbar=dict(title='Year', thickness=10,
                          tickfont=dict(color=MUTED, size=9),
                          outlinecolor=GRID),
        ),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>'
            'Artist: %{customdata[1]}<br>'
            f'{feature}: %{{x}}<br>'
            'Popularity: %{y}<extra></extra>'
        ),
        customdata=list(zip(df['Title'].tolist(), df['Artist'].tolist())),
        showlegend=False,
    ))

    x_vals = df[feature].dropna().values
    y_vals = df.loc[df[feature].notna(), 'Popularity'].values
    if len(x_vals) > 5:
        m, b, r_val, _, _ = stats.linregress(x_vals, y_vals)
        x_line = [float(x_vals.min()), float(x_vals.max())]
        y_line = [float(m * x + b) for x in x_line]
        fig.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode='lines',
            line=dict(color=RED, width=2, dash='dash'),
            name=f'Trend  r = {r_val:.2f}',
            hoverinfo='skip',
        ))

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font=dict(color=WHITE),
        margin=dict(l=55, r=20, t=10, b=50),
        xaxis=dict(title=feature, gridcolor=GRID, linecolor=GRID,
                   zerolinecolor=GRID, tickfont=dict(color=MUTED)),
        yaxis=dict(title='Popularity', gridcolor=GRID, linecolor=GRID,
                   zerolinecolor=GRID, tickfont=dict(color=MUTED)),
        showlegend=True,
        legend=dict(orientation='h', y=-0.22, x=0.5, xanchor='center',
                    bgcolor='rgba(0,0,0,0)', font=dict(size=10, color=MUTED)),
    )
    return fig




# ── Callback 4: Side-by-side Boxplot ─────────────────────────────────────────
@app.callback(Output('compare-chart', 'figure'),
              Input('compare-feature', 'value'),
              Input('compare-year', 'value'))
def update_compare(feature, sel_year):
    sel_year = int(sel_year)

    # Get data
    all_data  = scat_df[feature].dropna().values.astype(float)
    yr_data   = scat_df[scat_df['Year'] == sel_year][feature].dropna().values.astype(float)

    def box_stats(data):
        q1  = float(np.percentile(data, 25))
        med = float(np.median(data))
        q3  = float(np.percentile(data, 75))
        iqr = q3 - q1
        wlo = float(data[data >= q1 - 1.5*iqr].min())
        whi = float(data[data <= q3 + 1.5*iqr].max())
        out = data[(data < wlo) | (data > whi)]
        return q1, med, q3, iqr, wlo, whi, out

    def draw_box(fig, data, x_center, color, label):
        q1, med, q3, iqr, wlo, whi, out = box_stats(data)
        bw = 0.28

        # Violin
        try:
            kde  = stats.gaussian_kde(data, bw_method=0.4)
            yv   = np.linspace(data.min()-2, data.max()+2, 200)
            dens = kde(yv); dens = dens / dens.max() * 0.22
            fig.add_trace(go.Scatter(
                x=np.concatenate([x_center - dens, (x_center + dens)[::-1]]),
                y=np.concatenate([yv, yv[::-1]]),
                fill='toself',
                fillcolor=f'rgba(29,185,84,0.07)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip', showlegend=False,
            ))
        except Exception:
            pass

        hover = (f'<b>{label}</b><br>'
                 f'Median: {med:.1f}<br>'
                 f'Q1: {q1:.1f}<br>'
                 f'Q3: {q3:.1f}<br>'
                 f'IQR: {iqr:.1f}<br>'
                 f'Lower whisker: {wlo:.1f}<br>'
                 f'Upper whisker: {whi:.1f}<br>'
                 f'Outlier count: {len(out)}<extra></extra>')

        # Box body
        fig.add_trace(go.Scatter(
            x=[x_center-bw, x_center+bw, x_center+bw, x_center-bw, x_center-bw],
            y=[q1, q1, q3, q3, q1],
            fill='toself',
            fillcolor=f'rgba(29,185,84,0.35)',
            line=dict(color=color, width=2),
            hovertemplate=hover, name=label, showlegend=False,
        ))
        # Median
        fig.add_trace(go.Scatter(
            x=[x_center-bw, x_center+bw], y=[med, med],
            mode='lines', line=dict(color=WHITE, width=3.5),
            hovertemplate=hover, showlegend=False, name=label,
        ))
        # Invisible hover zone covering full box height for easy access
        fig.add_trace(go.Scatter(
            x=[x_center]*4,
            y=[wlo, q1, q3, whi],
            mode='markers',
            marker=dict(color='rgba(0,0,0,0)', size=10),
            hovertemplate=hover, showlegend=False, name=label,
        ))
        # Whiskers
        for ya, yb in [(wlo, q1), (q3, whi)]:
            fig.add_trace(go.Scatter(
                x=[x_center, x_center], y=[ya, yb],
                mode='lines', line=dict(color=color, width=2),
                hoverinfo='skip', showlegend=False,
            ))
        for yc in [wlo, whi]:
            fig.add_trace(go.Scatter(
                x=[x_center-0.13, x_center+0.13], y=[yc, yc],
                mode='lines', line=dict(color=color, width=2),
                hoverinfo='skip', showlegend=False,
            ))
        # Outliers
        if len(out):
            jit = np.random.uniform(-0.06, 0.06, len(out)).tolist()
            fig.add_trace(go.Scatter(
                x=[x_center + j for j in jit], y=out.tolist(),
                mode='markers',
                marker=dict(color=RED, size=6, opacity=0.75),
                hovertemplate=f'Outlier ({label}): %{{y}}<extra></extra>',
                showlegend=False,
            ))
        return q1, med, q3, iqr, wlo, whi, out

    fig = go.Figure()
    _, all_med, _, _, _, _, _ = draw_box(fig, all_data,  x_center=0.5, color=GREEN,       label='All Years')
    _, yr_med,  _, _, _, _, _ = draw_box(fig, yr_data,   x_center=1.5, color='#4CC9F0',   label=str(sel_year))

    # Annotation: median difference
    diff  = yr_med - all_med
    sign  = '+' if diff >= 0 else ''
    arrow = '▲' if diff > 0 else ('▼' if diff < 0 else '—')
    color_ann = '#4CC9F0' if diff > 0 else RED if diff < 0 else MUTED
    fig.add_annotation(
        x=1.0, y=max(all_med, yr_med) + 4,
        text=f'{arrow}  {sel_year} median is <b>{sign}{diff:.1f}</b> vs overall',
        showarrow=False,
        font=dict(color=color_ann, size=12),
        bgcolor='rgba(15,17,23,0.75)',
        bordercolor=color_ann, borderwidth=1,
        borderpad=6,
    )

    # Divider line
    y_range = scat_df[feature].dropna().values
    fig.add_shape(type='line',
                  x0=1.0, x1=1.0,
                  y0=float(y_range.min()) - 3,
                  y1=float(y_range.max()) + 3,
                  line=dict(color=GRID, width=1.5, dash='dot'))

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font=dict(color=WHITE),
        margin=dict(l=55, r=20, t=30, b=40),
        xaxis=dict(
            tickvals=[0.5, 1.5],
            ticktext=[f'All Years<br>(n={len(all_data)})',
                      f'{sel_year}<br>(n={len(yr_data)})'],
            tickfont=dict(color=WHITE, size=12),
            gridcolor=GRID, linecolor=GRID, zerolinecolor='rgba(0,0,0,0)',
            range=[0, 2],
        ),
        yaxis=dict(title=feature, gridcolor=GRID, linecolor=GRID,
                   zerolinecolor=GRID, tickfont=dict(color=MUTED)),
    )
    return fig



# ── Callback: Genre map highlight options ────────────────────────────────────
@app.callback(Output('gmap-highlight', 'options'),
              Output('gmap-highlight', 'value'),
              Input('gmap-topn', 'value'))
def update_gmap_options(topn):
    stats = (scat_df.groupby('Genre')['Popularity']
             .agg(avg_pop='mean', song_count='count').reset_index())
    stats = stats[stats['song_count'] >= 3].sort_values('avg_pop', ascending=False).head(topn)
    genres = sorted(stats['Genre'].tolist())
    opts = [{'label': 'Highlight genre...', 'value': 'none'}] +            [{'label': g, 'value': g} for g in genres]
    return opts, 'none'


# ── Callback: Genre feature map scatter ───────────────────────────────────────
@app.callback(Output('gmap-chart', 'figure'),
              Input('gmap-topn', 'value'),
              Input('gmap-x', 'value'),
              Input('gmap-y', 'value'),
              Input('gmap-highlight', 'value'))
def update_gmap(topn, x_feat, y_feat, hl_genre):
    all_feats = ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Popularity']
    agg_dict  = {f: 'mean' for f in all_feats}
    agg_dict['Popularity'] = 'mean'
    agg_dict['Genre']      = 'first'   # placeholder

    stats = (scat_df.groupby('Genre')
             .agg(avg_pop=('Popularity', 'mean'),
                  song_count=('Popularity', 'count'),
                  **{f: (f, 'mean') for f in all_feats})
             .reset_index())

    stats = (stats[stats['song_count'] >= 3]
             .sort_values('avg_pop', ascending=False)
             .head(topn))

    if stats.empty:
        fig = go.Figure()
        fig.update_layout(paper_bgcolor=BG, plot_bgcolor=CARD)
        return fig

    genres    = stats['Genre'].tolist()
    x_vals    = stats[x_feat].tolist()
    y_vals    = stats[y_feat].tolist()
    pops      = stats['avg_pop'].tolist()
    counts    = stats['song_count'].tolist()

    # Bubble size: scale song count to reasonable marker sizes
    max_cnt   = max(counts) if counts else 1
    sizes     = [max(12, min(55, (c / max_cnt) * 55)) for c in counts]

    # Color by avg popularity (green gradient)
    pop_min, pop_max = min(pops), max(pops)

    # Opacity for highlight
    opacities = [1.0 if (hl_genre == 'none' or hl_genre == g) else 0.12 for g in genres]

    fig = go.Figure()

    # Reference lines (overall avg of x and y features)
    x_avg = float(scat_df[x_feat].mean())
    y_avg = float(scat_df[y_feat].mean())

    # Quadrant shading (very subtle)
    x_range = [float(stats[x_feat].min()) - 5, float(stats[x_feat].max()) + 5]
    y_range = [float(stats[y_feat].min()) - 5, float(stats[y_feat].max()) + 5]

    # Smart label placement: compute nudged positions to avoid overlap
    # Sort by x so we can detect proximity
    indexed = sorted(enumerate(zip(genres, x_vals, y_vals, pops, counts, sizes, opacities)),
                     key=lambda t: t[1][1])

    # First pass: draw all markers (no text)
    for orig_i, (genre, x, y, pop, cnt, sz, op) in indexed:
        t_norm = (pop - pop_min) / (pop_max - pop_min + 1e-9)
        r = int(29  + t_norm * (1))
        g_val = int(100 + t_norm * 85)
        b_val = int(50  + t_norm * 34)
        clr = f'rgb({29},{g_val},{50})'

        is_hl   = (hl_genre == 'none' or hl_genre == genre)
        outline = WHITE if (hl_genre == genre) else GRID
        ow      = 2.5 if (hl_genre == genre) else 1.0

        hover = (f'<b>{genre}</b><br>'
                 f'Avg popularity: {pop:.1f}<br>'
                 f'Songs: {cnt}<br>'
                 f'{x_feat}: {x:.1f}<br>'
                 f'{y_feat}: {y:.1f}'
                 f'<extra></extra>')

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers',
            marker=dict(size=sz, color=clr, opacity=op,
                        line=dict(color=outline, width=ow)),
            hovertemplate=hover,
            showlegend=False, name=genre,
        ))

    # Smart label placement with force-based nudging and leader lines
    # Build initial label positions offset from bubble center
    import math

    # All 8 direction offsets (angle in degrees)
    def offset_candidates(x, y, sz):
        r = sz * 0.18 + 3.5   # offset radius scales with bubble size
        angles = [90, 270, 0, 180, 45, 135, 315, 225]
        x_scale = (max(x_vals) - min(x_vals) + 1) / (max(y_vals) - min(y_vals) + 1)
        cands = []
        for a in angles:
            rad = math.radians(a)
            cx = x + r * math.cos(rad) * x_scale
            cy = y + r * math.sin(rad)
            ha = 'right' if math.cos(rad) < -0.3 else ('left' if math.cos(rad) > 0.3 else 'center')
            va = 'top'   if math.sin(rad) < -0.3 else ('bottom' if math.sin(rad) > 0.3 else 'middle')
            cands.append((cx, cy, ha, va))
        return cands

    placed = []   # (lx, ly, lw, lh) — approximate bounding boxes

    def overlap_score(cx, cy, placed):
        """Lower = less overlap."""
        score = 0
        for px, py in placed:
            d = ((cx - px)**2 + (cy - py)**2) ** 0.5
            if d < 5:
                score += (5 - d) ** 2
        return score

    label_data = []  # (genre, anchor_x, anchor_y, label_x, label_y, ha, va)

    for orig_i, (genre, x, y, pop, cnt, sz, op) in indexed:
        if not (hl_genre == 'none' or hl_genre == genre):
            continue
        cands = offset_candidates(x, y, sz)
        best_score = 1e9
        best_pos   = cands[0]
        for cx, cy, ha, va in cands:
            s = overlap_score(cx, cy, placed)
            if s < best_score:
                best_score = s
                best_pos   = (cx, cy, ha, va)
        lx, ly, ha, va = best_pos
        placed.append((lx, ly))
        label_data.append((genre, x, y, lx, ly, ha, va, op))

    for genre, ax, ay, lx, ly, ha, va, op in label_data:
        dist = ((lx - ax)**2 + (ly - ay)**2) ** 0.5
        # Draw leader line only when label is moved far from bubble
        if dist > 5:
            fig.add_shape(type='line',
                x0=ax, y0=ay, x1=lx, y1=ly,
                line=dict(color='rgba(180,180,200,0.25)', width=0.8))
        fig.add_annotation(
            x=lx, y=ly, text=genre,
            showarrow=False, xanchor=ha, yanchor=va,
            font=dict(color=WHITE, size=10),
            bgcolor='rgba(15,17,23,0.55)',
            borderpad=2,
        )

    # Reference lines
    fig.add_vline(x=x_avg, line=dict(color=MUTED, width=1.2, dash='dash'))
    fig.add_hline(y=y_avg, line=dict(color=MUTED, width=1.2, dash='dash'))

    # Axis range with padding
    x_lo = min(x_vals) - 6
    x_hi = max(x_vals) + 6
    y_lo = min(y_vals) - 6
    y_hi = max(y_vals) + 6

    # Subtle quadrant corner labels (inside axes, not clipped)
    fig.add_annotation(x=x_hi - 1, y=y_hi - 1,
        text=f'↑ {y_feat}  {x_feat} →',
        showarrow=False, xanchor='right', yanchor='top',
        font=dict(color='rgba(138,143,168,0.35)', size=8))
    fig.add_annotation(x=x_lo + 1, y=y_lo + 1,
        text=f'↓ {y_feat}  ← {x_feat}',
        showarrow=False, xanchor='left', yanchor='bottom',
        font=dict(color='rgba(138,143,168,0.35)', size=8))

    # Avg reference labels (inside the chart area)
    fig.add_annotation(x=x_avg + 0.5, y=y_lo + 1,
        text=f'avg {x_feat}: {x_avg:.1f}',
        showarrow=False, xanchor='left', yanchor='bottom',
        font=dict(color='rgba(138,143,168,0.55)', size=8))
    fig.add_annotation(x=x_lo + 1, y=y_avg + 0.5,
        text=f'avg {y_feat}: {y_avg:.1f}',
        showarrow=False, xanchor='left', yanchor='bottom',
        font=dict(color='rgba(138,143,168,0.55)', size=8))

    # Star annotation for top-popularity genre
    if genres:
        top_i = pops.index(max(pops))
        if opacities[top_i] > 0.5:
            fig.add_annotation(
                x=x_vals[top_i], y=y_vals[top_i],
                text=f'★',
                showarrow=False, xanchor='center', yanchor='middle',
                font=dict(color='#F9C74F', size=14),
            )

    # Colorbar (inside right margin, not clipped)
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(
            colorscale=[[0, 'rgb(29,64,40)'], [1, GREEN]],
            color=[0, 1], showscale=True,
            colorbar=dict(
                title=dict(text='Avg Pop', font=dict(color=MUTED, size=9),
                           side='right'),
                thickness=10, len=0.55, x=1.01,
                tickfont=dict(color=MUTED, size=9),
                tickvals=[0, 1],
                ticktext=[f'{pop_min:.0f}', f'{pop_max:.0f}'],
                outlinecolor=GRID,
            ),
        ),
        showlegend=False, hoverinfo='skip',
    ))

    # Size legend — top-left corner of paper, away from data
    fig.add_annotation(
        x=0.01, y=0.99, xref='paper', yref='paper',
        text='● size = song count',
        showarrow=False, xanchor='left', yanchor='top',
        font=dict(color=MUTED, size=9),
    )

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font=dict(color=WHITE),
        margin=dict(l=55, r=70, t=10, b=50),
        xaxis=dict(title=x_feat, gridcolor=GRID, linecolor=GRID,
                   zerolinecolor=GRID, tickfont=dict(color=MUTED, size=11),
                   range=[x_lo, x_hi]),
        yaxis=dict(title=y_feat, gridcolor=GRID, linecolor=GRID,
                   zerolinecolor=GRID, tickfont=dict(color=MUTED, size=11),
                   range=[y_lo, y_hi]),
        hovermode='closest',
    )
    return fig


server = app.server

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
