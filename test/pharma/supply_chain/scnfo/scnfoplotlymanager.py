from typing import List, Dict, Tuple, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np

from dse_do_utils.datamanager import DataManager
from supply_chain.scnfo.scnfodatamanager import ScnfoDataManager


class PlotlyManager():
    """Holds method that create Plotly charts.
    Pass-in the DM as an input in the constructor.
    """
    def __init__(self, dm:DataManager):
        self.dm = dm

    def get_plotly_fig_m(self, id):
        """On the instance `self`, call the method named by id['index']
        For use with pattern-matching callbacks. Assumes the id['index'] is the name of a method of this class and returns a fig.
        """
        return getattr(self, id['index'])()

    def get_dash_tab_layout_m(self, page_id):
        """On the instance `self`, call the method named by get_tab_layout_{page_id}
        """
        return getattr(self, f"get_tab_layout_{page_id}")()


class ScnfoPlotlyManager(PlotlyManager):
    """Holds method that create Plotly charts.
    Pass-in the DM as an input in the constructor.
    """
    def __init__(self, dm: ScnfoDataManager):
        super().__init__(dm)

    def plotly_production_plant_time_bar(self):
        """Bar chart of production quantities per Plant over TimePeriod.
        Input tables: ['ProductionActivity', 'Location']
        Output tables: []
        """
        df = self.dm.production_activities.reset_index().merge(self.dm.locations.reset_index(), on='locationName').groupby(
            ['timePeriodSeq', 'plantName']).sum()
        labels = {'timePeriodSeq': 'Time Period', 'xProdSol': 'Production', 'productName': 'Product Name'}
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="xProdSol", color="plantName", title="Production",
                     labels=labels)  # , facet_row="timePeriodSeq")
        fig.update_xaxes(type='category')
        return fig

    def plotly_production_product_time_bar(self):
        """Bar chart of production quantities per Product over TimePeriod.
        Input tables: ['ProductionActivity', 'Location']
        Output tables: []
        """
        df = self.dm.production_activities.reset_index().merge(self.dm.locations.reset_index(), on='locationName').groupby(
            ['timePeriodSeq', 'productName']).sum()
        labels = {'timePeriodSeq': 'Time Period', 'xProdSol': 'Production', 'productName': 'Product Name'}
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="xProdSol", color="productName", title="Production",
                     labels=labels)  # , facet_row="timePeriodSeq")
        fig.update_xaxes(type='category')
        return fig

    def plotly_animated_demand_map(self, query=None):
        """Plotly map of US with demand locations.
        Input tables: ['Location']
        Output tables: ['DemandInventory']
        """
        df = self.dm.demand_inventories.groupby(['locationName', 'timePeriodSeq']).agg(
            quantity=pd.NamedAgg(column='quantity', aggfunc='sum'),
        )
        df = df.join(self.dm.locations).reset_index()
        fig = px.scatter_geo(df, lat="latitude", lon="longitude", color="quantity",
                             hover_name="city", size="quantity",
                             animation_frame="timePeriodSeq",
                             projection="equirectangular", width=1200, height=800,
                             #                      text='city'
                             #                      locationmode = 'USA-states',
                             size_max=40,
                             )
        fig.update_layout(
            title='Demand',
            # geo_scope='north america',
        )
        return fig

    def plotly_animated_supply_map(self, query=None):
        """Plotly map of US with production locations. Animated
        """
        df = self.dm.production_activities.groupby(['locationName', 'timePeriodSeq']).agg(
            quantity=pd.NamedAgg(column='xProdSol', aggfunc='sum'),
            cost=pd.NamedAgg(column='production_cost', aggfunc='sum'),
        )
        df = df.join(self.dm.locations).reset_index()
        fig = px.scatter_geo(df, lat=df.latitude, lon=df.longitude, color="quantity",
                             hover_name="city", size="quantity",
                             animation_frame="timePeriodSeq",
                             #                      projection="equirectangular",
                             #                      locationmode = 'USA-states',
                             width=1200, height=800,
                             size_max=50,
                             #                      hover_data = ['timePeriodSeq','quantity']  # 'locationName',
                             hover_data={'longitude': False, 'latitude': False, 'quantity': ':,'},
                             text='city'
                             )
        fig.update_layout(
            title='Production',
            # geo_scope='usa',
        )

        # Note: override hovertemplate does NOT work in combination with animation
        #     print("plotly express hovertemplate:", fig.data[0].hovertemplate)
        #     fig.update_traces(hovertemplate='<b>%{hovertext}</b><br><br>quantityy=%{marker.color:,}<extra></extra>') #
        #     print("plotly express hovertemplate:", fig.data[0].hovertemplate)
        #     show_fig(fig)
        return fig







    ###############################################
    # Demand
    ###############################################
    def describe_demand(self):
        """Print summary of demand statistics.
        TODO: ensure there is always a 'productGroup'?
        Input tables: ['Demand']
        Output tables: []
        """
        df = (self.dm.demand
#               .join(self.dm.products[['productGroup']])
              .reset_index())
        print(f"Demand entries = {df.shape[0]:,}")
        print(f"Num products = {len(df.productName.unique()):,}")
