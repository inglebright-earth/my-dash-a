# Import necessary libraries and modules for the dashboard application
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from functions import processLucasData  # Custom function for processing LUCAS data
import plotly.graph_objs as go
import plotly.express as px
import geopandas as gpd
import pandas as pd
pd.options.mode.copy_on_write = True  # Enable copy-on-write mode for pandas
import base64
import io

# Initialise the Dash application with a specific theme from Dash Bootstrap Components
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SPACELAB],
)
server = app.server

"""
Helper functions for file parsing and data manipulation
"""
def parse_contents(contents, filename):
    """
    Parses the contents of an uploaded file and extracts the year from the filename.
    It specifically supports CSV files and relies on naming conventions to extract the year.
    """
    # Split the content into type and data, then decode the data from base64
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    # Check if the file is a CSV and its filename length to determine the year format
    if 'csv' in filename and len(filename) >= 18:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        year = int(filename[3:7])
        return(df, year)
    elif 'csv' in filename and len(filename) < 18:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        year = int(filename[-8:-4])
        return(df, year)

def createCountryYearColumn(df):
    """
    Processes a DataFrame by dropping missing values, converting the 'Year' column to string,
    and creating a new column 'countryYear' by concatenating 'Country' and 'Year'.
    The DataFrame is then sorted by this new column.
    """
    df1 = df.dropna()
    df1['Year'] = df1['Year'].astype(str)
    df1['countryYear'] = df1['Country'] + ' ' + df1['Year']
    return df1

def reorder_df(df):
    """
    Reorders the DataFrame for visualization purposes by merging count and percentage data
    for different classes into a single DataFrame. This facilitates comparative analysis.
    """
    # Ensure required columns are present
    required_columns = ['Livestock %', 'Arable %', 'Forest %', 'Shrubland %', 'Grassland %']
    if not all(column in df.columns for column in required_columns):
        raise ValueError("DataFrame does not contain all required columns for melting.", df.columns)
    
    # Create a 'countryYear' column for merging purposes
    df['countryYear'] = df['Country'] + ' ' + df['Year'].astype(str)

    # Melt the DataFrame for count data across different classes
    df_melted_count = pd.melt(df, id_vars=['countryYear'], value_vars=['Livestock', 'Arable', 'Forest', 'Shrubland', 'Grassland'], 
                              var_name='Class', value_name='Count')

    # Melt the DataFrame for percentage data across different classes
    df_melted_percentage = pd.melt(df, id_vars=['countryYear'], value_vars=['Livestock %', 'Arable %', 'Forest %', 'Shrubland %', 'Grassland %'], 
                                   var_name='Class', value_name='Percentage')

    # Adjust 'Class' column to align counts and percentages
    df_melted_percentage['Class'] = df_melted_percentage['Class'].str.replace(' %', '')

    # Merge the melted count and percentage DataFrames
    df_final = pd.merge(df_melted_count, df_melted_percentage, on=['countryYear', 'Class'])
    df_final = df_final[['countryYear', 'Class', 'Count', 'Percentage']]

    return df_final

"""
Global DataFrame definitions and initial data loading and preprocessing
"""

# Load and preprocess LUCAS survey data from specified CSV files
DF1 = pd.read_csv('data/filtered/lucas12.csv')
DF1.drop(['Unnamed: 0'], axis=1, inplace=True)  # Remove an unnecessary column
DF1 = createCountryYearColumn(DF1)  # Apply preprocessing to add 'countryYear' column

DF2 = pd.read_csv('data/filtered/lucasSUM.csv')
DF2.drop(['Unnamed: 0'], axis=1, inplace=True)  # Remove an unnecessary column again
DF2 = createCountryYearColumn(DF2)  # Preprocess second DataFrame

# Load country codes for mapping and analysis purposes
COUNTRY_ID = pd.read_csv('data/raw/country_id/countries_codes_and_coordinates.csv')

# Define a dictionary for mapping class names to specific colors for visual consistency
COLORS = {
    "Livestock": "#1b6ba2",
    "Arable": "#b98c1b",
    "Grassland": "#8fbc8f",
    "Shrubland": "#a0522d",
    "Forest": "#006400",
}

