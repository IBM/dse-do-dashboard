# DO Dash App User Manual
This manual describes the generic components of the DO Dash App.

Contents:
* Top menu bar
* Home page
* Prepare Data page
* Run Model page
* Explore Solution page
* Visualization pages

## High-level Introduction
The DO Dash App contains 3 main areas:
1. The top-level menu bar. The logo and title can be customized.
2. The left-side menus to select which page is showing in the main areas. There are 2 sets of pages:
   - Main Pages. These are the default pages that implement generic visualization, 
reporting and interaction with the selected scenario.
   - Custom Visualization Pages. These pages implement specific visualizations for the application.
3. The main dahboard area where Visualization Pages show their page. The area where the page selected on the left is visualized.

## Top menu bar
The top menu bar contains
* Logo. Based on the `logo_file_name` of a file in the dashboard/assets folder.
* Title. Based on the `navbar_brand_name` of the DoDashApp.__init__()
* Scenario drop-down. Shows the names of all scenarios in the scenario database. 
By default, selects the first scenario in the DB. Switching scenario will load the tables based on the Visual Page requirements.
Tables will be cashed to improve performance.
* Refresh button. Refresh will clear the cache and thus force a redo any of the DB queries. If the scenario DB has been modified, 
the user may need to refresh, so we can see any new scenarios or other updates.
Note that this just clears the cache, it is not the same as a more intensive browser page reload, which will cause the Dash app to restart.


## Home page
The Home page contains:

### Reference Scenario
Select **one** scenario as the reference. 
Visualization pages that support scenario compare will receive the scenario data for both 
the selected scenario and the reference scenario. It is up to the specific Visualization Page to use this data to 
create scenario compare visualizations. 
The Visualization page should compare the currently selected scenario with the reference scenario.
Typically, the reference scenario stay constant and the user can easily switch the current scenanrio from the top dowp-down menu.
Note that this tends to be complex and is rarely implemented. One exception is the KpiComparePage. 

### Reference Scenarios
This is an alternative to the (single) Reference Scenario.
This option allows to compare multiple scenarios, not just two.
In a similar way, each Visualization page will need to implement this scenario compare visualization.
<!---
TODO: Does it include the current scenario?
-->
* Scenarios
* 

### Scenarios
This is a list of all scenarios. Each scenario has a dropdown with:
* Duplicate: creates a duplicate scenario. It generates a unique name. You can change the name in the dialog.
* Rename
* Download: as Excel file
* Delete

Note: if there are a large amount of scenarios (20-30 or more), the performance of this page will suffer due to the nature of the dropdown implementation.
<!---
TODO: Change to an AGGrid implementation
-->

### Download All Scenarios
Expand the harmonica to show the options.
Button to download all scenarios as Excel files within one zip file.

### Upload Scenarios
Expand the harmonica to show the options.
Upoad either a single Excel file, a set of Excel files, or a single zip-file with one or more Excel files.
Scenario name is based on the name fo the Excel file.
Scenarios will overwrite scenarios with same name.
Includes a drag-and-drop area where the user can drop files or select files.

### Stop Server
Expand the harmonica to show the options.
Press this button to stop the Dash App and release the port.
This is not necessary in Windows or Mac. In those cases, the port is automatically released if the \
script that started the Dash App is stopped.
However, on CP4D, the port was not released automatically/immediately. 
This button is a safer approach to stop the Dash App.

## Prepare Data
Shows default table views of each input table. Select input table from drop-down at the top.
Automatically selects the first table.
In addition, at the bottom is a pivot table view of the same data.
By default, it doesn't have a configuration, so it will render empty.
But in the DO Dash App, one can override the method `get_pivot_table_configs()` 
and provide default pivot configurations.

### Editing the input data
It is possible to edit the cells in the table. This allows a user to modify the scenario and do what-if analysis.
Each change to the value of cell is captured in the Dash App. The change is not immediately commited to the DB.
If there are changes, the user will see a red 'commit' button appear. Pressing the button will commit the changes into the DB.
<!--
TPDO: do we need to refresh?
-->

## Run Model
Allow the user to run the OptimizationEngine based on the current scenario.
Requires overriding the DoDashApp method `get_do_model_runner_configs()`.
There are 3 types of DoModelRunners:
- Class. Uses the OptimizationModel and DataManager. Runs the model locally, i.e. where the DashApp is running. Requires CPLEX to be installed.
- Notebook. Runs a 'solver' notebook. These would be the kind of notebook we would have in CP4D and the one that we would import into the DO Experiment. 
That is, it expects the `inputs` dictionary to be present and will generate all outputs in the `outpust` dictionary. 
Notebook is run locally to the DoDashApp.
- WML. Calls a deployed DO model in WML. Assumes the DO model has already been deployed in WML. 
Requires credentials, etc. Does not require a local CPLEX.

At the top is a drop-down to select which runner to use. By default will select the first.
There are 3 buttons:
- Run Model inline. Runs the model in an 'inline' fashion, i.e. you cannot navigate away from the current page. While the model is running, you can select the 'Update JobQueue' to see the current status of the run.
- Run Model LRC. Runs the model using Dash 'Long Running Callback'. This would allow a user to continue to navigate through the dashboard, 
while the optimization model is running in the background. Requires a cache.
<!--
TODO: document how to setup
-->
- Update JobQueue. The current status and log of the run are not automatically updated. Press this button to force an update.

## Explore Solution
This is the same visualizations as in Prepare Data, but now on the output tables.

## Visualization
The 'Visualization' main page button (blue letters) shows all custom visualization pages in a tab format in the main area.

## Custom Visualization Pages
These show as black letters below the blue lettered Main Pages. 
The list of custom visualization pages cna be collapsed using the "Visualiation Pages' button.
Each custom visualization specifies a specific set of input and output pages. 
Only these tables will be loaded once the user selects a page for a given curent scenario.
These tables are cached, so that switching between pages is efficient.