from typing import List, Dict, Tuple, Optional
import pandas as pd

from supply_chain.pharma.pharmadatamanager import PharmaDataManager
from supply_chain.scnfo.scnfoplotlymanager import ScnfoPlotlyManager

import plotly.express as px
import plotly.graph_objs as go
import numpy as np

from dse_do_dashboard.utils.dash_common_utils import plotly_figure_exception_handler

#######################################################################################
# Pharma
#######################################################################################


class PharmaPlotlyManager(ScnfoPlotlyManager):
    def __init__(self, dm:PharmaDataManager):
        super().__init__(dm)
        # self.line_name_category_orders = ['Abbott_Weesp_Line','Abbott_Olst_Granulate_Line',
        #                                 'Abbott_Olst_Packaging_Line_5','Abbott_Olst_Packaging_Line_6']
        # self.plant_name_category_orders = ['Abbott_Weesp_Plant', 'Abbott_Olst_Plant']

        self.line_name_category_orders = ['API_Line','Granulate_Line', 'Packaging_Line_1','Packaging_Line_2']
        self.plant_name_category_orders = ['API_Plant', 'Packaging_Plant']
        
    def describe_demand(self):
        """Print summary of demand statistics."""
        super().describe_demand()
        df = (self.dm.demand
              .join(self.dm.products[['productGroup']])
              .reset_index())
        print(f"Num product types = {len(df.productGroup.unique()):,}")

    # def plotly_demand_bars(self):
    #     """Product demand over time. Colored by productGroup."""
    #     product_aggregation_column = 'productGroup'
    #     df = (self.dm.demandplotly_production_activities_bars
    #           .join(self.dm.products[['productGroup']])
    #           ).groupby(['timePeriodSeq', product_aggregation_column]).sum()
    #     #     display(df.head())
    #
    #     labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name',
    #               'productGroup': 'Product Group'}
    #     fig = px.bar(df.reset_index(), x="timePeriodSeq", y="quantity", color=product_aggregation_column,
    #                  title='Total Product Demand', labels=labels)
    #     fig.update_layout(
    #         # title={
    #         #     'text': f"Total product demand",
    #         #     # 'y': 0.9,
    #         #     # 'x': 0.5,
    #         #     'xanchor': 'center',
    #         #     'yanchor': 'top'},
    #         legend={'orientation': 'v'},
    #         # legend_title_text=product_aggregation_column,
    #     )
    #
    #     return fig

    def gen_color_col(self, catSeries = None):
        '''Converts a series into a set of color codes
        NEEDS TO BE CALLED ON ENTIRE SERIES, NOT SUBSETTED VERSION
        '''

        cmap = ["#004172", "#08539d", "#2e64c7", "#be35a0", "#e32433", "#eb6007",
        "#fb8b00", "#c19f00", "#5c9c00", "#897500", "#cb0049", "#7746ba", "#0080d1",
        "#3192d2", "#ac6ac0", "#e34862", "#c57e00", "#71a500",  "#ad6e00", "#b82e2e",]

        color_dict = {
            'Other': "#7FB3D5",
            'API': "#B03A2E",
            ' - API': "#B03A2E",
            'Granulate': "#1F618D",
            'Tablet': "#117A65",
            'Package': "#B7950B",
            }
        
        if catSeries is not None:
            catSeries = catSeries.dropna() # some NAs get introduced for some reason
            labels = list(catSeries.unique())

            if ' - API' not in labels or 'API' not in labels:
                labels.append(' - API')
            
            
            labels = sorted(labels)

            cmap_ix = 0

            for ix in range(len(labels)):
                if cmap_ix == len(cmap):
                    cmap_ix = 0
                else:
                    if 'Granulate' in labels[ix]:
                        color_dict[labels[ix]] = "#1F618D"
                    elif 'Tablet' in labels[ix]:
                        color_dict[labels[ix]] =  "#117A65"
                    elif 'Package' in labels[ix]:
                        color_dict[labels[ix]] =  "#B7950B"
                    elif 'API' in labels[ix]:
                        color_dict[labels[ix]] = "#B03A2E"

                    if labels[ix] not in color_dict:
                        color_dict[labels[ix]] = cmap[cmap_ix]
                        cmap_ix += 1 
        
        return color_dict

    def plotly_demand_bars(self, query=None, title='Total Product Demand', view = "All"):
        """Product demand over time. Colored by productGroup."""
        product_aggregation_column = 'productName'
        
        df = (self.dm.demand
            .join(self.dm.products[['productGroup', 'productCountry']])
            )

        # df = (self.dm.demand # will return two dfs
        #     .join(self.dm.products[['productGroup', 'productCountry']])
        #     )

        df = df.reset_index()  

        df['productCountry'] = np.where(pd.isnull(df.productCountry), '', df.productCountry)

        df['location_product'] = df.productCountry + " - " + df.productName

        color_discrete_map = self.gen_color_col(df.location_product)

        if query is not None:
            df = df.query(query).copy()

        # Set location_product name
        df = df.reset_index()

        df = (df
              .groupby(['timePeriodSeq', 'location_product']).sum()
              .sort_values('quantity', ascending=False)
              )

        df['demand_proportion'] = df.groupby(['timePeriodSeq'])['quantity'].apply(lambda x: x/x.sum())

        df = df.reset_index()

        df['new_labels'] = np.where(df['demand_proportion'] < 0.015, 'Other', df['location_product'])

        # cmap = px.colors.qualitative.Light24  

        new_labels = df['new_labels'].unique()

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name',
                  'productGroup': 'Product Group'}

        if view == "All":
            color = "location_product"
        elif view == "Compact":
            color = "new_labels"

        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="quantity", 
                    color= color,
                    title=title, labels=labels,
                    #  color_discrete_sequence=px.colors.qualitative.Light24,
                    color_discrete_map=color_discrete_map,
                    height=600,
                    hover_name="location_product",
                    # hover_data=["quantity"]
                     )

        fig.update_layout(
            legend={
                'title': f"Total Product Demand",
                'bgcolor':'rgba(0,0,0,0)', # transparent background? not sure if this works
                'x': 1,
                'orientation': 'v'},
            margin = {'l':80,'t':50},
            hovermode="closest",
        )
        return fig

    def plotly_utilization_multi_facet_bars(self):
        """Line utilization colored by groupID.
        Shows which groupIDs claim how much capacity on which lines.
        Could be used to analyze why certain lines cannot produce enough of a given product,
        i.e. that they are busy with other products."""
        product_aggregation_column = 'productGroup'

        df = (self.dm.production_activities[['line_capacity_utilization']]
            .join(self.dm.products[['productGroup']])
            ).groupby(['timePeriodSeq', 'lineName', product_aggregation_column]).sum()
        
        labels = {'timePeriodSeq': 'Time Period', 'var_name': 'Utilization Type', 'lineName': 'Line Name',
                  'line_capacity_utilization': 'Line Capacity Utilization'}

        fig = px.bar(df.reset_index(), x="lineName", y="line_capacity_utilization", color=product_aggregation_column,
                    title='Line Utilization', labels=labels,
                    facet_col="timePeriodSeq",
                    )
        # get rid of duplicated X-axis labels
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.XAxis:
                fig.layout[axis].title.text = ''     

        # fig.for_each_trace(lambda t: t.update(name=t.name.split()[-1]))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split()[-1]))
        
        fig.update_layout(yaxis=dict(tickformat="%", ))
        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        
        fig.update_layout(
            legend=
                dict( # change legend location
                    title = "Product Group", 
                    orientation="h",
                    yanchor="top",
                    y=1.3,
                    xanchor="right",
                    x=0.95),
        
            # legend_title_text=None # this doesn't align the legend still
        )
        
        return fig
    
    def plotly_excess_utilization_line_time_bars(self):
        """Line utilization bar per line over time, clustered by time-period.
        Excess utilization over 100% is clearly colored as red.
        Good initial view of utilization and excess utilization.
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

        labels = {'timePeriodSeq': 'Time Period', 'var_name': 'Utilization Type', 'lineName': 'Line Name'}
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="Utilization", color='var_name', title='Line Utilization',
                    labels=labels,
                    facet_row="lineName",
                    #                  width = 2000
                    color_discrete_map = {'Regular Capacity':'green', 'Over Capacity':'red'},
                    height = 800,
                    )

        fig.update_layout(
            legend=
                dict( # change legend location
                    title = "Utilization Type", 
                    orientation="h",
                    yanchor="top",
                    y=1.05,
                    xanchor="right",
                    x=0.95),
        )
        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around

        ### This gets rid of the duplicated Y Axis labels caused by the facet_row argument
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ''
                fig.layout[axis].tickformat = '%'

        fig.for_each_annotation(lambda a: a.update(text=a.text.split("Line Name=")[-1]))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("_", " ")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Olst", "Olst<br>")))
        fig.for_each_annotation(lambda a: a.update(x = a.x-1.07, textangle = 270))

        fig.update_layout(
            legend=
            dict( # change legend location
                title = "Product Group",
                orientation="v",
                x=1.05,
                yanchor="top"
             ),
             margin = {'l' : 130, 't':80}
        )
        return fig

    def plotly_utilization_line_time_bars(self):
        """Line utilization colored by groupID.
        Shows which groupIDs claim how much capacity on which lines.
        Could be used to analyze why certain lines cannot produce enough of a given product,
        i.e. that they are busy with other products."""
        product_aggregation_column = 'productGroup'
        df = (self.dm.production_activities[['line_capacity_utilization']]
              .join(self.dm.products[['productGroup']])
              ).groupby(['timePeriodSeq', 'lineName', product_aggregation_column]).sum()

        color_discrete_map = self.gen_color_col()

        labels = {'timePeriodSeq': 'Time Period', 'var_name': 'Utilization Type', 'lineName': 'Line Name', 
                  'line_capacity_utilization':'Line Capacity Utilization'}
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="line_capacity_utilization", color=product_aggregation_column,
                     title='Line Utilization', labels=labels, facet_row = 'lineName',
                     color_discrete_map=color_discrete_map,
                     category_orders={
                        product_aggregation_column: ['API', 'Granulate', 'Tablet', 'Package'],
                        # 'lineName': ['Abbott_Weesp_Line', 'Abbott_Olst_Granulate_Line', 
                        #             'Abbott_Olst_Packaging_Line_5', 'Abbott_Olst_Packaging_Line_6' ],
                        'lineName' : self.line_name_category_orders,
                        'timePeriodSeq': df.reset_index().timePeriodSeq.sort_values().unique() },
                     height=800,
                     )

        fig.update_layout(
            legend=
            dict( # change legend location
                title = "Product Group",
                orientation="v",
                yanchor="top",
                y=1.1,
                xanchor="right",
                x=1.05),
            margin = {'l': 130,'t':80}
        )
        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        
        ### This gets rid of the duplicated Y Axis labels caused by the facet_row argument
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ''
                fig.layout[axis].tickformat = '%'

        fig.for_each_annotation(lambda a: a.update(x = a.x -1.07, textangle = 270))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("Line Name=")[-1]))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("_", " ")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Olst", "Olst<br>")))
        return fig

    def plotly_line_utilization_heatmap_v2(self):
        """
        Trying multiple traces to see if we can get a more clear color difference for utilization > 100%
        Can't get the hover to work with multiple traces
        """

        # product_aggregation_column = 'groupID'
        df = ((self.dm.production_activities
            )
         )

        df = df.pivot_table(values='line_capacity_utilization', index=['lineName'], columns=['timePeriodSeq'], aggfunc=np.sum)

        hovertemplate ='<b>Utilization: %{z:.1%}</b><br>Line: %{y} <br>Time Period: %{x} '
        trace = go.Heatmap(z=df.values, x=df.columns, y=df.index, colorscale='Portland', zmin = 0, zmid =1, hovertemplate=hovertemplate)  #colorscale='rdbu',
        fig = go.Figure(data=[trace], layout=go.Layout(width=1000, height=600))

        return fig
    
    def plotly_demand_fullfilment(self, mode=None):
        """Demand, Fulfilled, Unfulfilled, Backlog, BacklogResupply and Inventory over time, grouped by time-period.
        Colored by groupID.
        Very useful graph since it contains all critical variables at the demand locations. Good for explanation.
        """
        
        # Collect transportation activities into a destination location.
        # (later we'll do a left join to only select trnasportation into a demand location and ignore all other transportation activities)
        df0 = (self.dm.transportation_activities[['xTransportationSol']]
            .groupby(['productName', 'destinationLocationName', 'timePeriodSeq']).sum()
            .rename_axis(index={'destinationLocationName': 'locationName'})
            .rename(columns={'xTransportationSol':'Transportation'})
            )
    #     display(df0.head())
        
        product_aggregation_column = 'productGroup'
        df = (self.dm.demand_inventories[['quantity','xFulfilledDemandSol','xUnfulfilledDemandSol','xBacklogSol','xBacklogResupplySol','xInvSol']]
            .join(self.dm.products[['productGroup']])
            #           .join(self.dm.locations)
            .join(df0, how='left')
            ).groupby(['timePeriodSeq', product_aggregation_column]).sum()
        if 'relative_week' in df.columns:  # TODO: remove if not relevant anymore
            df = df.drop(columns=['relative_week'])
    #     display(df.head())
        df = (df
            # .drop(columns=['relative_week'])
            .rename(
            columns={'quantity': 'Demand', 'xFulfilledDemandSol': 'Fulfilled', 'xUnfulfilledDemandSol': 'Unfulfilled',
                    'xBacklogSol': 'Backlog', 'xBacklogResupplySol': 'Backlog Resupply', 'xInvSol': 'Inventory'})
            )
            
        df = (df.stack()
            .rename_axis(index={None: 'var_name'})
            .to_frame(name='quantity')
            .reset_index()
            )

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name', 'productGroup':'Product Group',
                'var_name': 'Var'}
        
        if mode is None:  #'bar_subplot_by_time'
            fig = px.bar(df, x="var_name", y="quantity", color=product_aggregation_column, title="Demand", labels=labels,
                    facet_col="timePeriodSeq",
                    category_orders={
                        'var_name': ['Demand', 'Transportation', 'Fulfilled', 'Unfulfilled', 'Backlog', 'Backlog Resupply',
                                    'Inventory']},
                    height=700
                    )
        elif mode == 'multi_line':
            fig = px.line(df, x="timePeriodSeq", y="quantity", color='var_name', title="Demand", labels=labels,
                facet_row=product_aggregation_column,
                height=700
                )
        elif mode == 'animated_horizontal_bars':
            fig = px.bar(df, y="var_name", x="quantity", color=product_aggregation_column, title="Demand", labels=labels,
    #                  facet_col="timePeriodSeq",
                    animation_frame="timePeriodSeq",
                    category_orders={
                        'var_name': ['Demand', 'Transportation', 'Fulfilled', 'Unfulfilled', 'Backlog', 'Backlog Resupply',
                                    'Inventory']},
                    height=700
                    )
        elif mode == 'animated_vertical_bars':
            fig = px.bar(df, x="timePeriodSeq", y="quantity", color=product_aggregation_column, title="Demand", labels=labels,
    #                  facet_col="timePeriodSeq",
                    animation_frame="timePeriodSeq",
                    facet_row = 'var_name',
                    category_orders={
                        'var_name': ['Demand', 'Transportation', 'Fulfilled', 'Unfulfilled', 'Backlog', 'Backlog Resupply',
                                    'Inventory']},
                    height=700
                    )

        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        
        return fig

    def plotly_demand_fullfilment_multi_plot(self, mode=None, var_names=None):
        """Demand, Fulfilled, Unfulfilled, Backlog, BacklogResupply and Inventory over time, grouped by time-period.
        Colored by groupID.
        Very useful graph since it contains all critical variables at the demand locations. Good for explanation.
        """

        # Collect transportation activities into a destination location.
        # (later we'll do a left join to only select trnasportation into a demand location and ignore all other transportation activities)
        df0 = (self.dm.transportation_activities[['xTransportationSol']]
               .groupby(['productName', 'destinationLocationName', 'timePeriodSeq']).sum()
               .rename_axis(index={'destinationLocationName': 'locationName'})
               .rename(columns={'xTransportationSol':'Transportation'})
               )
        #     display(df0.head())

        # print(f"products in demand = {self.dm.demand_inventories.index.get_level_values('productName').unique()}")
        # print(f"products = {self.dm.products[['productGroup', 'productCountry']]}")

        product_aggregation_column = 'productName'
        df = (self.dm.demand_inventories[['quantity','xFulfilledDemandSol','xUnfulfilledDemandSol','xBacklogSol','xBacklogResupplySol','xInvSol']]
              .join(self.dm.products[['productGroup', 'productCountry']], how='left')
              #           .join(self.dm.locations)
              .join(df0, how='left')
              ).groupby(['timePeriodSeq', product_aggregation_column, "productCountry"]).sum()
        # print(f"products = {df.index.get_level_values('productName').unique()}")

        if 'relative_week' in df.columns:  # TODO: remove if not relevant anymore
            df = df.drop(columns=['relative_week'])

        df = (df
            .rename(
            columns={'quantity': 'Demand', 'xFulfilledDemandSol': 'Fulfilled', 'xUnfulfilledDemandSol': 'Unfulfilled',
                     'xBacklogSol': 'Backlog', 'xBacklogResupplySol': 'Backlog Resupply', 'xInvSol': 'Inventory'})
        )

        df = (df.stack()
              .rename_axis(index={None: 'var_name'})
              .to_frame(name='quantity')
              .reset_index()
              )

        var_name_category_order =  ['Demand', 'Transportation', 'Fulfilled', 'Unfulfilled', 'Backlog', 'Backlog Resupply', 'Inventory']

        num_vars = 6
        if var_names is not None:
            df = df.query("var_name in @var_names").copy()
            num_vars = len(var_names)
            var_name_category_order =  var_names

        df['location_product'] = df.productCountry + " - " +  df.productName

        color_discrete_map = self.gen_color_col(df['location_product'])
        # print(f"color_discrete_map={color_discrete_map}")
        # print(f"location_product = {df['location_product'].unique()}")

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Quantity', 'productName': 'Product Name', 'productGroup':'Product Group',
                  'var_name': 'Var', 'location_product': 'Product Country'}

        active_var_names = []

        if mode == 'columns':
            fig = px.bar(df, x="timePeriodSeq", y="quantity", 
                        #  color=product_aggregation_column, 
                         title="Fulfillment", 
                         labels=labels,
                         facet_col="var_name",
                         color = "location_product",
                         color_discrete_map= color_discrete_map,
                         category_orders={
                            #  'var_name': ['Demand', 'Transportation', 'Fulfilled', 'Unfulfilled', 'Backlog', 'Backlog Resupply',
                            #               'Inventory'],
                             'var_name': var_name_category_order
                        },
                         height=400
                         )

            for axis in fig.layout:
                if type(fig.layout[axis]) == go.layout.XAxis:
                    fig.layout[axis].title.text = ''
            
           

            fig.update_layout(
                # keep the original annotations and add a list of new annotations:
                annotations = list(fig.layout.annotations) + 
                [go.layout.Annotation(
                        x=0.55,
                        y=-0.15,
                        font=dict(
                            size=14
                        ),
                        showarrow=False,
                        text="Time Period",
                        textangle=0,
                        xref="paper",
                        yref="paper"
                    )
                ]
            )


        else:  # e.g. None
            fig = px.bar(df, x="timePeriodSeq", y="quantity", 
                        #  color=product_aggregation_column, 
                         title="Fulfillment", labels=labels,
                         facet_row="var_name",
                         color = "location_product",
                         color_discrete_map= color_discrete_map,
                         category_orders={
                            #  'var_name': ['Demand', 'Transportation', 'Fulfilled', 'Unfulfilled', 'Backlog', 'Backlog Resupply',
                            #               'Inventory'],
                             'var_name': var_name_category_order
                        },
                         height=250*num_vars
                         )

            fig.for_each_annotation(lambda a: a.update(x = a.x -1.045, textangle = 270))

             # get rid of duplicated Y-axis labels
            for axis in fig.layout:
                if type(fig.layout[axis]) == go.layout.YAxis:
                    fig.layout[axis].title.text = ''     


        fig.update_layout(hovermode="closest",legend = {'orientation': 'v'})  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("Var=")[-1]))

        fig.update_layout(legend = 
                            {'orientation': 'v',
                            'x': 1,
                            },
                          margin = {'l': 75}
                            )

        # fig.layout.yaxis2.update(matches=None)
        # fig.layout.yaxis3.update(matches=None)
        fig.layout.yaxis4.update(matches=None)
        fig.update_yaxes(showticklabels=True, col=4)  #, col=2

        fig.update_layout(
            margin={'l': 80, 't': 50, 'r': 20, 'b': 60})

        return fig

    # def plotly_inventory_days_of_supply_line(self, mode:str='line', query=None):
    #     """Demand inventory, normalized by days-of-supply."""
    #     num_days = 2 * 365  # For now assume 2 years. TODO: get from number of time-periods and bucket length
    #     df1 = (self.dm.demand[['quantity']]
    #            .join(self.dm.products['productGroup'])
    #            .groupby(['productGroup','productName','locationName']).sum()
    #            )
    #     df1['demand_per_day'] = df1.quantity / num_days
    #     df1 = df1.drop(columns=['quantity'])
    #     #         display(df1.head())

    #     df = (self.dm.demand_inventories[['xInvSol']]
    #           .join(df1)
    #           .reset_index()
    #           .set_index(['locationName','productGroup','productName'])
    #           .sort_index()
    #           )
    #     if query is not None:
    #         df = df.query(query).copy()

    #     df['days_of_supply'] = df.xInvSol / df.demand_per_day

    #     df = df.reset_index()
    #     df['product_location'] = df.locationName + " - " + df.productName

    #     labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Inventory', 'productName': 'Product Name',
    #               'productGroup': 'Product Group', 'days_of_supply': 'Days of Supply'}
    #     if mode == 'bar':
    #         fig = px.bar(df, x="timePeriodSeq", y="days_of_supply",
    #                      color='product_location',
    #                      height=600,
    #                      title='Demand Inventory (days-of-supply)', labels=labels)
    #     else:
    #         fig = px.line(df, x="timePeriodSeq", y="days_of_supply",
    #                       color='product_location',
    #                       height=600,
    #                       title='Demand Inventory (days-of-supply)', labels=labels)
    #     fig.update_layout(
    #         hovermode="closest",
    #         # title={
    #         #     'text': f"Total product demand",
    #         #     # 'y': 0.9,
    #         #     # 'x': 0.5,
    #         #     'xanchor': 'center',
    #         #     'yanchor': 'top'},
    #         legend={'orientation': 'v'},
    #         # legend_title_text=product_aggregation_column,
    #     )

    #     return fig

    def plotly_wh_inventory(self, mode:str='bar', query=None):
        """Warehouse inventory stacked bar chart by productName.
        TODO: remove products that have no inventory over the whole time-line."""
        df = (self.dm.warehouse_inventories[['xInvSol']]
              # .query("xInvSol > 0")
              .join(self.dm.products[['productGroup', 'productCountry']])
              .sort_index()
              .sort_values(['xInvSol'], ascending=False)
              )
        if query is not None:
            df = df.query(query)

        df = df.reset_index()

        df['productCountry'] = df['productCountry'].fillna("")
        df['location_product'] = df['productCountry'] + " - " + df['productName']
        df['location_product'] = df['location_product'].fillna('API')

        color_discrete_map = self.gen_color_col(df['location_product'])

        labels = {'timePeriodSeq': 'Time Period', 'days_of_supply':'Days of Supply', 'quantity': 'Inventory', 'productName': 'Product Name',
                  'productGroup': 'Product Group', 
                  'location_product': 'Product Location',
                   "xInvSol": "Inventory"}


        if mode == 'bar':
            fig = px.bar(df, x="timePeriodSeq", y="xInvSol",
                         color='location_product',
                         color_discrete_map = color_discrete_map, 
                         height=600,
                         title='Warehouse Inventory', labels=labels)
        elif mode == 'area':
            fig = px.area(df, x="timePeriodSeq", y="xInvSol",
                         color='location_product',
                         color_discrete_map = color_discrete_map, 
                         height=600,
                         title='Warehouse Inventory', labels=labels)
        else:
            fig = px.line(df, x="timePeriodSeq", y="xInvSol",
                         color='location_product',
                         color_discrete_map = color_discrete_map, 
                          height=600,
                          title='Warehouse Inventory', labels=labels)
        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v',
                    # 'yanchor': 'middle',
                    'x': 1.05,
                    },
            margin = {'l': 80,'t':80}
            # legend_title_text=product_aggregation_column,
        )

        return fig

    def plotly_plant_inventory(self, mode:str='bar', query=None):
        """Plant inventory stacked bar chart by productName.
        TODO: remove products that have no inventory over the whole time-line."""
        df = (self.dm.plant_inventories[['xInvSol']]
              #               .query("xInvSol > 0")  # Doesn't work well: will reduce the number of entries in the horizon
              .join(self.dm.products[['productGroup', 'productCountry']])
              .sort_index()
              .sort_values(['xInvSol'], ascending=False)
              )
        if query is not None:
            df = df.query(query)

        df = df.reset_index()

        # df = df[df.xInvSol > 0]

        df.productCountry = df['productCountry'].fillna("")

        df['location_product'] = df['productCountry'] + " - " + df['productName']

        # df['location_product'] = df['location_product'].fillna('API')

        color_discrete_map = self.gen_color_col(df['location_product'])

        labels = {'timePeriodSeq': 'Time Period', 'days_of_supply':'Days of Supply', 'quantity': 'Inventory', 'productName': 'Product Name',
                  'productGroup': 'Product Group', 
                  'location_product': 'Product Location'}

        category_orders = {
            # 'locationName': ['Abbott_Weesp_Plant', 'Abbott_Olst_Plant'],
            'locationName': self.plant_name_category_orders
            }

        if mode == 'bar':
            fig = px.bar(df, x="timePeriodSeq", y="xInvSol",
                         facet_row='locationName',
                         color='location_product',
                         color_discrete_map = color_discrete_map, 
                         category_orders=category_orders,
                         height=600,
                         title='Plant Inventory', labels=labels)
            fig.for_each_annotation(lambda a: a.update(x = a.x-1.04, textangle = 270))
        elif mode == 'area':
            fig = px.area(df, x="timePeriodSeq", y="xInvSol",
                         facet_row='locationName',
                         color='location_product',
                        # color='productName',
                         color_discrete_map = color_discrete_map, 
                         category_orders=category_orders,
                         height=600,
                         title='Plant Inventory', labels=labels)
            fig.for_each_annotation(lambda a: a.update(x = a.x-1.08, textangle = 270))
        else:
            fig = px.line(df, x="timePeriodSeq", y="xInvSol",
                         color='location_product',
                         color_discrete_map = color_discrete_map, 
                         category_orders=category_orders,
                          height=600,
                          title='Plant Inventory', labels=labels)

        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v',
                    'x': 1.05,},
            margin = {'l': 80, 't':80}
        )

        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ''  

        fig.for_each_annotation(lambda a: a.update(text=a.text.split("locationName=")[-1]))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("_", " ")))
        return fig

    def plotly_demand_inventory(self, mode:str='bar', query=None):
        """Plant inventory stacked bar chart by productName.
        TODO: remove products that have no inventory over the whole time-line."""
        df = (self.dm.demand_inventories[['xInvSol']]
              #               .query("xInvSol > 0")  # Doesn't work well: will reduce the number of entries in the horizon
              .join(self.dm.products[['productGroup', 'productCountry']])
              .sort_index()
              .sort_values(['xInvSol'], ascending=False)
              )
        if query is not None:
            df = df.query(query)

        df = df.reset_index()
        df['productCountry'] = df['productCountry'].fillna('')
        df['location_product'] = df.productCountry + " - " + df.productName


        color_discrete_map = self.gen_color_col(df['location_product'])

        labels = {'timePeriodSeq': 'Time Period', 'days_of_supply':'Days of Supply', 'quantity': 'Inventory', 'productName': 'Product Name',
                  'productGroup': 'Product Group', 'location_product': 'Product Location', 'xInvSol': 'Inventory'}
        
        if mode == 'bar':
            fig = px.bar(df, x="timePeriodSeq", y="xInvSol",
                         color_discrete_map=color_discrete_map,
                         color='location_product',
                         height=600,
                         title='Demand Inventory', labels=labels)
        else:
            fig = px.line(df, x="timePeriodSeq", y="xInvSol",
                          color_discrete_map=color_discrete_map,
                          color='location_product',
                          height=600,
                          title='Demand Inventory', labels=labels)
        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v',
                    'x': 1.05},
            margin={'l':80,'t':80},
            # legend_title_text=product_aggregation_column,
        )

        return fig

    def plotly_line_product_capacity_heatmap(self):
        """Heatmap of capacity as line vs product. Good insight on line specialization/recipe-properties.
        Input tables: ['RecipeProperties', 'Line', 'Product']
        Output tables: []
        """
        df = (self.dm.recipe_properties[['capacity']]
              .join(self.dm.lines)
              .join(self.dm.products[['productGroup']])
              #           .join(self.dm.plants.rename(columns={'locationDescr':'plantDescr'}), on='plantName')
              #           .join(self.dm.locations, on='locationName')
              )  # .groupby(['lineName','productType']).max()
        df = df.reset_index()
        #     display(df.head())
        # df = df.pivot_table(values='capacity', index=['lineDescr'], columns=['productType'], aggfunc=np.max)
        df = df.pivot_table(values='capacity', index=['lineName'], columns=['productGroup'], aggfunc=np.max)

        df = df.reset_index()

        cols = ["API", "Granulate", "Tablet", "Package"]
        df= df[cols]

        labels = {'lineName': 'Line', 'productGroup': 'Product Group', 'productName': 'Product Name'}
        labels = dict(x="Product Group", y="Line", color="Capacity")
        
        # labels = dict(x=["1","2","3","4"], y="Line", color="Capacity")

        fig = px.imshow(df, labels=labels, width=1000,
                        color_continuous_scale='YlOrRd',
                        # labels = {
                        #    'x':["1","2","3","4"]
                        # },
                        # y = ["Abbott Olst<br>Granulate Line", "Abbott Olst<br>Packaging Line 5", "Abbott Olst<br>Packaging Line 6", "Abbott<br>Weesp Line"],
                        y = ["Granulate Line", "Packaging Line 1", "Packaging Line 2", "API Line"],
                        # y = ["API Line", "Granulate Line", "Packaging Line 1", "Packaging Line 2"],
                        # x = ["API", "Granulate", "Tablet", "Package"],
                        # template="ggplot2",
                        )

        # for i, label in enumerate(['orignal', 'clean', '3', '4']):
        #     fig.layout.annotations[i]['text'] = label

        # fig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)


        fig.update_layout(
            hovermode="closest",
            title={
                'text': "Maximum Line Capacity by Product Type",
                # 'y': 0.92,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        margin = {'l': 60,'t':80,'b':60})

        return fig

    def plotly_line_package_capacity_heatmap(self):
        """Heatmap of capacity as line vs product. Good insight on line specialization/recipe-properties.
        Input tables: ['RecipeProperties', 'Line', 'Product']
        Output tables: []
        """
        df = (self.dm.recipe_properties[['capacity']]
              .join(self.dm.lines)
              .join(self.dm.products[['productGroup', 'productCountry']])
              #           .join(self.dm.plants.rename(columns={'locationDescr':'plantDescr'}), on='plantName')
              #           .join(self.dm.locations, on='locationName')
              .query("productGroup == 'Package'")
              )  # .groupby(['lineName','productType']).max()
        df = df.reset_index()

        df.productName = df.productName.astype(str)

        df['location_product'] = df['productCountry'] + ' - ' + df['productName']
        df['location_product'] = df['location_product'].fillna('API')

        # df = df.pivot_table(values='capacity', index=['lineDescr'], columns=['productType'], aggfunc=np.max)
        df = df.pivot_table(values='capacity', index= ['lineName'], 
                            columns=['location_product']  , aggfunc=np.max)

        labels = {'lineName': 'Line', 'productGroup': 'Product Group', 'productName': 'Product Name',
                  }
        labels = dict(x="Line", y="Product" , color="Max Capacity")
        fig = px.imshow(df, 
                        aspect = 'auto',
                        labels=labels,
                        # height = 800,
                        #                     width=1000,
                        color_continuous_scale='YlOrRd',
                        # y = ["Abbott Olst<br>Packaging Line 5", "Abbott Olst<br>Packaging Line 6"],
                        # y = ["Packaging Line 1", "Packaging Line 2"],
                        )

        fig.update_layout(
            title={
                'text': "Maximum Packaging Line Capacity by Product",
                # 'y': 0.92,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            margin = {'l': 140,'t':40,'b':100})

        fig.update_xaxes(tickfont={'size':11})


        return fig

    def plotly_time_product_group_capacity_heatmap(self):
        """Heatmap of capacity over time.
        Good to detect and time-variation in capacity.
        Input tables: ['RecipeProperties', 'Line', 'Product']
        Output tables: []
        """

        df = (self.dm.recipe_properties[['capacity']]
              .join(self.dm.lines)
              .join(self.dm.products[['productGroup']]))
        df = df.reset_index()

        
        cols = ["API", "Granulate", "Tablet", "Package"]
        # df= df[cols]

        df = df.pivot_table(values='capacity', index=['productGroup'], columns=['timePeriodSeq'], aggfunc=np.max)

        df= df.reindex(cols)
        # print(df.index)
        
        labels = {'lineName': 'Line', 'productGroup': 'Product Group', 'productName': 'Product Name'}
        labels = dict(x="Time Period", y="Product Group", color="Capacity")
        fig = px.imshow(df, labels=labels,
                        color_continuous_scale='YlOrRd',
                        # y = ["API", "Granulate", "Tablet", "Package"]
                        )
        fig.update_layout(
            title={
                'text': "Maximum Line Capacity by Product Group and Time Period",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        margin = {'l': 90,'t':80,'b':60})

        return fig

    def plotly_time_package_capacity_heatmap(self):
        """Heatmap of capacity over time.
        Good to detect and time-variation in capacity.
        Input tables: ['RecipeProperties', 'Line', 'Product']
        Output tables: []
        """

        df = (self.dm.recipe_properties[['capacity']]
              .join(self.dm.lines)
              .join(self.dm.products[['productGroup']]))
        df = df.reset_index()
        df = df.query("productGroup == 'Package'")
        # display(df.head())
        df = df.pivot_table(values='capacity', index=['productName'], columns=['timePeriodSeq'], aggfunc=np.max)

        labels = {'lineName': 'Line', 'productGroup': 'Product Group', 'productName': 'Product Name'}
        labels = dict(x="Time Period", y="Product Name", color="Capacity")
        fig = px.imshow(df, labels=labels,
                        # color_discrete_sequence=px.colors.qualitative.G10  # Doesn't work!
                        # color_continuous_scale='Turbo',
                        # color_continuous_scale='YlOrBr',
                        color_continuous_scale='YlOrRd',
                        height = 1000,
                        )
        fig.update_layout(
            title={
                'text': "Maximum Line Capacity by Product and Time Period",
#                 'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
        margin = {'l': 90,'t':80,'b':60})

        return fig

    # def plotly_time_product_capacity_bars(self):
    #     """Heatmap of capacity over time.
    #     Good to detect and time-variation in capacity.
    #     Input tables: ['RecipeProperties', 'Line', 'Product']
    #     Output tables: []
    #     """
    #     df = (self.dm.recipe_properties[['capacity']]
    #           .join(self.dm.lines)
    #           .join(self.dm.products[['productGroup']]))
    #     #     display(df.head())

    #     df = df[['capacity','productGroup']].groupby(['lineName','timePeriodSeq','productName']).max()
    #     #     display(df.head())

    #     labels = {'lineName': 'Line', 'productGroup': 'Product Group', 'productName': 'Product Name', 'timePeriodSeq':'Time Period', 'capacity':'Capacity'}
    #     #     labels = dict(x="Time Period", y="Product Group", color="Capacity")
    #     fig = px.bar(df.reset_index(), x='timePeriodSeq', y='capacity', color='productName',labels=labels,
    #                  facet_col='productGroup',
    #                  category_orders={
    #                      "productGroup": ["API", "Granulate", "Tablet", "Package"]
    #                      },
                     
    #                  #                  facet_row = 'lineName',
    #                  )

    #     fig.update_layout(
    #         hovermode="closest",
    #         title={
    #             'text': "Maximum Line Capacity by Product and Time Period",
    #             'y': 0.95,
    #             'x': 0.5,
    #             'xanchor': 'center',
    #             'yanchor': 'top'})

    #     fig.update_layout(legend=dict(
    #         yanchor="top",
    #         y=0.99,
    #         xanchor="right",
    #         x=1.15,
    #         orientation="v"
    #     ))
    #     fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    #     return fig

    def plotly_time_product_group_capacity_bars(self):
        """Heatmap of capacity over time.
        Good to detect and time-variation in capacity.
        Input tables: ['RecipeProperties', 'Line', 'Product']
        Output tables: []
        """
        df = (self.dm.recipe_properties[['capacity']]
              .join(self.dm.lines)
              .join(self.dm.products[['productGroup']]))
        #     display(df.head())

        df = df[['capacity','productGroup']].groupby(['lineName','timePeriodSeq','productGroup']).max()
        #     display(df.head())

        color_discrete_map = self.gen_color_col()

        labels = {'lineName': 'Line', 'productGroup': 'Product Group', 'productName': 'Product Name', 'timePeriodSeq':'Time Period', 'capacity':'Capacity'}
        #     labels = dict(x="Time Period", y="Product Group", color="Capacity")
        fig = px.bar(df.reset_index(), x='timePeriodSeq', y='capacity', color='productGroup',labels=labels,
                     facet_col='productGroup',
                     category_orders={
                         "productGroup": ["API", "Granulate", "Tablet", "Package"]
                         },
                     color_discrete_map= color_discrete_map
                     )

        fig.update_layout(
            hovermode="closest",
            title={
                'text': "Maximum Line Capacity by Product Group and Time Period",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'}
        )

        fig.update_layout(
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=1.15,
                orientation="v"
            ),
            margin = {'l': 60,'t':80,'b':60},
            )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.XAxis:
                fig.layout[axis].title.text = ''  

        return fig



    def plotly_demand_inventory_bar_subplot_by_time(self):
        """Demand, Fulfilled, Unfulfilled, Backlog, BacklogResupply and Inventory over time, grouped by time-period.
        Colored by groupID.
        Very useful graph since it contains all critical variables at the demand locations. Good for explanation.
        """
        # product_aggregation_column = 'groupID'
        # df1 = (self.dm.demand_inventories
        #        .join(self.dm.products[['productType', 'subgroupID', 'groupID']])
        #        #           .join(self.dm.locations)
        #        ).groupby(['timePeriodSeq', product_aggregation_column]).sum()
        # if 'relative_week' in df1.columns:  # TODO: remove if not relevant anymore
        #     df1 = df1.drop(columns=['relative_week'])
        # df1 = (df1
        #        # .drop(columns=['relative_week'])
        #        .rename(
        #     columns={'quantity': 'Demand', 'xFulfilledDemandSol': 'Fulfilled', 'xUnfulfilledDemandSol': 'Unfulfilled',
        #              'xBacklogSol': 'Backlog', 'xBacklogResupplySol': 'Backlog Resupply', 'xDemandInvSol': 'Inventory'})
        #        )
        # df1 = (df1.stack()
        #        .rename_axis(index={None: 'var_name'})
        #        .to_frame(name='quantity')
        #        .reset_index()
        #        )

        # # Inflows from plants:
        # df2 = (self.dm.plant_to_demand_transportation[['xTransportationSol']]
        #        .join(self.dm.products[['productType', 'subgroupID', 'groupID']])
        #        .groupby(['timePeriodSeq', product_aggregation_column]).sum()
        #        .rename(columns={'xTransportationSol': 'Production'})
        #        )
        # df2 = (df2.stack()
        #        .rename_axis(index={None: 'var_name'})
        #        .to_frame(name='quantity')
        #        .reset_index()
        #        )

        # df = pd.concat([df1, df2])

        # # print(df.head())

        # labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name',
        #           'var_name': 'Var'}
        # fig = px.bar(df, x="var_name", y="quantity", color=product_aggregation_column, title="Demand", labels=labels,
        #              facet_col="timePeriodSeq",
        #              category_orders={
        #                  'var_name': ['Demand', 'Production', 'Fulfilled', 'Unfulfilled', 'Backlog', 'Backlog Resupply',
        #                               'Inventory']},
        #              height=700
        #              )
        # fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        # return fig

        product_aggregation_column = 'groupID'
        df1 = (self.dm.demand_inventories
               .join(self.dm.products[['productType', 'subgroupID', 'groupID']])
               #           .join(self.locations)
               ).groupby(['timePeriodSeq', product_aggregation_column]).sum()
        if 'relative_week' in df1.columns:  # TODO: remove if not relevant anymore
            df1 = df1.drop(columns=['relative_week'])
        df1 = (df1
            # .drop(columns=['relative_week'])
            .rename(
            columns={'quantity': 'Demand', 'xFulfilledDemandSol': 'Fulfilled', 'xUnfulfilledDemandSol': 'Unfulfilled',
                     'xBacklogSol': 'Backlog', 'xBacklogResupplySol': 'Backlog Resupply', 'xDemandInvSol': 'Inventory'})
        )
        df1 = (df1.stack()
               .rename_axis(index={None: 'var_name'})
               .to_frame(name='quantity')
               .reset_index()
               )

        # Inflows from plants:
        df2 = (self.dm.plant_to_demand_transportation[['xTransportationSol']]
               .join(self.dm.products[['productType', 'subgroupID', 'groupID']])
               .groupby(['timePeriodSeq', product_aggregation_column]).sum()
               .rename(columns={'xTransportationSol': 'Production'})
               )
        df2 = (df2.stack()
               .rename_axis(index={None: 'var_name'})
               .to_frame(name='quantity')
               .reset_index()
               )

        df = pd.concat([df1, df2])

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name',
                  'var_name': 'Var'}

        import plotly.graph_objects as go

        fig = go.Figure()

        fig.update_layout(
            template="simple_white",
            xaxis=dict(title_text="Time"),
            yaxis=dict(title_text="Quantity"),
            barmode="stack",
        )

        colors = ["#6495ED", "#FFBF00", "#FF7F50", "#DE3163", "#9FE2BF"]

        for p, c in zip(df.groupID.unique(), colors):
            plot_df = df[df.groupID == p]
            fig.add_trace(
                go.Bar(x=[plot_df.timePeriodSeq, plot_df.var_name], y=plot_df.quantity, name=p, marker_color=c),
            )

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        return fig

    #######################################################################################
    # Inventory
    #######################################################################################
    def plotly_inventory_days_of_supply_line(self, mode:str='line', query=None):
        """Demand inventory, normalized by days-of-supply.
        Args:
            mode (str): line (default) or bar. Bar will result in a stacked bar.

        Input tables: ['Demand', 'Product']
        Output tables: ['DemandInventory]
        """
        # num_days = 2 * 365  # For now assume 2 years. TODO: get from number of time-periods and bucket length
        num_days = len(self.dm.demand.index.unique(level='timePeriodSeq')) * 30
        df1 = (self.dm.demand[['quantity']]
               .join(self.dm.products['productGroup'])
               .groupby(['productGroup','productName','locationName']).sum()
               )
        df1['demand_per_day'] = df1.quantity / num_days

        df1 = df1.drop(columns=['quantity'])

        temp = self.dm.demand_inventories[['xInvSol']].reset_index()

        temp = temp[temp.locationName == 'PERU']

        df = (self.dm.demand_inventories[['xInvSol']]
              .join(df1)
              .reset_index()
              .set_index(['locationName','productGroup','productName'])
              .sort_index()
              )
        if query is not None:
            df = df.query(query).copy()

        df['days_of_supply'] = df.xInvSol / df.demand_per_day

        tdf = df.reset_index()
        tdf = tdf[tdf.locationName == 'PERU']

        df = df.reset_index()

        df['location_product'] = df.locationName + " - " + df.productName

        color_discrete_map = self.gen_color_col(df['location_product'])

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Inventory', 'productName': 'Product Name',
                  'productGroup': 'Product Group', "days_of_supply": "Days of Supply", 'days_of_supply_smoothed': 'Days of Supply'}

        df['days_of_supply'] = df['days_of_supply'].clip(upper = 100)

        df = df.sort_values('timePeriodSeq')

        df['days_of_supply_smoothed'] = df['days_of_supply'].rolling(window=5).mean()

        if mode == 'bar':
            fig = px.bar(df, x="timePeriodSeq", y="days_of_supply",
                         color='location_product',
                         color_discrete_map=color_discrete_map,
                         height=600,
                         title='Demand Inventory (days-of-supply)', labels=labels)
        else:
            fig = px.line(df, x="timePeriodSeq", y="days_of_supply",
                          color='location_product',
                          color_discrete_map=color_discrete_map,
                          height=600,
                          title='Demand Inventory (days-of-supply)', labels=labels)
        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v',
            "title": 'Product Location',
            'x': 1.05},
            margin={'l':80,'t':60, 'r':0},
        )

        return fig

    def plotly_inventory_days_of_supply_slack_line(self, mode:str='line', query=None):
        """Demand inventory, days-of-supply slack.
        Args:
            mode (str): line (default) or bar. Bar will result in a stacked bar.

        Input tables: ['Demand', 'Product']
        Output tables: ['DemandInventory]
        """
        # num_days = 2 * 365  # For now assume 2 years. TODO: get from number of time-periods and bucket length
        num_days = len(self.dm.demand.index.unique(level='timePeriodSeq')) * 30
        df1 = (self.dm.demand[['quantity']]
               .join(self.dm.products['productGroup'])
               .groupby(['productGroup','productName','locationName']).sum()
               )
        df1['demand_per_day'] = df1.quantity / num_days
        df1 = df1.drop(columns=['quantity'])

        df = (self.dm.demand_inventories[['xDOSSlackSol']]
              .join(df1)
              .reset_index()
              .set_index(['locationName','productGroup','productName'])
              .sort_index()
              )
        if query is not None:
            df = df.query(query).copy()

        df['dosSlack'] = df.xDOSSlackSol / df.demand_per_day

        df = df.reset_index()

        df['location_product'] = df.locationName + " - " + df.productName

        color_discrete_map = self.gen_color_col(df['location_product'])

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Inventory', 'productName': 'Product Name',
                  'productGroup': 'Product Group', "days_of_supply": "Days of Supply"}

        df['dosSlack'] = df['dosSlack'].clip(upper = 100)

        if mode == 'bar':
            fig = px.bar(df, x="timePeriodSeq", y="dosSlack",
                         color='location_product',
                         color_discrete_map=color_discrete_map,
                         height=600,
                         title='Demand Inventory Slack (days-of-supply)', labels=labels)
        else:
            fig = px.line(df, x="timePeriodSeq", y="dosSlack",
                          color='location_product',
                          color_discrete_map=color_discrete_map,
                          height=600,
                          title='Demand Inventory Slack (days-of-supply)', labels=labels)

        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v',
            "title": 'Product Location',
            'x': 1.05},
            margin={'l': 80, 't': 60, 'r': 0},
        )

        return fig

    def plotly_wh_inventory_days_of_supply_line(self, mode:str='line', query=None):
        """Warehouse inventory, normalized by days-of-supply."""
        # num_days = 2 * 365  # For now assume 2 years. TODO: get from number of time-periods and bucket length
        num_days = len(self.dm.demand.index.unique(level='timePeriodSeq')) * 30
        df1 = (self.dm.demand[['quantity']]
               .join(self.dm.products[['productGroup', 'productCountry']])
               .groupby(['productGroup','productName', 'productCountry']).sum()
               )

        df1['demand_per_day'] = df1.quantity / num_days
        df1 = df1.drop(columns=['quantity'])

        df = (self.dm.warehouse_inventories[['xInvSol']]
              .join(df1)
              .reset_index()
              .set_index(['locationName','productGroup','productName', 'productCountry'])
              .sort_index()
              )
        if query is not None:
            df = df.query(query).copy()

        df['days_of_supply'] = (df.xInvSol / df.demand_per_day)

        df = df.reset_index()

        df.productCountry = df.productCountry.fillna("")

        df['location_product'] = df.productCountry + " - " + df.productName

        df.days_of_supply = df.days_of_supply.clip(upper = 100)

        color_discrete_map = self.gen_color_col(df['location_product'])

        labels = {'timePeriodSeq': 'Time Period', 'days_of_supply':'Days of Supply', 'quantity': 'Inventory', 'productName': 'Product Name',
                  'productGroup': 'Product Group', 'location_product': 'Product Location', 'xInvSol': 'Inventory'}

        if mode == 'bar':
            fig = px.bar(df, x="timePeriodSeq", y="days_of_supply",
                         color='location_product',
                         color_discrete_map=color_discrete_map,
                         height=600,
                         title='Warehouse Inventory (days-of-supply)', labels=labels)
        elif mode == 'area':
            fig = px.area(df, x="timePeriodSeq", y="xInvSol",
                          color='productName',
                          color_discrete_map=color_discrete_map,
                          height=600,
                          title='Warehouse Inventory', labels=labels)
        else:
            fig = px.line(df, x="timePeriodSeq", y="days_of_supply",
                          color='location_product',
                          color_discrete_map=color_discrete_map,
                          height=600,
                          title='Warehouse Inventory (days-of-supply)', 
                          labels=labels)

        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v',
            "x": 1.05},
            margin={'l': 80, 't': 60, 'r': 0},
        )

        return fig

    def plotly_package_demand_bars(self, query=None):
        """Product demand over time. Colored by productGroup.

        Input tables: ['Demand', 'Product']
        Output tables: []
        """
        df = (self.dm.demand
              .join(self.dm.products[['productGroup']])
              .query("productGroup == 'Package'")
              )
        if query is not None:
            df = df.query(query)

        aggregation_column = 'locationName'
        df = df.groupby(['timePeriodSeq', aggregation_column]).sum()

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name',
                  'productGroup': 'Product Group'}
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="quantity", color=aggregation_column,
                     title='Total Package Demand', labels=labels)
        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v'},
        )

        return fig

    def plotly_package_demand_lines(self, query=None):
        """Product demand over time. Colored by productGroup.
        Input tables: ['Demand', 'Product']
        Output tables: []
        """
        df = (self.dm.demand
              .join(self.dm.products[['productGroup']])
              .query("productGroup == 'Package'")
              )
        if query is not None:
            df = df.query(query)

        aggregation_column = 'locationName'
        df = df.groupby(['timePeriodSeq', aggregation_column]).sum()

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name',
                  'productGroup': 'Product Group'}

        fig = px.line(df.reset_index(), x="timePeriodSeq", y="quantity", color=aggregation_column,
                      title='Total Package Demand', labels=labels)

        fig.update_layout(
            hovermode="closest",
            legend={'orientation': 'v'},
        )

        return fig

    def plotly_demand_fullfilment_scroll(self):
        """Demand, Fulfilled, Unfulfilled, Backlog, BacklogResupply and Inventory over time, grouped by time-period.
        Colored by groupID.
        Very useful graph since it contains all critical variables at the demand locations. Good for explanation.
        """

        # Collect transportation activities into a destination location.
        # (later we'll do a left join to only select trnasportation into a demand location and ignore all other transportation activities)
        df0 = self.dm.transportation_activities
        df0['destinationTimePeriodSeq'] = df0.index.get_level_values('timePeriodSeq') + df0.transitTime
        df0 = (df0[['xTransportationSol', 'destinationTimePeriodSeq']]
               .groupby(['productName', 'destinationLocationName', 'destinationTimePeriodSeq']).sum()
               .rename_axis(index={'destinationLocationName': 'locationName', 'destinationTimePeriodSeq':'timePeriodSeq'})
               .rename(columns={'xTransportationSol':'Transportation'})
               )
        #     display(df0.head())

        product_aggregation_column = 'productGroup'
        df = (self.dm.demand_inventories[['quantity','xFulfilledDemandSol','xUnfulfilledDemandSol','xBacklogSol','xBacklogResupplySol','xInvSol']]
              .join(self.dm.products[['productGroup']])
              #           .join(self.dm.locations)
              .join(df0, how='left')
              ).groupby(['timePeriodSeq', product_aggregation_column]).sum()
        if 'relative_week' in df.columns:  # TODO: remove if not relevant anymore
            df = df.drop(columns=['relative_week'])
        #     display(df.head())
        df = (df
            # .drop(columns=['relative_week'])
            .rename(
            columns={'quantity': 'Demand', 'xFulfilledDemandSol': 'Fulfilled', 'xUnfulfilledDemandSol': 'Unfulfilled',
                     'xBacklogSol': 'Backlog', 'xBacklogResupplySol': 'Backlog Resupply', 'xInvSol': 'Inventory'})
        )
        #     display(df.head())
        df = (df.stack()
              .rename_axis(index={None: 'var_name'})
              .to_frame(name='quantity')
              .reset_index()
              )
        #     display(df.head())


        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name', 'productGroup':'Product Group',
                  'var_name': 'Var'}

        fig = go.Figure()
        fig.update_layout(
            template="simple_white",
            xaxis=dict(title_text="Time"),
            yaxis=dict(title_text="Quantity"),
            barmode="stack",
            height=700
        )

        colors = self.gen_color_col()

        # Default colors:
        for p in df.productGroup.unique():
            plot_df = df[df.productGroup == p]
            fig.add_trace(go.Bar(x=[plot_df.timePeriodSeq, plot_df.var_name], y=plot_df.quantity, name=p, marker_color = colors[p]))

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around

        fig.update_layout(
                xaxis = dict(
                    tickfont = dict(size=9)))

        fig.update_layout(
            margin={'l': 10, 't': 10, 'r': 0, 'b':10})

        return fig

    def plotly_demand_fullfilment_scroll_product(self):
        """Demand, Fulfilled, Unfulfilled, Backlog, BacklogResupply and Inventory over time, grouped by time-period.
        Colored by groupID.
        Very useful graph since it contains all critical variables at the demand locations. Good for explanation.
        """

        # Collect transportation activities into a destination location.
        # (later we'll do a left join to only select trnasportation into a demand location and ignore all other transportation activities)
        # df0 = (self.dm.transportation_activities[['xTransportationSol']]
        #        .groupby(['productName', 'destinationLocationName', 'timePeriodSeq']).sum()
        #        .rename_axis(index={'destinationLocationName': 'locationName'})
        #        .rename(columns={'xTransportationSol':'Transportation'})
        #        )
        df0 = self.dm.transportation_activities
        df0['destinationTimePeriodSeq'] = df0.index.get_level_values('timePeriodSeq') + df0.transitTime
        df0 = (df0[['xTransportationSol', 'destinationTimePeriodSeq']]
               .groupby(['productName', 'destinationLocationName', 'destinationTimePeriodSeq']).sum()
               .rename_axis(index={'destinationLocationName': 'locationName', 'destinationTimePeriodSeq':'timePeriodSeq'})
               .rename(columns={'xTransportationSol':'Transportation'})
               )
        #     display(df0.head())

        # product_aggregation_column = 'productGroup'
        product_aggregation_column = 'productName'
        df = (self.dm.demand_inventories[['quantity','xFulfilledDemandSol','xUnfulfilledDemandSol','xBacklogSol','xBacklogResupplySol','xInvSol']]
              .join(self.dm.products[['productGroup', 'productCountry']])
              #           .join(self.dm.locations)
              .join(df0, how='left')
              ).groupby(['timePeriodSeq', product_aggregation_column, 'productCountry']).sum()
        # print(df.head())
        if 'relative_week' in df.columns:  # TODO: remove if not relevant anymore
            df = df.drop(columns=['relative_week'])
        #     display(df.head())
        df = (df
            # .drop(columns=['relative_week'])
            .rename(
            columns={'quantity': 'Demand', 'xFulfilledDemandSol': 'Fulfilled', 'xUnfulfilledDemandSol': 'Unfulfilled',
                     'xBacklogSol': 'Backlog', 'xBacklogResupplySol': 'Backlog Resupply', 'xInvSol': 'Inventory'})
        )

        df = (df.stack()
              .rename_axis(index={None: 'var_name'})
              .to_frame(name='quantity')
              .reset_index()
              )

        labels = {'timePeriodSeq': 'Time Period', 'quantity': 'Demand', 'productName': 'Product Name', 'productGroup':'Product Group',
                  'var_name': 'Var'}

        fig = go.Figure()
        fig.update_layout(
            template="simple_white",
            xaxis=dict(title_text="Time"),
            yaxis=dict(title_text="Quantity"),
            barmode="stack",
            height=900,
            # width = 2000
        )

        df = df.reset_index()
        df['location_product'] = df['productCountry'] + ' - ' + df['productName']
        df['location_product'] = df['location_product'].fillna('API')

        colors = self.gen_color_col(df['location_product'])

        # Default colors:
        # for p in df[product_aggregation_column].unique():
        #     print(f"p = {p}")

        # print(df[product_aggregation_column].unique())
        # print(colors)

        # Default colors:
        for p in df['location_product'].unique():
            # print(f"p = {p}")

            plot_df = df[df['location_product'] == p]
            try:
                fig.add_trace(go.Bar(x=[plot_df.timePeriodSeq, plot_df.var_name], y=plot_df.quantity, name=p, 
                    marker_color = colors[p]
                                ))
            except:
                pass


        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around

        fig.update_layout(
                xaxis = dict(
                    tickfont = dict(size=9)),
                legend = {'orientation': 'v', 'x': 1})

        fig.update_layout(
            margin={'l': 10, 't': 10, 'r': 0, 'b': 30})
        
        
        return fig

    def plotly_production_activities_bars(self, query=None, title='Production'):
        """Production activity over time, colored by productGroup.
        Input tables: ['Product', 'Location']
        Output tables: ['ProductionActivity']
        """
        product_aggregation_column = 'productGroup'
        product_aggregation_column = 'productName'
        
        df = (self.dm.production_activities
            .join(self.dm.products[['productGroup', 'productCountry']]))
        
        df = df.reset_index()

        df.productCountry = df.productCountry.fillna('')
        df['location_product'] = df.productCountry + " - " +  df.productName

        color_discrete_map = self.gen_color_col(df['location_product'])
        
        if query is not None:
            df = df.query(query)

        df = (df    
            .reset_index()
            .merge(self.dm.locations.reset_index(), on='locationName')
            ).groupby(['timePeriodSeq', product_aggregation_column, 'lineName', 'location_product']).sum()

        active_line_name_category_orders = [l for l in self.line_name_category_orders if l in df.index.unique(level='lineName')]  # Avoids empty spaces in Plotly chart
        labels = {'timePeriodSeq': 'Time Period', 'xProdSol': 'Production', 'productName': 'Product Name', 'location_product': 'Product Location'}
        category_orders = {
            # 'lineName' : ['Abbott_Weesp_Line','Abbott_Olst_Granulate_Line', 'Abbott_Olst_Packaging_Line_5','Abbott_Olst_Packaging_Line_6'],
            # 'lineName' : self.line_name_category_orders,
            'lineName' : active_line_name_category_orders,
            # 'timePeriodSeq': df.reset_index().timePeriodSeq.sort_values().unique(),
            'timePeriodSeq': df.index.unique(level='timePeriodSeq').sort_values()
        }
        
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="xProdSol", color='location_product',
                    color_discrete_map= color_discrete_map,
                    title=title, labels=labels,
                    facet_row = 'lineName',
                    category_orders=category_orders,
                    height=800,
                    )

        fig.update_layout(legend = 
                            {'orientation': 'v',
                            'x': 1.05,
                            }
        )
        
        fig.update_layout(margin = {'l': 85, 't':80})

        fig.for_each_annotation(lambda a: a.update(x = a.x-1.04, textangle = 270))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("lineName=")[-1]))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("_", " ")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Olst", "Olst<br>")))

        # get rid of duplicated X-axis labels
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ''     
        
        fig.update_xaxes(type='category')
        fig.update_layout(hovermode="closest",legend = {'orientation': 'v'})  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
        return fig

    def plotly_planned_production_activities_bars(self, query=None, title='Production'):
        """Production activity over time, colored by productGroup.
        Input tables: ['Product', 'Location']
        Output tables: ['ProductionActivity']
        """

        product_aggregation_column = 'productName'
        
        df = (self.dm.planned_production_activity
            .join(self.dm.products[['productGroup', 'productCountry']])
            # .sort_index()
            )


        df = df.reset_index()
        df['productCountry'] = np.where(pd.isnull(df.productCountry), '', df.productCountry)
        df['location_product'] = df.productCountry + " - " +  df.productName

        color_discrete_map = self.gen_color_col(df['location_product'])

        if query is not None:
            df = df.query(query)

        df = (df    
            ).groupby(['timePeriodSeq', product_aggregation_column, 'lineName', 'productCountry', 'location_product']).sum()
        
        active_line_name_category_orders = [l for l in self.line_name_category_orders if l in df.index.unique(level='lineName')]  # Avoids empty spaces in Plotly chart
        labels = {'timePeriodSeq': 'Time Period', 'xProdSol': 'Production', 'productName': 'Product Name', 
                  'location_product': 'Product Location'}

        # df = (df.reset_index())

        category_orders = {
            # 'lineName' : ['Abbott_Weesp_Line','Abbott_Olst_Granulate_Line', 'Abbott_Olst_Packaging_Line_5','Abbott_Olst_Packaging_Line_6'],
            # 'lineName' : self.line_name_category_orders,
            'lineName' : active_line_name_category_orders,
            # 'timePeriodSeq': df.reset_index().timePeriodSeq.sort_values().unique()
            # 'timePeriodSeq': df.timePeriodSeq.sort_values().unique()
            'timePeriodSeq': df.index.unique(level='timePeriodSeq').sort_values()
        }

        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="quantity", color='location_product',
                    color_discrete_map=color_discrete_map,
                    title=title, labels=labels,
                    facet_row = 'lineName',
                    category_orders = category_orders,
                    height=800,
                    )

        fig.update_layout(legend = 
                            {'orientation': 'v',
                            'x': 1.05,
                            }
        )
        
        fig.update_layout(margin = {'l': 90,'t':60})
        # fig.for_each_annotation(lambda a: a.update(x = a.x -1., y = a.y-0.15, textangle = 0, 
        # font  = {'size':16}
        # ))

        fig.for_each_annotation(lambda a: a.update(x = a.x-1.055, textangle = 270))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("lineName=")[-1]))

        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("_", " ")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Olst", "Olst<br>")))

        # get rid of duplicated X-axis labels
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ''     
        
        fig.update_xaxes(type='category')

        fig.update_layout(hovermode="closest",legend = {'orientation': 'v'})

        return fig

    def plotly_production_slack_bars(self, query=None, title='Production Slack'):
        """Production activity slack over time, colored by productName.
        Input tables: ['Product']
        Output tables: ['ProductionActivity']
        """
        product_aggregation_column = 'productName'
        
        df = (self.dm.production_activities
            .join(self.dm.products[['productGroup', 'productCountry']]))

        df = df.reset_index()
        df['productCountry'] = np.where(pd.isnull(df.productCountry), '', df.productCountry)
        df['location_product'] = df.productCountry + " - " +  df.productName

        color_discrete_map = self.gen_color_col(df['location_product'])

        if query is not None:
            df = df.query(query)

        df = (df    
            .reset_index()
    #           .merge(self.dm.locations.reset_index(), on='locationName')
            ).groupby(['timePeriodSeq', product_aggregation_column, 'lineName', 'productCountry', 'location_product']).sum()
        
        labels = {'timePeriodSeq': 'Time Period', 'xProdSol': 'Production', 'productName': 'Product Name', 
                  'location_product': 'Product Location'}
        active_line_name_category_orders = [l for l in self.line_name_category_orders if l in df.index.unique(level='lineName')]  # Avoids empty spaces in Plotly chart
        
        category_orders = {
            # 'lineName' : ['Abbott_Weesp_Line','Abbott_Olst_Granulate_Line',
            #                             'Abbott_Olst_Packaging_Line_5','Abbott_Olst_Packaging_Line_6'],
            # 'lineName' : self.line_name_category_orders,
            'lineName' : active_line_name_category_orders,
            # 'timePeriodSeq': df.reset_index().timePeriodSeq.sort_values().unique()
            'timePeriodSeq': df.index.unique(level='timePeriodSeq').sort_values(),
        }
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="xProdSlackSol", color='location_product',
                    color_discrete_map=color_discrete_map,
                    title=title, labels=labels,
                    facet_row = 'lineName',
                    category_orders=category_orders,
                    height=800,
                    )

        fig.update_layout(legend = 
                            {'orientation': 'v',
                            'x': 1.05,
                            }
        )
        
        fig.update_layout(margin = {'l': 85, 't':60})

        fig.for_each_annotation(lambda a: a.update(x = a.x-1.05, textangle = 270))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("lineName=")[-1]))

        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("_", " ")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Olst", "Olst<br>")))
    
        # get rid of duplicated X-axis labels
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ''     
        
        fig.update_xaxes(type='category')
        fig.update_layout(hovermode="closest",legend = {'orientation': 'v'})

        return fig

    def plotly_production_excess_bars(self, query=None, title='Production Plan Difference', mode = None):
        """Production activity excess (compared to plan) over time, colored by productName.
        Default mode returns excess as a substraction, percentage returns as percentage
        Input tables: ['Product', 'PlannedproductionActivity']
        Output tables: ['ProductionActivity']
        """
        product_aggregation_column = 'productName'

        planned_production = (self.dm.planned_production_activity
            .reset_index()
            # .astype({'planId': int})
            # .query("planId == 1")  # HACK!!!! Need to filter on planId
            # .reset_index()
            .set_index(['productName','lineName','timePeriodSeq','recipeId'], verify_integrity = True)
        )

        df = (self.dm.production_activities
            .join(self.dm.products[['productGroup', 'productCountry']])
            .join(planned_production, how = 'left')  
            .rename(columns={'quantity':'plannedProductionQuantity'})
            )
        df.plannedProductionQuantity = df.plannedProductionQuantity.fillna(0)

        if mode == 'percentage':
            df['planExcessQuantity'] = ((df.xProdSol - df.plannedProductionQuantity) / df.plannedProductionQuantity)

        else:
            df['planExcessQuantity'] = df.xProdSol - df.plannedProductionQuantity

        df = df.reset_index()
        df['productCountry'] = np.where(pd.isnull(df.productCountry), '', df.productCountry)
        df['location_product'] = df.productCountry + " - " +  df.productName

        color_discrete_map = self.gen_color_col(df['location_product'])

        if query is not None:
            df = df.query(query)

        df = (df    
            .reset_index()
            ).groupby(['timePeriodSeq', product_aggregation_column, 'lineName', 'productCountry', 'location_product']).sum()
        
        labels = {'timePeriodSeq': 'Time Period', 'xProdSol': 'Production', 'productName': 'Product Name', 
                  'location_product': 'Product Location', 'planExcessQuantity':'Plan Difference'}
        active_line_name_category_orders = [l for l in self.line_name_category_orders if l in df.index.unique(level='lineName')]  # Avoids empty spaces in Plotly chart
        
        # df = df.reset_index()

        category_orders = {
            # 'lineName' : ['Abbott_Weesp_Line','Abbott_Olst_Granulate_Line',
            #                             'Abbott_Olst_Packaging_Line_5','Abbott_Olst_Packaging_Line_6'],
            # 'lineName' : self.line_name_category_orders,
            'lineName' : active_line_name_category_orders,
            # 'timePeriodSeq': [df.timePeriodSeq.sort_values().unique()]
            'timePeriodSeq': df.index.unique(level='timePeriodSeq').sort_values()
        }
        
        fig = px.bar(df.reset_index(), x="timePeriodSeq", y="planExcessQuantity", color='location_product',
                    color_discrete_map=color_discrete_map,
                    title=title, labels=labels,
                    facet_row = 'lineName',
                    category_orders=category_orders,
                    height=800,
                    )

        fig.update_layout(legend = 
                            {'orientation': 'v',
                            'x': 1.05,
                            }
        )

        if mode is not None:
            for axis in fig.layout:
                if type(fig.layout[axis]) == go.layout.YAxis:
                    fig.layout[axis].title.text = ''
                    fig.layout[axis].tickformat = '%'
        
        fig.update_layout(margin = {'l': 85})

        fig.for_each_annotation(lambda a: a.update(x = a.x-1.05, textangle = 270))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("lineName=")[-1]))

        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("_", " ")))
        fig.for_each_annotation(lambda a: a.update(text=a.text.replace("Olst", "Olst<br>")))

        fig.update_layout(hovermode="closest")  # Is supposed to be the default, but in DE we get multiple. Setting 'closest' explicitly is a work-around
    
        # get rid of duplicated X-axis labels
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.YAxis:
                fig.layout[axis].title.text = ''     
        
        fig.update_xaxes(type='category')
        fig.update_layout(hovermode="closest",legend = {'orientation': 'v'},
                          margin= {'l':85,'t':60})

        return fig

    def plotly_inventory_flow_sankey_test(self, include_wip=True):
        """Sankey diagram of transportation activities.
        See https://stackoverflow.com/questions/50486767/plotly-how-to-draw-a-sankey-diagram-from-a-dataframe
        """

        aggregation_column = 'productName'

        # Collect inventories (location-product):

        # for these groupby productGroup instead of productName
        df1 = self.dm.plant_inventories[[]].groupby(['locationName',aggregation_column]).sum().copy()
        df1['type'] = 'plant'
        df2 = self.dm.warehouse_inventories[[]].groupby(['locationName',aggregation_column]).sum().copy()
        df2['type'] = 'warehouse'
        df3 = self.dm.demand_inventories[[]].groupby(['locationName',aggregation_column]).sum().copy()
        df3['type'] = 'demand'
        df4 = pd.DataFrame([{'locationName':'External',aggregation_column:'None', 'type':'external'}]).set_index(['locationName',aggregation_column])
        df5 = self.dm.WIP[[]].groupby(['locationName',aggregation_column]).sum().copy()
        df5 = df5.reset_index()
        df5['locationName'] = df5.locationName + "_wip"
        df5 = df5.set_index(['locationName',aggregation_column])
        df5['type'] = 'wip'
        df6 = self.dm.plant_inventories[[]].groupby(['locationName']).sum().copy()
        df6[aggregation_column] = 'None'
        df6 = df6.reset_index().set_index(['locationName',aggregation_column])
        df6['type'] = 'source'
        product_locations = pd.concat([df5, df4, df1, df2, df3, df6]) # should be same dataframes with same keys

        product_locations = product_locations.reset_index()
        product_locations = product_locations.merge(self.dm.products[['productGroup']], on = 'productName')

        # Create locationName vs id
        inventory_labels_df = (product_locations.reset_index()
                            .reset_index().rename(columns={'index': 'id'})
                            )
        inventory_labels_df['label'] = inventory_labels_df.locationName + " - " +inventory_labels_df['productGroup']
        
        #Collect inventory flows - transportation
        df1 = (self.dm.transportation_activities[['xTransportationSol']].join(self.dm.products[['productGroup']])
            .query("xTransportationSol > 0")
            .groupby(['originLocationName', 'destinationLocationName','shippingMode','productGroup']).sum()
            .rename(columns={'xTransportationSol':'quantity'})
            )

        df1 = df1.reset_index()
        
        df1 = (df1.merge(inventory_labels_df[['locationName','productGroup','id']], left_on=['originLocationName','productGroup'], right_on=['locationName','productGroup'])
            .rename(columns={'id': 'source'})
            .drop(columns=['locationName'])
            )

        df1 = (df1.merge(inventory_labels_df[['locationName','productGroup','id']], left_on=['destinationLocationName','productGroup'], right_on=['locationName','productGroup'])
            .rename(columns={'id': 'target'})
            .drop(columns=['locationName'])
            )
        df1['label'] = df1.shippingMode +  " - " + df1['productGroup'] + " from " + df1.originLocationName + " to " + df1.destinationLocationName  
        df1 = df1.drop(columns=['originLocationName','destinationLocationName','shippingMode'])
        df1['color'] = 'rosybrown' 
        
        aggregation_column = 'productGroup'
        #Collect inventory flows - Production
        df2 = (self.dm.production_activities[['xProdSol']].join(self.dm.products[['productGroup']])
            .join(self.dm.bom_items[['quantity']].rename(columns={'quantity':'component_bom_quantity'}), how='left')
            .join(self.dm.lines[['plantName']])
            .join(self.dm.plants[['locationName']], on='plantName')
            .query("xProdSol > 0")
            .reset_index()
            )

        df2.componentName.fillna('None',inplace=True)  # For any product without components
        df2['component_quantity'] = df2.xProdSol * df2.component_bom_quantity
        df2 = (df2
            .drop(columns=['component_bom_quantity','recipeId','timePeriodSeq'])
            .groupby(['componentName', aggregation_column,'lineName','plantName','locationName']).sum()
            .rename(columns={'xProdSol':'quantity'})
            )
        df2 = df2.reset_index()
   
        df2 = (df2.merge(inventory_labels_df[['locationName',aggregation_column,'id','type']], left_on=['locationName',aggregation_column], right_on=['locationName',aggregation_column])
            .rename(columns={'id': 'target'})
            )
        df2 = (df2.merge(inventory_labels_df[['locationName',aggregation_column,'id','type']], left_on=['locationName','componentName'], right_on=['locationName',aggregation_column], suffixes=[None,'_y'])
            .rename(columns={'id': 'source'})
            .drop(columns=[aggregation_column+'_y'])
            )
        df2['label'] = df2.type + " - " + df2.componentName + " to " + df2[aggregation_column]
        df2 = df2[[aggregation_column, 'quantity', 'source', 'target', 'label']]
        
        df2['color'] = 'olive' 
        
        # Collect inventory flows - WIP
        df3 = (self.dm.WIP[['wipQuantity']].join(self.dm.products[['productGroup']])
            .query("wipQuantity > 0")
            .rename(columns={'wipQuantity':'quantity'})
            )
        df3 = df3.reset_index()
        df3['locationNameWip'] = df3.locationName + '_wip'
    #     display(df3.head())
        df3 = (df3.merge(inventory_labels_df[['locationName',aggregation_column,'id']], left_on=['locationName',aggregation_column], right_on=['locationName',aggregation_column])
            .rename(columns={'id': 'target'})
    #           .drop(columns=['locationName'])
            )
        df3 = (df3.merge(inventory_labels_df[['locationName',aggregation_column,'id']], left_on=['locationNameWip',aggregation_column], right_on=['locationName',aggregation_column], suffixes=[None,'_y'])
            .rename(columns={'id': 'source'})
            .drop(columns=['locationName_y'])
            )
    #     display(df3.head())
        df3['label'] = "wip - " + df3[aggregation_column] + " to " + df3.locationName 
    #     df1 = df1.drop(columns=['locationNameWip','locationName','shippingMode'])
    #     display(df3.head()) 
        df3['color'] = 'lightsalmon' 
        
        
        if include_wip:
            df = pd.concat([df1, df2, df3])
        else:
            df = pd.concat([df1, df2])

        # df = df.merge(self.dm.products[['productGroup']], on = 'productName')
        
        # Set pop-up text
        

    #     df['color'] = 'aquamarine'    
        fig = go.Figure(data=[go.Sankey(
            #         valueformat = ".0f",
            #         valuesuffix = "TWh",
            #         Define nodes
            node=dict(
                pad=15,
                thickness=15,
                line=dict(color="black", width=0.5),
                label=inventory_labels_df.label.array,
            ),
            # Add links
            link=dict(
                source=df.source.array,
                target=df.target.array,
                value=df.quantity.array,
                label=df.label.array,
                color = df.color.array,
            ))])

        fig.update_layout(title_text="",
                        font_size=10,
                        height=1000)
        return fig

    def plotly_inventory_flow_sankey(self, include_wip=True):
        """Sankey diagram of transportation activities.
        See https://stackoverflow.com/questions/50486767/plotly-how-to-draw-a-sankey-diagram-from-a-dataframe
        """
        # Collect inventories (location-product):
        df1 = self.dm.plant_inventories[[]].groupby(['locationName','productName']).sum().copy()
        df1['type'] = 'plant'
        df2 = self.dm.warehouse_inventories[[]].groupby(['locationName','productName']).sum().copy()
        df2['type'] = 'warehouse'
        df3 = self.dm.demand_inventories[[]].groupby(['locationName','productName']).sum().copy()
        df3['type'] = 'demand'
        df4 = pd.DataFrame([{'locationName':'External','productName':'None', 'type':'external'}]).set_index(['locationName','productName'])
        df5 = self.dm.WIP[[]].groupby(['locationName','productName']).sum().copy()
        df5 = df5.reset_index()
        df5['locationName'] = df5.locationName + "_wip"
        df5 = df5.set_index(['locationName','productName'])
        df5['type'] = 'wip'
        df6 = self.dm.plant_inventories[[]].groupby(['locationName']).sum().copy()
        df6['productName'] = 'None'
        df6 = df6.reset_index().set_index(['locationName','productName'])
        df6['type'] = 'source'
        product_locations = pd.concat([df5, df4, df1, df2, df3, df6])
    #     display(product_locations.head())
        # Create locationName vs id
        inventory_labels_df = (product_locations.reset_index()
                            .reset_index().rename(columns={'index': 'id'})
                            )
        inventory_labels_df['label'] = inventory_labels_df.locationName + " - " +inventory_labels_df.productName
    #     display(inventory_labels_df.head())
        
        #Collect inventory flows - transportation
        df1 = (self.dm.transportation_activities[['xTransportationSol']]
            .query("xTransportationSol > 0")
            .groupby(['originLocationName', 'destinationLocationName','shippingMode','productName']).sum()
            .rename(columns={'xTransportationSol':'quantity'})
            )
        df1 = df1.reset_index()
    #     display(df1.head())
        df1 = (df1.merge(inventory_labels_df[['locationName','productName','id']], left_on=['originLocationName','productName'], right_on=['locationName','productName'])
            .rename(columns={'id': 'source'})
            .drop(columns=['locationName'])
            )
    #     display(df1.head())
        df1 = (df1.merge(inventory_labels_df[['locationName','productName','id']], left_on=['destinationLocationName','productName'], right_on=['locationName','productName'])
            .rename(columns={'id': 'target'})
            .drop(columns=['locationName'])
            )
        df1['label'] = df1.shippingMode +  " - " + df1.productName + " from " + df1.originLocationName + " to " + df1.destinationLocationName  
        df1 = df1.drop(columns=['originLocationName','destinationLocationName','shippingMode'])
        df1['color'] = 'rosybrown' 
    #     display(df1.head())
        
        #Collect inventory flows - Production
        df2 = (self.dm.production_activities[['xProdSol']]
            .join(self.dm.bom_items[['quantity']].rename(columns={'quantity':'component_bom_quantity'}), how='left')
            .join(self.dm.lines[['plantName']])
            .join(self.dm.plants[['locationName']], on='plantName')
            .query("xProdSol > 0")
            .reset_index()
    #            .groupby(['locationName', 'plantName','lineName', 'productName']).sum()
            )
        df2.componentName.fillna('None',inplace=True)  # For any product without components
        df2['component_quantity'] = df2.xProdSol * df2.component_bom_quantity
        df2 = (df2
            .drop(columns=['component_bom_quantity','recipeId','timePeriodSeq'])
            .groupby(['componentName', 'productName','lineName','plantName','locationName']).sum()
            .rename(columns={'xProdSol':'quantity'})
            )
        df2 = df2.reset_index()
    #     display(df2.head())
        df2 = (df2.merge(inventory_labels_df[['locationName','productName','id','type']], left_on=['locationName','productName'], right_on=['locationName','productName'])
            .rename(columns={'id': 'target'})
            )
        df2 = (df2.merge(inventory_labels_df[['locationName','productName','id','type']], left_on=['locationName','componentName'], right_on=['locationName','productName'], suffixes=[None,'_y'])
            .rename(columns={'id': 'source'})
            .drop(columns=['productName_y'])
            )
        df2['label'] = df2.type + " - " + df2.componentName + " to " + df2.productName
        df2 = df2[['productName', 'quantity', 'source', 'target', 'label']]
        
        df2['color'] = 'olive' 
    #     display(df2.head())
        
        # Collect inventory flows - WIP
        df3 = (self.dm.WIP[['wipQuantity']]
            .query("wipQuantity > 0")
            .rename(columns={'wipQuantity':'quantity'})
            )
        df3 = df3.reset_index()
        df3['locationNameWip'] = df3.locationName + '_wip'
    #     display(df3.head())
        df3 = (df3.merge(inventory_labels_df[['locationName','productName','id']], left_on=['locationName','productName'], right_on=['locationName','productName'])
            .rename(columns={'id': 'target'})
    #           .drop(columns=['locationName'])
            )
        df3 = (df3.merge(inventory_labels_df[['locationName','productName','id']], left_on=['locationNameWip','productName'], right_on=['locationName','productName'], suffixes=[None,'_y'])
            .rename(columns={'id': 'source'})
            .drop(columns=['locationName_y'])
            )
    #     display(df3.head())
        df3['label'] = "wip - " + df3.productName + " to " + df3.locationName 
    #     df1 = df1.drop(columns=['locationNameWip','locationName','shippingMode'])
    #     display(df3.head()) 
        df3['color'] = 'lightsalmon' 
        
        if include_wip:
            df = pd.concat([df1, df2, df3])
        else:
            df = pd.concat([df1, df2])
        
        # Set pop-up text
        
    #     display(df.head())

    #     df['color'] = 'aquamarine'    
        fig = go.Figure(data=[go.Sankey(
            #         valueformat = ".0f",
            #         valuesuffix = "TWh",
            #         Define nodes
            node=dict(
                pad=15,
                thickness=15,
                line=dict(color="black", width=0.5),
                label=inventory_labels_df.label.array,
            ),
            # Add links
            link=dict(
                source=df.source.array,
                target=df.target.array,
                value=df.quantity.array,
                label=df.label.array,
                color = df.color.array,
            ))])

        fig.update_layout(title_text="",
                        font_size=10,
                        height=1000,
                        margin={'l':40, 'r':40, 't':40})
        return fig



    def plotly_line_product_group_capacity_heatmap(self):
        """Heatmap of capacity as line vs product. Good insight on line specialization/recipe-properties.
        Input tables: ['RecipeProperties', 'Line', 'Product']
        Output tables: []
        """
        df = (self.dm.recipe_properties[['capacity']]
            .join(self.dm.lines)
            .join(self.dm.products[['productGroup']])
            #           .join(self.dm.plants.rename(columns={'locationDescr':'plantDescr'}), on='plantName')
            #           .join(self.dm.locations, on='locationName')
            )  # .groupby(['lineName','productType']).max()
        df = df.reset_index()
        # df = df.pivot_table(values='capacity', index=['lineDescr'], columns=['productType'], aggfunc=np.max)
        df = df.pivot_table(values='capacity', index=['lineName'], columns=['productGroup'], aggfunc=np.max)

        labels = {'lineName': 'Line', 'productGroup': 'Product Group', 'productName': 'Product Name'}
        labels = dict(x="Product Group", y="Line", color="Capacity")
        fig = px.imshow(df, labels=labels, width=1000,
                        color_continuous_scale='YlOrRd',
                        # y = ["Abbott Olst<br>Granulate Line", "Abbott Olst<br>Packaging Line 5", 
                        #         "Abbott Olst<br>Packaging Line 6", "Abbott<br>Weesp Line"],
                        y = ["Granulate Line", "Packaging Line 1",  "Packaging Line 2", "API Line"],
                        x = ["API", "Granulate", "Tablet", "Package"],
        )

        fig.update_layout(
            title={
                'text': "Maximum Line Capacity by Product Type",
                # 'y': 0.92,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})

        return fig

    

    @plotly_figure_exception_handler
    def plotly_transportation_bar(self, query = None, title = 'Transportation Activity'):
        """
        """
        df = self.dm.transportation_activities[['xTransportationSol']].query("xTransportationSol > 0")\
            .join(self.dm.products[['productGroup', 'productCountry']])\
            .groupby(['timePeriodSeq', 'originLocationName', 'destinationLocationName','shippingMode','productName']).\
            sum().rename(columns={'xTransportationSol':'quantity'})

        if query is not None:
            df = df.query(query).copy()
            # title = "Departing From: " + query.split("originLocationName == ")[-1].replace("_", " ").replace("'","")
        else:
            pass
            # title = "Transportation Activity"

        df = df.join(self.dm.products[['productGroup', 'productCountry']])

        df = df.reset_index()

        df.productCountry = df.productCountry.fillna("")
        df['location_product'] = df['productCountry'] + " - " + df['productName']
        df['location_product'] = df['location_product'].fillna('API')

        color_discrete_map = self.gen_color_col(df['location_product'])

        labels = {'location_product': 'Product Location', 'timePeriodSeq': 'Time Period', "quantity": 'Quantity'}

        if len(df.shippingMode.unique()) < 2:
            fct = None
        else:
            fct = "shippingMode"

        category_orders = {'shippingMode': ['Air', 'Sea', 'Truck', 'Rail']}
        active_shipping_mode_category_orders = [sm for sm in ['Air', 'Sea', 'Truck', 'Rail'] if sm in df.shippingMode.unique()]

        fig = px.bar(data_frame = df, x = "timePeriodSeq", y = "quantity", color = "location_product", 
                    labels = labels,
                    facet_col = fct,
                    # category_orders = category_orders,
                    category_orders = {'shippingMode': active_shipping_mode_category_orders},
                    color_discrete_map=color_discrete_map)

        fig.update_layout(title = title, legend = {'orientation': 'v', 'x': 1.05},
                          margin = {'l':80, 't':80})

        if len(df.shippingMode.unique()) > 1:
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("shippingMode=")[-1].capitalize()))

        fig.update_layout(hovermode="closest")

        return fig

    def demand_choropleth_map(self):
        """"""
        df = (self.dm.demand
         .join(self.dm.products[['productGroup', 'productCountry']]))

        
        # Set location_product name
        df = df.reset_index()
        df['location_product'] = df.locationName + " - " + df.productName

        df = (df
            .groupby(['timePeriodSeq', 'location_product', 'productCountry']).sum()
            .sort_values('quantity', ascending=False))
        
        # locs = pd.read_csv('/workspace/geocode_abbott_locations_fixed.csv')

        # print(self.dm.locations.head())
        # print(locs.head())
        locs = self.dm.locations.reset_index()

        df = df.reset_index()
        df = df.merge(locs[["locationName", "latitude", "longitude", "countryIso"]], left_on = "productCountry", right_on = "locationName")

        df_gby = df.groupby("countryIso")['quantity'].mean().reset_index()

        fig = px.choropleth(df_gby, 
                    locations = "countryIso",
                    color = "quantity",
                    width = 1200,
                    title = "Demand Choropleth Map")
        
        fig.update_layout(paper_bgcolor='#edf3f4',
                            geo=dict(bgcolor= '#edf3f4', showframe = False),
                            margin = {'b': 0, 't':50},
                            title = {'y': 0.95},
                            coloraxis_colorbar=dict(title="Quantity")
        )
        return fig

    def unfulfilled_demand_choropleth_map(self, animation_col = None):
        """
        """
        df0 = (self.dm.transportation_activities[['xTransportationSol']]
            .groupby(['productName', 'destinationLocationName', 'timePeriodSeq']).sum()
            .rename_axis(index={'destinationLocationName': 'locationName'})
            .rename(columns={'xTransportationSol':'Transportation'})
            )
        
        product_aggregation_column = 'productName'
        df = (self.dm.demand_inventories[['quantity','xFulfilledDemandSol','xUnfulfilledDemandSol','xBacklogSol','xBacklogResupplySol','xInvSol']]
                    .join(self.dm.products[['productGroup', 'productCountry']])
                    #           .join(self.dm.locations)
                    .join(df0, how='left')
                    ).groupby(['timePeriodSeq', 'productCountry', product_aggregation_column]).sum()

        df = df.reset_index()

        # locs = pd.read_csv('/workspace/geocode_abbott_locations_fixed.csv')
        locs = self.dm.locations.reset_index()

        df = df.merge(locs[["locationName", "latitude", "longitude", "countryIso"]], left_on = "productCountry", right_on = "locationName")

        if animation_col is not None:
            df_gby = df.groupby(["countryIso", animation_col])['xUnfulfilledDemandSol'].mean().reset_index()
            title = "Animated Unfulfilled Demand Choropleth Map"
            width = 2000
        else:
            df_gby = df.groupby("countryIso")['xUnfulfilledDemandSol'].mean().reset_index()
            title = "Unfulfilled Demand Choropleth Map"
            width = 1000

        fig = px.choropleth(df_gby, 
                    locations = "countryIso",
                    color = "xUnfulfilledDemandSol",
                    animation_frame=animation_col,
                    animation_group = animation_col,
#                     facet_col = "productGroup",
                   width = width,
                #    height = 1000,
                   title = title)
        
        fig.update_layout(legend = {'title': 'Quantity'},
                            paper_bgcolor='#edf3f4',
                            geo=dict(bgcolor= '#edf3f4', showframe = False),
                            margin = {'b': 0, 't':50},
                            title = {'y': 0.95},
                            width = width,
                            coloraxis_colorbar=dict(title="Quantity")
                            )

        return fig
    
    def line_map(self):
        """
        """
        import math
        import random

        aggregation_column = 'productName'
        #Collect inventory flows - transportation
        df1 = (self.dm.transportation_activities[['xTransportationSol']].join(self.dm.products[['productGroup']])
            .query("xTransportationSol > 0")
            .groupby(['originLocationName', 'destinationLocationName','shippingMode','productGroup']).sum()
            .rename(columns={'xTransportationSol':'quantity'})
            )
        df1 = df1.reset_index()

        # locs = pd.read_csv('/workspace/geocode_abbott_locations_fixed.csv')
        locs = self.dm.locations.reset_index()

        map_locs = df1.drop_duplicates(['originLocationName', 'destinationLocationName', 'shippingMode', 'productGroup', 'quantity'])
    
        df6 = map_locs.merge(locs[["locationName", "latitude", "longitude", "countryIso"]], left_on = "originLocationName", right_on = "locationName")
        df6 = df6.rename({'latitude': 'origin_lat', 'longitude':'origin_lon', 'countryIso':'origin_iso3'}, axis = 1)
        df6 = df6.merge(locs[["locationName", "latitude", "longitude", "countryIso"]], left_on = "destinationLocationName", right_on = "locationName")
        df6 = df6.rename({'latitude': 'destination_lat', 'longitude':'destination_lon', 'countryIso':'destination_iso3'}, axis = 1)

        fig = go.Figure()

        fig = fig.add_trace(go.Scattergeo(
        #     locationmode = 'USA-states',
            lon = df6['origin_lon'],
            lat = df6['origin_lat'],
            hoverinfo = 'text',
            text = df6['originLocationName'],
            name = "Supply Chain Origin",
            # showlegend = False,
            mode = 'markers',
            marker = dict(
                size = 8,
                color = 'rgb(255, 0, 0)',
            )))

        df6 = df6.reset_index().copy()
        # add some jitter to prevent overlays
        random.seed(42)
        df6['destination_lat'] = df6['destination_lat'].apply(lambda x : x + random.uniform(-0.75, 0.75))
        df6['destination_lon'] = df6['destination_lon'].apply(lambda x : x + random.uniform(-0.75, 0.75))

        fig = fig.add_trace(go.Scattergeo(
            # locationmode = 'USA-states',
            lon = df6['destination_lon'],
            lat = df6['destination_lat'],
            hoverinfo = 'text',
            text = df6['destinationLocationName'],
            name = "Supply Chain Destination",
            mode = 'markers',
            marker = dict(
                size = df6.quantity.apply(math.log).clip(lower = 2)*2,
                color = "blue",
            )))
        
        color_dict = {'sea': 'darkblue', 'truck': 'darkgreen', 'air': 'darkred', 'Sea': 'darkblue', 'Truck': 'darkgreen', 'Air':'darkred'
        }

        df6['showlegend'] = False

        df6['linetype'] = "solid"

        ix = df6.groupby('shippingMode').first()['index'].values
        for i in ix:
            df6['showlegend'].iloc[i] = True

        for i in range(len(df6)):
            fig.add_trace(
                go.Scattergeo(
                    lon = [df6['origin_lon'][i], df6['destination_lon'][i]],
                    lat = [df6['origin_lat'][i], df6['destination_lat'][i]],
                    mode = 'lines',
                    name = df6['shippingMode'][i],
                    showlegend = bool(df6['showlegend'][i]),
                    # showlegend = False,
                    line_dash= df6['linetype'][i],
                    line = dict(width = 1,color = color_dict[df6['shippingMode'][i]]),
        #             opacity = float(df_flight_paths['cnt'][i]) / float(df_flight_paths['cnt'].max()),
                )
            )
        # adding a choropleth on top
        df = (self.dm.demand
                .join(self.dm.products[['productGroup', 'productCountry']])
                )
            
        # Set location_product name
        df = df.reset_index()
        df['location_product'] = df.locationName + " - " + df.productName

        df = (df
            .groupby(['timePeriodSeq', 'location_product', 'productCountry']).sum()
            .sort_values('quantity', ascending=False))

        df = df.reset_index()

        df = df.merge(locs[["locationName", "latitude", "longitude", "countryIso"]], left_on = "productCountry", right_on = "locationName")

        df = df.sort_values('timePeriodSeq')

        df_gby = df.groupby("countryIso")['quantity'].mean().reset_index()

        fig = fig.add_trace(
            go.Choropleth(
                locations = df_gby['countryIso'],
                z = df_gby['quantity'],
                colorscale = "Reds",
                colorbar_title = "Quantity"
            )
        )

        fig.update_layout(coloraxis_colorbar_x=-1)

        fig.update_layout(
            width = 1000,
            # height = 1000,
            legend = {
                'title': 'Transportation Type',
                'orientation': 'v',
                'x': 0.85,
                'y': 0.9,
            },
            title = {'text': "Supply Chain Overview", 'y': 0.95},
            margin = {
                't': 50,
                'b': 0,
            },
            paper_bgcolor='#edf3f4',
            geo=dict(bgcolor= '#edf3f4', showframe = False),
    )


        return fig
    
    def percent_unfullfilleddemand(self):
        # product_aggregation_column = 'productGroup' # potentially for further unpacking
        df = (self.dm.demand_inventories[['quantity','xUnfulfilledDemandSol']])
            # .join(self.dm.products[['productGroup']])
            # ).groupby(['timePeriodSeq']).sum()

        unfulfilled_demand = df.xUnfulfilledDemandSol.groupby(['timePeriodSeq']).sum()
        num_tp = len(self.dm.demand.index.unique(level='timePeriodSeq'))
        average_monthly_demand = df.quantity.sum()/num_tp

        final_df = (unfulfilled_demand/average_monthly_demand).replace([np.inf, -np.inf], np.nan).fillna(0).round(4)*100

        # final_df = final_df.groupby('timePeriodSeq').mean()

        return final_df

    def percent_backlog(self):
        # product_aggregation_column = 'productGroup'
        df = (self.dm.demand_inventories[['quantity','xBacklogSol']])
            # .join(self.dm.products[['productGroup']])
            # ).groupby(['timePeriodSeq']).sum()
        
        backlog = df.xBacklogSol.groupby('timePeriodSeq').sum()

        num_tp = len(self.dm.demand.index.unique(level='timePeriodSeq'))

        average_monthly_demand = df.quantity.sum()/num_tp

        # final_df = (df.xBacklogSol/df.quantity).replace([np.inf, -np.inf], np.nan).fillna(0).round(4)*100

        final_df = (backlog / average_monthly_demand).replace([np.inf, -np.inf], np.nan).fillna(0).round(4)*100

        # final_df = final_df.groupby('timePeriodSeq').mean()

        return final_df
    
    def dos_inv(self):
        # product_aggregation_column = 'productGroup'

        # print(self.dm.products)

        # can feed it plant or warehouse inventories

        df_demand = (self.dm.demand_inventories[['quantity','xFulfilledDemandSol','xUnfulfilledDemandSol','xBacklogSol','xBacklogResupplySol','xInvSol']])
            # .join(self.dm.products[['productGroup']])
            # ).groupby(['timePeriodSeq']).sum()

        df_inv = (self.dm.demand_inventories[['quantity','xFulfilledDemandSol','xUnfulfilledDemandSol','xBacklogSol','xBacklogResupplySol','xInvSol']])
            # .join(self.dm.products[['productGroup']])
            # ).groupby(['timePeriodSeq']).sum()


        final_df = (df_demand.groupby(["productName", "timePeriodSeq"]).xInvSol.sum()/df_inv.groupby(["productName", "timePeriodSeq"]).\
                    quantity.sum()).replace([np.inf, -np.inf], np.nan).fillna(0).round(4)

        final_df = pd.Series(final_df.groupby('timePeriodSeq').mean().values)


        t = self.get_demand_location_dos(30).groupby(['timePeriodSeq']).agg({'dosQuantity': 'sum'})
        t = pd.Series(t.reset_index()['dosQuantity'])
    
        final_dos = (final_df/t)
        
        return final_dos
    
    def average_inv(self):
        # product_aggregation_column = 'productGroup'
        # num_timeperiods = self.dm.active_timeperiods.max()
        num_timeperiods = 30

        df_inv = (self.dm.demand_inventories[['xInvSol']]
            # .join(self.dm.products[['productGroup']])
            ).groupby(['timePeriodSeq']).sum()

        final_df = (df_inv.xInvSol/num_timeperiods).round(4)
        # final_df = final_df.groupby('timePeriodSeq').mean()

        return final_df

    def get_demand_location_dos(self, dos:int):
        """Compute the quantity of product at the end of a time-period that represents the 
        Days-Of-Supply computed using the actual demand in the following time-periods.
        The quantity can be used in a days-of-supply inventory constraint or objective.
        For the last time-periods, assume demand remains constant with the value of the last time-period.
        
        Args:
            dos (int): Days-Of-Supply. Number of days.
            
        Note: use dm.demand_inventories. Is has already expanded to all time-periods.
        """
    #     num_tps = 24  # Number of time-periods
        
        # num_days_tp = 30  # Number of days per time-period. To keep it simple, use 30 per month. HARD-CODED for now. TODO: put in parameter, or add as column in TimePeriods
        num_days_tp = len(self.dm.demand.index.unique(level='timePeriodSeq')) * 30
        # print(self.dm.demand_inventories.head())
        df = (self.dm.demand_inventories[['quantity']]
            .sort_index()  # sort index so the shift will work right
            ).fillna(0)
    
        num_tps = len(df.index.unique(level='timePeriodSeq'))-1
    #     df['numDays'] = num_days_tp
        df['demandPerDay'] = df.quantity / num_days_tp  #df.numDays
        df['nextDemandPerDay'] = df.demandPerDay  # Note we are shifting the nextDemandPerDay, so initialize once
        df['dosQuantity'] = 0  # We are incrementing the dosQuantity, so initialize
        
        remaining_dos = dos  # Remaining DOS in each iteration, initialize with all DOS
        shift = 0  # Only for debuging
        
        # Iterate over the next time-periods until it covers all requested dos days
        # Sum the DOS quantity
        # Assume demand is constant throughout the time-period
        while remaining_dos > 0:
            # print(remaining_dos)
            shift = shift + 1
            # print(shift)
            next_dos = min(remaining_dos, num_days_tp)
    #         print(f"Shift = {shift}, remaining_dos = {remaining_dos}, next_dos={next_dos}")
            df['nextDemandPerDay'] = df.groupby(['locationName','productName'])['nextDemandPerDay'].shift(-1)  #, fill_value=0)  
            # print(df.head())
            # print(num_tps)
            # print(df.loc[pd.IndexSlice[:,:,num_tps],'demandPerDay'])
            df.loc[pd.IndexSlice[:,:,num_tps],'nextDemandPerDay'] = df.loc[pd.IndexSlice[:,:,num_tps],'demandPerDay']  # Fill gap from the shift with last demand
            # print("test")
            df['dosQuantity'] = df.dosQuantity + df.nextDemandPerDay * next_dos
            
            remaining_dos = remaining_dos - next_dos
            # print("test")
    #         display(df.query("locationName=='NAMIBIA'").head(24))
        df = df.drop(columns=['demandPerDay', 'nextDemandPerDay'])

        # print(df)
        return df
    
    def kpi_heatmap(self):
        '''
        '''

        cols = [self.percent_unfullfilleddemand(), self.percent_backlog(), self.dos_kpi(as_time = True), 
                self.calc_air_pct(as_time = True), self.utilization_kpi(as_time = True)]

        final_df = pd.DataFrame(data= cols).\
                    rename({'xUnfulfilledDemandSol': 'unfulfilled_demand', 'xBacklogSol': 'backlog', 'xInvSol': 'dos_inv', 
                            'Unnamed 0': 'air_sea_ratio', 'line_capacity_utilization': 'utilization'}, 
                        axis = 0)
        
        heatmap_df = final_df.copy()

        # make a green zone around 30 days and orange if between 10-20 and 40-50, then red between 0-10 and 50-60
        heatmap_df.loc['dos_inv'] = np.where((heatmap_df.loc['dos_inv'] <=  10)  | (heatmap_df.loc['dos_inv'] >= 60), 2, 
                                        np.where((heatmap_df.loc['dos_inv'] >= 40) & (heatmap_df.loc['dos_inv'] < 60), 1,
                                            np.where((heatmap_df.loc['dos_inv'] >= 20) & (heatmap_df.loc['dos_inv'] < 40), 0, np.nan)))


        heatmap_df.loc['unfulfilled_demand'] = np.where(heatmap_df.loc['unfulfilled_demand'] > 5, 2, 
                                                    np.where(heatmap_df.loc['unfulfilled_demand'] < 2, 0, 1))

        heatmap_df.loc['backlog'] = np.where(heatmap_df.loc['backlog'] > 10, 2, 
                                        np.where(heatmap_df.loc['backlog'] < 5, 0, 1))
        
        heatmap_df.loc['air_sea_ratio'] = np.where(heatmap_df.loc['air_sea_ratio'] > 50, 2, 
                                                    np.where(heatmap_df.loc['air_sea_ratio'] < 20, 0, 1))

        heatmap_df.loc['utilization'] = np.where(heatmap_df.loc['utilization'] > 95, 2, 
                                                    np.where(heatmap_df.loc['utilization'] < 85, 0, 1))

        # final_df = final_df.apply(lambda x:(x - x.min())/(x.max() - x.min()), axis = 0)

        fig = px.imshow(heatmap_df,
                        color_continuous_scale =["green", "orange", "red"],
                        y = ["Unfulfilled Demand %", "Backlog %", "Inventory<br>Days of Supply", "Air Shipping %", "Utilization %"]
                        )
        # customdata allows to add an "invisible" dataset that is not being plotted but whose values can be used for reference
        fig.update_traces(customdata= final_df,
                   hovertemplate = 
                   "%{y}: %{customdata: .3f}"+
                   "<br>Time Period %{x}"+
                   '<extra></extra>')

        fig.update(layout_coloraxis_showscale=False)
        fig.update_layout(margin = {'b':40, 'l':140, 'r':10, 't':20}) # hide colorbar

        return fig
    
    def make_gauge(self, value: float, title: str, orange_threshold: float, red_threshold: float, max_val: float):
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
            )
        )   
        
        fig.update_layout(font = {'color': 'green' if value < orange_threshold else 'orange' if value > orange_threshold and value < red_threshold else 'red', 'family': "Arial"},
                          margin={'t':10,'b':30},
                          )

        return fig

    def make_gauge_dos(self, value: float, title: str, max_val: float, type = None):
        ''' Standalone function for the DOS gauge
        '''

        steps = [
            {'range': [0, 10], 'color': 'red'},
            {'range': [60, max_val], 'color': 'red'},
            {'range': [10, 20], 'color': 'orange'},
            {'range': [40, 60], 'color': 'orange'},
            {'range': [20, 40], 'color': 'green'},
        ]

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, .75]},
            title = {'text': title, 'font': {'color': 'black', 'size': 18}},
            gauge = {'axis': {'range': [None, max_val], 'tickfont': {'color': 'black'}},
                     'threshold' : {'line': {'color': "darkred", 'width': 4}, 'thickness': 0.75, 'value': 60},
                     'steps': steps,
                     'bar': {'color': "darkblue"},},
            )
        )   
        
        fig.update_layout(font = {'color': 'green' if value < 40 and value > 20 else 'orange' if ((value > 40 and value < 60) or (value > 10 and value < 20)) else 'red', 'family': "Arial"},
                          margin={'t': 10, 'b': 30})

        return fig

    
    def calc_air_pct(self, as_time = False):
        """
        When setting as_time = True, returns a vector with a value at each time index.
        The issue is that not all time indices have a value for air or sea shipping. 
        A hacky solution: create a df initialized to 0 with all combinations of timePeriodSeq and shippingMode (i.e. 21 time periods * 3 shippingModes)
        then iterate over the original df that was grouped by timePeriodSeq and shippingMode, 
        check if the grouped data has a value for that time/shippingMode combination, 
        if yes then copy/paste that value
        if no, then keep 0 as the value
        TODO: Probably a better way to write that code
        """
        import warnings
        warnings.filterwarnings("ignore")

        print(pd.__version__)

        df = self.dm.transportation_activities[['xTransportationSol']].query("xTransportationSol > 0")\
            .join(self.dm.products[['productGroup', 'productCountry']])\
            .groupby(['timePeriodSeq', 'originLocationName', 'destinationLocationName','shippingMode','productName']).\
            sum().rename(columns={'xTransportationSol':'quantity'})
        
        if not 'Air' in df.index.get_level_values('shippingMode') and as_time:
            num_tp = len(self.dm.demand.index.unique(level='timePeriodSeq'))
            return pd.Series(index = range(num_tp+1), data = 0)
        elif not 'Air' in df.index.get_level_values('shippingMode') and not as_time:
            return 0
        
        if as_time:
            df = df.reset_index()
            from itertools import product
            df_gby = df.groupby(['shippingMode', 'timePeriodSeq']).sum().reset_index()

            dft = pd.DataFrame(product(df['shippingMode'].unique(),
                 df['timePeriodSeq'].unique()), columns = ['shippingMode', 'timePeriodSeq'])

            dft['quantity'] = 0

            ### HACK ### probably a better way to write this code
            for i in range(len(dft)):
                sm = dft['shippingMode'].iloc[i]
                ts = dft['timePeriodSeq'].iloc[i]
                if len(df_gby.loc[(df_gby.shippingMode == sm) & (df_gby.timePeriodSeq == ts)]['quantity']) != 0:
                    dft['quantity'].iloc[i] = df_gby.loc[(df_gby.shippingMode == sm) & (df_gby.timePeriodSeq == ts)]['quantity']
                else:
                    continue
                
            air = dft.loc[dft.shippingMode == 'Air'].quantity.values
            sea = dft.loc[dft.shippingMode == 'Sea'].quantity.values

            ratio = pd.Series(air/(air+sea)).replace([np.inf, -np.inf], np.nan).fillna(0).round(3)
                   
        else:
            df_gby = df.groupby('shippingMode').sum()

            air = df_gby.loc[df_gby.index == 'Air'].quantity.values
            sea = df_gby.loc[df_gby.index == 'Sea'].quantity.values

            ratio = air/(sea+air)

            ratio = np.round(ratio, 3)

        return ratio*100
    
    def utilization_kpi(self, as_time = False):
        """
        """

        product_aggregation_column = 'productGroup'
        df = (self.dm.production_activities[['line_capacity_utilization']]
             .join(self.dm.products[['productGroup']])
             ).groupby(['timePeriodSeq', 'lineName', product_aggregation_column]).sum().reset_index()

        # df = df[df['lineName'] == 'Abbott_Olst_Packaging_Line_5']
        df = df[df['lineName'].isin(['Abbott_Olst_Packaging_Line_5', 'Packaging_Line_1'])]  # works both for Client and Pharma
        # df = df[df['lineName'] == 'Packaging_Line_1']  # Ony for Pharma

        df['line_capacity_utilization'] = (df['line_capacity_utilization'].replace(0, np.nan)*100)
        # VT notes 20211122: why the replace 0 with Nan? Probably to force the mean() to ignore months that have zero utilization?
        # TODO: why not filter?
        # df['line_capacity_utilization'] = (df['line_capacity_utilization']*100)

        if as_time:
            return df.set_index('timePeriodSeq')['line_capacity_utilization'].sort_index()
        else:
            return float(df.groupby('lineName')['line_capacity_utilization'].mean())
    
    def dos_kpi(self, as_time = False):
        '''
        '''
        df = self.dm.demand_inventories[['quantity', 'xInvSol']]
            
        num_days = len(self.dm.demand.index.unique(level='timePeriodSeq')) * 30

        demand_inv = df.groupby('timePeriodSeq')['xInvSol'].sum()

        total_demand = df['quantity'].sum()

        demand_dos = demand_inv / (total_demand / num_days)

        if as_time:
            return demand_dos
        else:
            return float(demand_dos.mean())



        