# Create a DataFrame for displaying classification information in a human-readable format
CLASSTABLE = pd.DataFrame({
    'Forest': ['C10 (broadleaves woodland)', 'C20 (coniferous woodlands)', 'C30 (mixed woodlands)'],
    'Shrubland': ['D10 (shrublands with sparse tree cover)', 'D20 (shrublands without tree cover)', ''],
    'Grassland': ['E10 (grasslands with sparse tree/shrub cover)', 'E20 (grasslands without tree/shrub cover)', 'E30 (spontaneously re-vegetated surface)'],
    'Agroforestry': ['Den Herder et al. (2017)', '', '']
})

"""
Markdown text blocks for various sections of the application, providing context and information to the user
"""

# Text blocks defined using Markdown for easy formatting. These blocks provide contextual information
# about the data source, classification source, overview of the LUCAS survey, and details on the project and methodology.

datasource_text = dcc.Markdown(
    """
    [Data source:](https://ec.europa.eu/eurostat/web/lucas/overview)
    Eurostat | LUCAS Point Survey
    """
)

link_text = dcc.Markdown(
    """
    [Classification source:](https://www.sciencedirect.com/science/article/abs/pii/S0167880917301159?via%3Dihub) den Herder et al. (2017). 
        Current extent and stratification of agroforestry in the European Union. Agriculture, Ecosystems & Environment, 241, 121–132. 
    """
)

lucas_text = dcc.Markdown(
    """
    The Land Use/Cover Area frame Survey (LUCAS) is a dataset for understanding land use and land cover across the 
    European Union. Conducted every three years since 2006 by [Eurostat](https://ec.europa.eu/eurostat/web/lucas/information-data), LUCAS provides comprehensive data on various 
    land categories, including agricultural, forest, and urban areas. The survey involves a systematic sampling of 
    points across the EU, offering insights into land use changes and patterns. 


    The work of den Herder et al. ([2017](https://www.sciencedirect.com/science/article/abs/pii/S0167880917301159?via%3Dihub)), utilised this dataset to address the gaps in understanding agroforestry's extent 
    and distribution in Europe. Their methodology focused on identifying agroforestry systems through specific combinations 
    of primary and secondary land covers, as well as land management indicators within the LUCAS data. They classified 
    agroforestry into three main types: arable agroforestry, livestock agroforestry, and high-value tree agroforestry. 
    Their approach enhances the understanding of regional variations in agroforestry practices and informs the classification 
    framework presented here.
    """
)

learn_text = dcc.Markdown(
    """
    Based on the article "Agroforestry as a Sustainable Land Use Option to Reduce Wildfire Risks in 
    European Mediterranean Areas" by Damianidis et al. ([2020](https://link.springer.com/article/10.1007/s10457-020-00482-w)), this project automates the classification 
    of the LUCAS dataset into distinct land categories such as forest, shrubland, grassland, arable, 
    and livestock agroforestry. 
    
    The process was initially undertaken on a Geographic Information System (GIS) software and involved repetitive tasks 
    to filter the five individual countries, is now streamlined using Python. This approach not only simplifies data handling 
    but also integrates a DASH-based dashboard application for interactive visualisation. Users can input any LUCAS dataset 
    from 2009 onwards, and the system then processes and displays the results on the dashboard. This tool 
    offers the flexibility of updating with new datasets and exporting the processed data. 
    
    The project addresses the need for efficient data analysis and visualisation in the context of studying land use 
    and its implications on wildfire risks in European Mediterranean regions, aligning with the findings 
    of Damianidis et al. ([2020](https://link.springer.com/article/10.1007/s10457-020-00482-w)).

    """
)

upload_text = dcc.Markdown(
    """
    To utilise the upload feature of the dashboard, choose two of the available options:

    1) Visit [Eurostat](https://ec.europa.eu/eurostat/web/lucas/information-data) and select data from the year 2009 onwards.
    
    2) For local usage, utilise the preloaded datasets available in the `data/testData` folder.

    """
)