#         print(f"Num productGroup types = {len(df.productGroup.unique()):,}")
        print(f"Num locations = {len(df.locationName.unique()):,}")
        print(f"Num time-periods = {len(df.timePeriodSeq.unique()):,}")

    def plotly_demand_bars(self):
        """Product demand over time. Colored by productGroup.
        Input tables: ['Product', 'Demand']
        Output tables: []
        """
        product_aggregation_column = 'productGroup'
        df = (self.dm.demand
              .join(self.dm.products[['productGroup']])
              ).groupby(['timePeriodSeq', product_aggregation_column]).sum()
        #     display(df.head())

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name',
                  'productGroup': 'Product Group'}
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="quantity", color=product_aggregation_column,
                     title='Total Product Demand', labels=labels)
        fig.update_layout(
            # title={
            #     'text': f"Total product demand",
            #     # 'y': 0.9,
            #     # 'x': 0.5,
            #     'xanchor': 'center',
            #     'yanchor': 'top'},
            legend={'orientation': 'v'},
            # legend_title_text=product_aggregation_column,
        )

        return fig





    ###############################################
    # Production Capacity
    ###############################################
    def describe_production_assets(self):
        """Print statistics on production capacity.
        Input tables: ['RecipeProperties', 'Line', 'Plant','Location']
        Output tables: []
        """
        df = (self.dm.recipe_properties[['capacity', 'cost']]
              .join(self.dm.lines)
              .join(self.dm.plants.rename(columns={'locationDescr': 'plantDescr'}), on='plantName')
              .join(self.dm.locations, on='locationName')
              .reset_index()
              )
        #     display(df.head())
        print(f"Total Recipe Properties = {df.shape[0]:,}")
        print(f"Total Time Periods = {len(df.timePeriodSeq.unique()):,}")
        print(f"Total Products = {len(df.productName.unique()):,}")
        print(f"Total Lines = {len(df.lineName.unique()):,}")
        print(f"Total Plants = {len(df.plantName.unique()):,}")
        print(f"Max Capacity = {df.capacity.max():,}")
        print(f"Min Capacity = {df.capacity.min():,}")
        print(f"Max Cost = {df.cost.max():0,.4f}")
        print(f"Min Cost = {df.cost.min():0,.4f}")

    def plotly_capacity_sunburst(self):
        """Sunburst of production capacity:
        State->Plant->Line
        Input tables: ['RecipeProperties', 'Line', 'Plant','Location']
        Output tables: []
        """
        df = (self.dm.recipe_properties[['capacity']]
              .join(self.dm.lines)
              .join(self.dm.plants.rename(columns={'locationDescr': 'plantDescr'}), on='plantName')
              .join(self.dm.locations, on='locationName')
              ).groupby(['lineName', 'plantName', 'city', 'state', 'country']).max()
        #     display(df.head())

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'demand', 'productName': 'Product Name'}
        fig = px.sunburst(df.reset_index(), path=['state', 'plantName', 'lineName'], values='capacity', labels=labels,
                          height=500)

        fig.update_layout(
            title={
                'text': "Maximum Line Capacity",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        return fig




    ###############################################
    # Production Activities
    ###############################################
    def plotly_excess_utilization_multi_facet_bars(self):
        """Line utilization bar per line over time, clustered by time-period.
        Excess utilization over 100% is clearly colored as red.
        Good initial view of utilization and excess utilization.
        Input tables: []
        Output tables: ['LineUtilization]
        """
        df = (self.dm.line_utilization.copy()
              )
        df['Regular Capacity'] = df.utilization.clip(0, 1)
        df['Over Capacity'] = (df.utilization - 1).clip(0)
        df = df[['Regular Capacity', 'Over Capacity']]
        df = (df.stack()
              .rename_axis(index={None: 'var_name'})
              .to_frame(name='Utilization')
              .reset_index()
              )
        #     display(df.head())

        labels = {'timePeriodSeq': 'Time Period', 'var_name': 'Utilization Type', 'lineName': 'Line Name'}
        fig = px.bar(df.reset_index(), x="lineName", y="Utilization", color='var_name', title='Line Utilization',
                     labels=labels,
                     facet_col="timePeriodSeq",
                     #                  width = 2000
                     color_discrete_map = {'Regular Capacity':'green', 'Over Capacity':'red'},
                     )
        fig.update_layout(
            legend=
                dict( # change legend location
                    title = "Utilization Type", 
                    orientation="h",
                    yanchor="top",
                    y=1.20,
                    xanchor="right",
                    x=0.95),
            # legend_title_text=None # this doesn't align the legend still
        )
        fig.update_layout(yaxis=dict(tickformat="%", ))
        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        return fig

    def plotly_excess_utilization_line_time_bars(self):
        """Line utilization bar per line over time, clustered by time-period.
        Excess utilization over 100% is clearly colored as red.
        Good initial view of utilization and excess utilization.
        Input tables: []
        Output tables: ['LineUtilization]
        """
        df = (self.dm.line_utilization.copy()
              )
        df['Regular Capacity'] = df.utilization.clip(0, 1)
        df['Over Capacity'] = (df.utilization - 1).clip(0)
        df = df[['Regular Capacity', 'Over Capacity']]
        df = (df.stack()
              .rename_axis(index={None: 'var_name'})
              .to_frame(name='Utilization')
              .reset_index()
              )
        #     display(df.head())

        labels = {'timePeriodSeq': 'Time Period', 'var_name': 'Utilization Type', 'lineName': 'Line Name'}
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="Utilization", color='var_name', title='Line Utilization',
                     labels=labels,
                     facet_row="lineName",
                     #                  width = 2000
                     color_discrete_map = {'Regular Capacity':'green', 'Over Capacity':'red'},
                     )
        fig.update_layout(
            legend=
            dict( # change legend location
                title = "Utilization Type",
                orientation="h",
                yanchor="top",
                y=1.20,
                xanchor="right",
                x=0.95),
            # legend_title_text=None # this doesn't align the legend still
        )
        fig.update_layout(yaxis=dict(tickformat="%", ))
        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        return fig



    ###############################################
    # Transportation Activities
    ###############################################


    def plotly_production_activities_sankey(self):
        """Sankey diagram of production activities.
        See https://stackoverflow.com/questions/50486767/plotly-how-to-draw-a-sankey-diagram-from-a-dataframe
        """
        # Create productName vs id
        product_labels_df = (self.dm.products[[]].reset_index()
                             .reset_index().rename(columns={'index': 'id'})
                             )
        # Sankey based on production_activities
        df = (self.dm.production_activities[['xProdSol']]
              .query("xProdSol > 0")
              #      .join(dm.products[['stage']])
              .join(self.dm.bom_items[['quantity']].rename(columns={'quantity':'component_bom_quantity'}))
              )
        df['component_quantity'] = df.xProdSol * df.component_bom_quantity
        df = (df
              .drop(columns=['component_bom_quantity'])
              .groupby(['componentName', 'productName','lineName']).sum()
              )

        df = df.reset_index()
        #     display(df.head())

        # Set pop-up text
        df['label'] = df.productName + " - " + df.lineName

        df = (df.merge(product_labels_df, left_on='productName', right_on='productName')
              .rename(columns={'id': 'target'})
              )
        #     display(df.head())
        df = (df.merge(product_labels_df, left_on='componentName', right_on='productName', suffixes=[None,'_y'])
              .drop(columns=['productName_y'])
              .rename(columns={'id': 'source'})
              )
        #     display(df.head())

        product_labels_df['color_nodes'] = np.where(product_labels_df.productName == 'Tablet', 'rgba(63, 191, 63, 0.9)',
            np.where(product_labels_df.productName == 'Granulate', "rgba(185, 2, 103, 0.95)", 
            np.where(product_labels_df.productName == 'API', "rgba(251, 33, 44, 0.9)", "rgba(43, 155, 247, 0.92)")))

        df['color_links'] = np.where(df.componentName == 'Tablet', 'rgba(63, 191, 63, 0.45)',
            # np.where(df.componentName == 'Granulate', "rgba(63, 191, 191, 0.45)", 
            np.where(df.componentName == 'API', "rgba(251, 33, 44, 0.45)", "rgba(43, 155, 247, 0.45)"))
            #)

        fig = go.Figure(data=[go.Sankey(
            arrangement ='snap',
            #         valueformat = ".0f",
            #         valuesuffix = "TWh",
            #         Define nodes
            node=dict(
                pad=15,
                thickness=15,
                line=dict(color="black", width=0.5),
                label=product_labels_df.productName.array,
                color=product_labels_df.color_nodes.array,
                #           color =  data['data'][0]['node']['color']
            ),
            # Add links
            link=dict(
                source=df.source.array,
                target=df.target.array,
                value=df.xProdSol.array,
                label=df.label.array,
                color=df.color_links.array,
                line=dict(color="black", width=0.25),
                #           label =  data['data'][0]['link']['label'],
                #           color =  data['data'][0]['link']['color']
            ))])

        fig.update_layout(
            # title_text="Production",
                          font_size=10,
        )
                        #   height=800)
        return fig

    def plotly_transportation_activities_sankey(self):
        """Sankey diagram of transportation activities.
        See https://stackoverflow.com/questions/50486767/plotly-how-to-draw-a-sankey-diagram-from-a-dataframe
        Input tables: ['Location']
        Output tables: ['TransportationActivity']
        """
        # Create locationName vs id
        location_labels_df = (self.dm.locations[[]].reset_index()
                              .reset_index().rename(columns={'index': 'id'})
                              )
        # Sankey based on transportation_activities
        df = (self.dm.transportation_activities[['xTransportationSol']]
              .query("xTransportationSol > 0")
              .groupby(['originLocationName', 'destinationLocationName','shippingMode','productName']).sum()
              )
        df = df.reset_index()
        #     display(df.head())

        df = (df.merge(location_labels_df, left_on='originLocationName', right_on='locationName')
              .rename(columns={'id': 'source'})
              .drop(columns=['locationName'])
              )
        #     display(df.head())
        df = (df.merge(location_labels_df, left_on='destinationLocationName', right_on='locationName')
              .rename(columns={'id': 'target'})
              .drop(columns=['locationName'])
              )
        # display(df.head())

        # Set pop-up text
        df['label'] = df.productName + " - " + df.shippingMode

        location_labels_df['color_nodes'] = np.where(location_labels_df.locationName == 'Abbott_Olst_Plant', 'rgba(63, 191, 63, 0.9)',
            np.where(location_labels_df.locationName == 'Abbott_WH_NL', "rgba(63, 191, 191, 0.9)", 
            np.where(location_labels_df.locationName == 'Abbott_Weesp_Plant', "rgba(251, 33, 44, 0.9)", "rgba(43, 155, 247, 0.92)")))

        df['color_links'] = np.where(df.originLocationName == 'Abbott_Olst_Plant', 'rgba(63, 191, 63, 0.45)',
            np.where(df.originLocationName == 'Abbott_WH_NL', "rgba(63, 191, 191, 0.45)", 
            np.where(df.originLocationName == 'Abbott_Weesp_Plant', "rgba(251, 33, 44, 0.45)", "rgba(43, 155, 247, 0.45)")))

        # print(df.head())
        fig = go.Figure(data=[go.Sankey(
            arrangement ='snap',
            #         valueformat = ".0f",
            #         valuesuffix = "TWh",
            #         Define nodes
            node=dict(
                pad=15,
                thickness=15,
                line=dict(color="black", width=0.5),
                label=location_labels_df.locationName.array,
                color = location_labels_df.color_nodes.array,
                #           color =  data['data'][0]['node']['color']
            ),
            # Add links
            link=dict(
                source=df.source.array,
                target=df.target.array,
                value=df.xTransportationSol.array,
                line=dict(color="black", width=0.25),
                label=df.label.array,
                color=df.color_links.array,
                #           label =  data['data'][0]['link']['label'],
                #           color =  data['data'][0]['link']['color']
            ))])

        fig.update_layout(
            # title_text="Transportation",
                          font_size=10,
        )
                        #   height=800)
        return fig
