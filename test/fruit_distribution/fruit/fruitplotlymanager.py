# Copyright IBM All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Dict, Tuple, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np
# from dse_do_utils.datamanager import DataManager
from dse_do_utils.plotlymanager import PlotlyManager

from .fruitdatamanager import FruitDataManager


class FruitPlotlyManager(PlotlyManager):
    """Holds method that create Plotly charts.
    Pass-in the DM as an input in the constructor.
    """

    def __init__(self, dm: FruitDataManager):
        super().__init__(dm)

    def plotly_demand_pie(self):
        """Pie chart of demand quantities.
        Input tables: ['Demand']
        Output tables: []
        """

        df = (self.dm.demand
              )

        labels = {'product': 'Product Name', 'demand': 'Demand'}
        fig = px.pie(df.reset_index(), values='demand', names='product',
                     title='Total product demand', labels=labels)

        return fig

    def plotly_demand_vs_inventory_bar(self):
        """Bar chart of demand vs inventory quantities.
        Input tables: ['Demand', 'Inventory']
        Output tables: []
        """
        df = (self.dm.demand.join(self.dm.inventory).groupby(['product']).sum()
              .reset_index()
              .melt(id_vars=['product'], var_name='source', value_name='quantity')
              )
#         display(df.head())
        labels = {'product': 'Product Name', 'demand': 'Demand', 'inventory': 'Inventory', 'quantity':'Quantity'}
        fig = px.bar(df.reset_index(), x="product", y="quantity", title="Demand vs Inventory",
                     color="source", barmode='group',
                     labels=labels
                     )  # , facet_row="timePeriodSeq")
#         fig.update_xaxes(type='category')

        return fig

    @staticmethod
    def make_traffic_light_gauge(value: float, title: str, orange_threshold: float, red_threshold: float, max_val: float):
        """
        TODO: move to PlotlyManager?
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