# Define a footer for the web application with additional information or credit
footer = html.Div(
    dcc.Markdown(
        """
        This dashboard was created by Zak Inglebright to showcase Python's ability to solve common problems related to geoinformatics.     
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)

"""
Tables for Displaying Classification Information and Data Upload Components
"""
# Create a DataTable for displaying classification information in a user-friendly format
classificationTable = dash_table.DataTable(
    id="classID",
    data=CLASSTABLE.to_dict('records'),  # Convert DataFrame to dictionary for easy rendering in DataTable
    columns=[{'name': i, 'id': i} for i in CLASSTABLE.columns],  # Define columns based on DataFrame structure
    page_size=20,  # Number of rows to display at once
    style_table={"overflowX": "auto"},  # Enable horizontal scrolling
    style_cell={'textAlign': 'left'},  # Align text to the left for readability
)

# Define a component for users to upload data files
dataUpload = dcc.Upload(
    id='datatable-upload',
    children=html.Div(['Drag and Drop or ', html.A('Select Files')]),  # Text displayed in the upload component
    style={
        'height': '60px', 'lineHeight': '60px',
        'borderWidth': '1px', 'borderStyle': 'dashed',
        'borderRadius': '4px', 'textAlign': 'center', 'margin': '10px'
    },
)

# DataTables for displaying LUCAS survey point data and summary information
PointXY_table = dash_table.DataTable(
    id='XY-upload-container', 
    columns=[{'name': i, 'id': i, } for i in DF1.columns[:]],  # Define columns based on DF1 structure
    page_size=15,
    style_table={"overflowX": "scroll"},  # Enable horizontal scrolling
    style_cell={'textAlign': 'right'},  # Align numbers to the right for readability
    export_format='csv',  # Allow exporting the table as CSV
    export_headers='display',  # Use display names for headers in the exported file
    merge_duplicate_headers=True  # Merge headers if they are duplicates
)

summaryTable = dash_table.DataTable(
    id='datatable-upload-container', 
    columns=[{'name': i, 'id': i, } for i in DF2.columns[:13]],  # Define columns based on DF2 structure
    page_size=15,
    style_table={"overflowX": "scroll"},  # Enable horizontal scrolling
    style_cell={'textAlign': 'right'},  # Align numbers to the right for readability
    export_format='csv',  # Allow exporting the table as CSV
    export_headers='display',  # Use display names for headers in the exported file
    merge_duplicate_headers=True  # Merge headers if they are duplicates
)

"""
Figures for Data Visualization
"""
# Function to create a scatter map for visualizing geographical data points
def makeScatterMap(gdf):
    # Add a conditional column for displaying LC2 data only for 'Arable' class points
    gdf['LC2_conditional'] = gdf.apply(lambda row: row['LC2'] if row['CLASS'] == 'Arable' else '', axis=1)

    # Create a scatter map using Plotly Express, setting latitude and longitude for plotting points
    fig = px.scatter_mapbox(gdf, lat="LAT", lon="LONG",     
                            hover_name="CLASS",  # Define hover information
                            labels={  # Rename labels for better readability
                                'countryYear': 'Country by Year',    
                                'LC1': 'Landcover 1',
                                'LC2_conditional': 'Landcover 2 (Arable)',
                                'LAND_MNGT': 'Land management',
                                'CLASS': 'Class',
                            },
                            hover_data={  # Define additional data to show on hover
                                'countryYear': False, 
                                'LAT': False,
                                'LONG': False,
                                'Country': True,
                                'CLASS': True,
                                'Year': True,
                                'LC1': True,
                                'LC2_conditional': True,
                                'LAND_MNGT': True
                            },
                            color='CLASS',  # Color points by class
                            color_discrete_map=COLORS,  # Use predefined colors for classes
                            mapbox_style="open-street-map",  # Set the map style
                            zoom=3, center={'lat': 48.23610, 'lon': 21.22574})  # Initial map zoom and center

    # Update traces to refine hover template for different data points
    fig.update_traces(
        hovertemplate=
            "<b>%{customdata[4]} </b> <br>"+
            "Landcover 1: %{customdata[6]} <br>"+
            "Landcover 2 (Arable): %{customdata[7]} <br>"+
            "Land management: %{customdata[8]}"
        )
    
    # Ensure layout margins are set to 0 for full width/height utilization
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return(fig)  # Return the constructed figure

# Function to create a stacked bar chart for visualizing data distributions
def make_stack(df):
    # Sort DataFrame by 'countryYear' for consistent ordering
    df = df.sort_values(by = 'countryYear')
    # Create a stacked bar chart using Plotly Express
    fig = px.bar(df, x="countryYear", y='Percentage', color='Class', 
                    color_discrete_map=COLORS,  # Use predefined colors
                    labels={'Percentage':'Percentage %'},  # Label for y-axis
                    hover_data={  # Data to show on hover
                        'Class': False, 
                        'countryYear': False, 
                        'Percentage': ':.2f',  # Format percentage with 2 decimal points
                        'Count': True},
                    title= "Landuse & Landcover Classification Per Country by Year",
        )
    
    # Update the layout to adjust the title font size and position
    fig.update_layout(
        title = dict(font =dict(size = 22), yref='paper')
    )

    # Customize hover template for better data presentation
    fig.update_traces(hovertemplate=
                    'Percentage: %{y:.2f}% <br>' + 
                    'Count: %{customdata[1]} <br>' ) 
                    
    return(fig)  # Return the constructed figure



"""
Creating Tabs and Cards for Navigation and Layout Structure
"""
# Tabs for organizing different sections of the application for a cleaner user interface

# ========== Overview Tab Components
# Creating a card for the 'Learn' tab which will contain an overview of the project
learn_card = dbc.Card(
    [
        dbc.CardHeader("Project Overview"),  # Header/title of the card
        dbc.CardBody(learn_text),  # Body of the card containing the Markdown text about the project overview
        dbc.CardHeader("Upload Instructions"),  # Header/title of the upload instructions
        dbc.CardBody(upload_text), # Body containing information on how to upload data onto dashboard
    ],
    className="mt-4",  # Margin top for styling, adds space above the card for visual separation
)

# ========== Classification Tab Components
# Creating a card for the 'Classification' tab with multiple sections
class_card = dbc.Card(
    [
        dbc.CardHeader("Introduction to LUCAS"),  # Header/title for the introduction section
        dbc.CardBody(lucas_text),  # Body containing the Markdown text about LUCAS
        dbc.CardHeader("The Designation of Classes Within the LUCAS"),  # Header/title for the classification section
        html.Div(classificationTable),  # Div containing a DataTable for classification information
        dbc.CardHeader("Link to Paper"),  # Header/title providing a link to the relevant paper
        dbc.CardBody(link_text),  # Body containing the Markdown with the link to the paper
    ],
    className="mt-4",  # Margin top for styling
)

# ========== Export Tab Components
# Creating a card for the 'Export' tab which will contain data export options and information
export_card = dbc.Card(
    [
        dbc.CardHeader("Classified LUCAS Survey Point Data"),  # Header/title for the section on point data
        dbc.CardBody(PointXY_table),  # Body containing the DataTable for displaying point data
        dbc.CardHeader("Proportion of LUCAS Data Points per Country by Count & Percentages"),  # Header/title for the section on data proportions
        dbc.CardBody(summaryTable),  # Body containing the DataTable for displaying data summaries
    ],
    className="mt-4",  # Margin top for styling
)

# ========== Build tabs
# Creating the tabbed navigation structure by combining the previously defined cards into tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(learn_card, tab_id="tab-1", label="Overview"),  # Tab for the project overview
        dbc.Tab(class_card, tab_id="tab-2", label="LUCAS"),  # Tab for LUCAS classification information
        dbc.Tab(export_card, tab_id="tab-3", label="Export"),  # Tab for exporting data
    ],
    id="tabs",  # Identifier for the Tabs component, used for callback triggers
    active_tab="tab-1",  # Set the default active tab to the project overview
    className="mt-2",  # Margin top for styling, adds space above the tabs for visual separation
)




"""
Main Layout Definition
"""
# The main container that defines the layout and structure of the web application
app.layout = dbc.Container(
    [
       dbc.Row(
            dbc.Col(
                html.H2(
                    "LUCAS Survey Point Classification",  # Title of the application
                    className="text-center bg-primary text-white p-2",  # Styling classes
                ),
            ),
       ),
       # Row for tabs and content
       dbc.Row(
            [
                dbc.Col(tabs, width=12, lg=4, className="mt-4 border"),  # Column for tabs
                dbc.Col(
                    [
                        dataUpload,  # Data upload component

                        # Dropdown for selecting countries/years for visualization
                        dcc.Dropdown(
                            id='my-dropdown',
                            multi=True,  # Allow multiple selections
                            options=[{"label": x, "value": x} for x in sorted(DF1["countryYear"].unique())],
                            value=[]
                        ),
                        dcc.Graph(id="my-map", figure={}),  # Placeholder for the map
                        dcc.Graph(id="stackedGraph", figure={}),  # Placeholder for the stacked bar chart
                        html.Hr(),  # Horizontal rule for visual separation
                        dcc.Store(id='storage-gdf'),  # Store for geodataframe
                        dcc.Store(id='storage-table'),  # Store for table data
                        html.H6(datasource_text, className="my-2"),  # Data source text
                    ],
                    width=12,
                    lg=8,
                    className="pt-4",
                ),
            ],
            className="ms-1",  # Margin start for alignment
        ),
        dbc.Row(dbc.Col(footer)),  # Footer row
    ],
    fluid=True,  # Use the full width of the screen
)

"""
Callbacks for Interactivity
"""

# Callback for processing uploaded data and updating stored data
@app.callback(Output('storage-gdf', 'data'),  # Stores the geodataframe for map visualization
              Output('storage-table', 'data'), # Stores processed table data for visualizations and export
              Input('datatable-upload', 'contents'), # Input from the file upload component
              State('datatable-upload', 'filename')) # State of the filename to parse year and perform processing

def update_storage1(contents, filename):     
    global DF1
    global DF2 

    if contents is None:
        return DF1.to_dict('records'), DF2.to_dict('records') # Return current DFs if no file uploaded
    
    # Parse and process the uploaded data
    df, year = parse_contents(contents, filename)
    lucas_df, lucasTable = processLucasData(df, COUNTRY_ID, year)
    
    lucas_df = createCountryYearColumn(lucas_df) # Add 'countryYear' column
    lucasTable = createCountryYearColumn(lucasTable)

    # Check for duplicates and update the dataframes
    if lucas_df['countryYear'].iloc[0] in DF1['countryYear'].values:  # Prevents duplicates
        raise ValueError("Dataframe Entered Twice, Please Try Another Dataframe")
    else:
        # Concatenate new data with existing dataframes and sort
        DF1 = pd.concat([DF1, lucas_df]).sort_values(by='countryYear')
        DF2 = pd.concat([DF2, lucasTable]).sort_values(by='countryYear')
        
        # Convert updated DataFrames to dictionaries for Dash storage component
        data1 = DF1.to_dict('records')
        data2 = DF2.to_dict('records')
        
        return data1, data2

# Callbacks for updating export tables based on stored data
@app.callback(Output('datatable-upload-container', 'data'),
              Output('XY-upload-container', 'data'),
              Input('storage-table', 'data'),
              Input('storage-gdf', 'data'))

def on_data_set_table(data1, data2):
    if data1 is None or data2 is None:
        raise PreventUpdate  # Prevent callback from firing if data is not set
    # Return the data for DataTables
    return data1, data2

# Callback for updating dropdown options based on available data
@app.callback(
    Output('my-dropdown', 'options'),
    Input('storage-gdf', 'data')
)
def update_dropdown_options(data):
    df = pd.DataFrame.from_records(data)
    # Create and return dropdown options from the 'countryYear' column
    return [{"label": i, "value": i} for i in sorted(df['countryYear'].unique())]

# Callback for updating map based on selected dropdown values
@app.callback(
    Output('my-map', 'figure'),
    [Input('my-dropdown', 'value'),
     Input('storage-gdf', 'data')]
)
def update_map(chosen_value, data):
    if not chosen_value:
        raise PreventUpdate  # Prevent update if no selection is made

    # Filter the data based on selected 'countryYear' values
    df = pd.DataFrame.from_records(data)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONG, df.LAT), crs="EPSG:4326")
    gdf_filtered = gdf[gdf['countryYear'].isin(chosen_value)]

    # Generate and return the map figure
    return makeScatterMap(gdf_filtered)

# Callback for updating the stacked bar chart based on stored table data
@app.callback(Output('stackedGraph', 'figure'),
              Input('storage-table', 'data'))

def update_barplot(data):
    # Reorder and prepare the data for plotting
    df = reorder_df(pd.DataFrame.from_records(data))
    # Generate and return the stacked bar chart
    stack = make_stack(df) 
    return stack

# Main function to run the Dash app if this script is executed as the main program
if __name__ == "__main__":
    app.run_server(debug=True, port = 8797)  # Run the app with debugging enabled
