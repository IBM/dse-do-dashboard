# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List, NamedTuple

import pandas as pd
from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import dash_ag_grid as dag
from dash import html

from dse_do_dashboard.do_dash_app import DoDashApp
from dse_do_dashboard.visualization_pages.visualization_page import VisualizationPage
from dse_do_utils.plotlymanager import PlotlyManager

# from fruit_distribution.fruit.fruitplotlymanager import FruitPlotlyManager


class KpiPageTemplate(VisualizationPage):
    """Abstract class. Creates a layout of KPI gauges with multiple rows of KPI gauges.
    Override the method `get_plotly_figures`.
    """
    def __init__(self, dash_app: DoDashApp, page_name: str = 'Default', page_id: str = 'default', url: str = 'default',
                 input_table_names=None, output_table_names=None, include_kpi_grid: bool = False, **kwargs):
        if output_table_names is None:
            output_table_names = []
        if input_table_names is None:
            input_table_names = []
        self.include_kpi_grid = include_kpi_grid
        super().__init__(dash_app=dash_app,
                         page_name=page_name,
                         page_id=page_id,
                         url=url,
                         input_table_names=input_table_names,
                         output_table_names=output_table_names,
                         **kwargs
                         )

    def get_plotly_figures(self, pm: PlotlyManager) -> List[List[go.Figure]]:
        """Create gauges for KPI page as rows of columns.
        That is, each entry in the gauges represents a row. Each row contains a set of go.Figure.

        Abstract method. This is just a sample of a 2x2 matrix of KPIs. Override to """
        kpi_df = pm.dm.kpis
        gauges = [
            [
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 1 %",
                    value=round(.88 * 100, 3),
                    orange_threshold=75,
                    red_threshold=90,
                    max_val=100),
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 2",
                    value=55,
                    orange_threshold=75,
                    red_threshold=90,
                    max_val=100),
            ],
            [
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 3 %",
                    value=round(.33 * 100, 3),
                    orange_threshold=25,
                    red_threshold=50,
                    max_val=100),
                KpiPageTemplate.make_traffic_light_gauge(
                    title="KPI 4",
                    value=777,
                    orange_threshold=750,
                    red_threshold=900,
                    max_val=1000),
            ],
        ]
        return gauges

    def get_layout_children(self, pm: PlotlyManager):
        """Creates a layout for KPI gauges with multiple rows and columns.
        Each row can contain any number of columns."""
        figures = self.get_plotly_figures(pm=pm)

        figure_style = {'height': '20vh', 'width': '20vw', 'margin-left': 'auto', 'margin-right': 'auto',
                       'display': 'block'}
        layout_childen = []

        for figure_row in figures:
            row_layout = dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody(
                            dcc.Graph(
                                style=figure_style,
                                figure=figure
                            )
                        )
                    ])
                )
                for figure in figure_row
            ])
            layout_childen.append(row_layout)

        if self.include_kpi_grid:
            kpi_grid = self.get_kpi_grid(pm)
            grid_layout = html.Div([kpi_grid])
            layout_childen.append(grid_layout)

        return layout_childen

    @staticmethod
    def make_traffic_light_gauge(value: float, title: str, orange_threshold: float, red_threshold: float, max_val: float):
        """
        """
        steps = [
            {'range': [0, orange_threshold], 'color': 'green'},
            {'range': [orange_threshold, red_threshold], 'color': 'orange'},
            {'range': [red_threshold, max_val], 'color': 'red'},
        ]

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, .75]},
            title = {'text': title, 'font': {'color': 'black', 'size': 18}},
            gauge = {'axis': {'range': [None, max_val], 'tickfont': {'color': 'black'}},
                     'threshold' : {'line': {'color': "darkred", 'width': 4}, 'thickness': 0.75, 'value': red_threshold},
                     'steps': steps,
                     'bar': {'color': "darkblue"},},
        ))

        fig.update_layout(font = {'color': 'green' if value < orange_threshold else 'orange' if value > orange_threshold and value < red_threshold else 'red', 'family': "Arial"},
                          margin={'t':10,'b':30},
                          )

        return fig

    @staticmethod
    def make_traffic_light_gauge_v2(value: float, title: str, low_threshold: float, medium_threshold: float, max_val: float, reverse: bool=False) -> go.Figure:
        """
        Create a traffic-light-style gauge.
        Parameters
        ----------
        value : float
            The value to display on the gauge.
        title : str
            The title of the gauge.
        low_threshold : float
            The threshold for the low (green) range.
        medium_threshold : float
            The threshold for the medium (orange) range.
        max_val : float
            The maximum value of the gauge.
        reverse : bool
        """
        if reverse:
            low_color = 'red'
            med_color = 'orange'
            high_color = 'green'
        else:
            low_color = 'green'
            med_color = 'orange'
            high_color = 'red'

        steps = [
            {'range': [0, low_threshold], 'color': low_color},
            {'range': [low_threshold, medium_threshold], 'color': med_color},
            {'range': [medium_threshold, max_val], 'color': high_color},
        ]

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, .75]},
            title = {'text': title, 'font': {'color': 'black', 'size': 18}},
            gauge = {'axis': {'range': [None, max_val], 'tickfont': {'color': 'black'}},
                     'threshold' : {'line': {'color': "darkred", 'width': 4}, 'thickness': 0.75, 'value': medium_threshold},
                     'steps': steps,
                     'bar': {'color': "darkblue"},},
        ))

        fig.update_layout(font = {'color': low_color if value < low_threshold else med_color if value > low_threshold and value < medium_threshold else high_color, 'family': "Arial"},
                          margin={'t':10,'b':30},
                          )

        return fig



    def get_kpi_grid(self, pm: PlotlyManager, format_num_decimals: int = 3) -> dag.AgGrid:
        """Create a grid for the KPI data."""

        if pm.get_multi_scenario_compare_selected():
            kpis = pm.get_multi_scenario_table('kpis').drop(columns=['scenario_seq'])
        elif pm.get_reference_scenario_compare_selected():
            ref_df = pm.ref_dm.kpis.reset_index()
            ref_df['scenario_name'] = 'Reference'
            selected_df = pm.dm.kpis.reset_index()
            selected_df['scenario_name'] = 'Current'
            kpis = pd.concat([selected_df, ref_df])
        else:
            kpis = pm.dm.kpis.reset_index()
            kpis['scenario_name'] = 'Current'
        df = kpis.copy().rename(columns={'NAME': 'kpi', 'VALUE': 'value'})


        if pm.dm.business_kpis is not None and not pm.dm.business_kpis.empty:
            if pm.get_multi_scenario_compare_selected():
                business_kpis = pm.get_multi_scenario_table('BusinessKpi').drop(columns=['scenario_seq'])
            elif pm.get_reference_scenario_compare_selected():
                ref_df = pm.ref_dm.business_kpis.reset_index()
                ref_df['scenario_name'] = 'Reference'
                selected_df = pm.dm.business_kpis.reset_index()
                selected_df['scenario_name'] = 'Current'
                business_kpis = pd.concat([selected_df, ref_df])
            else:
                business_kpis = pm.dm.business_kpis.reset_index()
                business_kpis['scenario_name'] = 'Current'
            business_kpis = business_kpis.copy()
            df = pd.concat([df, business_kpis], axis=0)
            df = df.drop_duplicates(subset=['kpi','scenario_name'], keep='first')  # Drop duplicate KPIs, keep the first occurrence


        # # Convert long DataFrame with columns 'kpi', 'value', and 'scenario_name' to wide format: index='kpi', columns='scenario_name', values='value'
        df = df.pivot(index='kpi', columns='scenario_name', values='value').reset_index()
        
        # Fill NaN values with 0 or empty string depending on your preference
        # Option 1: Fill with 0 for numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Option 2: If you prefer to keep NaN as empty or show as text, comment out the above and use:
        # df = df.fillna('')


        # Bob - 2026-03-31:
        # Fixed the issue where column headers containing dots caused NaN values in AgGrid.
        # Root Cause:
        # AG Grid interprets dots in field names as nested object paths (e.g., "scenario.name" tries to access row.scenario.name instead of row["scenario.name"]).
        # Solution Applied:
        # Added valueGetter functions to all column definitions that use bracket notation to properly access column data:
        # - For numeric columns: 'valueGetter': {"function": f"params.data['{c}']"}
        # - For the 'kpi' column: 'valueGetter': {"function": "params.data['kpi']"}
        # This ensures that column names with dots are treated as literal strings rather than nested object paths, allowing the data to display correctly instead of showing NaN values.

        column_def_override = {
            c: {'field': c, 'headerName': c,
                # 'type': ['numericColumn'],
                'type': 'numericColumn',
                'valueFormatter': {"function": f"d3.format(',.{format_num_decimals}~f')(params.value)"},
                'valueGetter': {"function": f"params.data['{c}']"}
                } if c != 'kpi' else {'field': 'kpi', 'headerName': 'KPI', 'pinned': 'left', 'valueGetter': {"function": "params.data['kpi']"}}
            for c in df.columns
        }
        # column_def_override = {}

        columns_in_grid = df.columns
        columns_in_data = columns_in_grid
        columnDefs = [column_def_override[c] if c in column_def_override.keys() else {'field': c} for c in
                      columns_in_grid]

        defaultColDef = {
            'editable': False,
            # make every column use 'text' filter by default
            "filter": "agTextColumnFilter",
            "columnSize": "autoSize",
            "columnSizeOptions": {"skipHeader": True},

        }

        grid = dag.AgGrid(
            id="basic-df-grid",
            rowData=df[columns_in_data].to_dict("records"),
            columnDefs=columnDefs,
            dashGridOptions={'pagination': True, "rowHeight": 30, 'alwaysMultiSort': True},
            defaultColDef=defaultColDef,
            style={"height": 600, "width": '100%'},
            columnSize="autoSize",
            # columnSizeOptions={"skipHeader": False},
        )
        return grid