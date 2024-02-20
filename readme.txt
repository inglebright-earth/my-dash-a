#####------------ OVERVIEW OF DASHBOARD ------------#####

This project leverages Python to automate the classification of LUCAS datasets into categories like forest, shrubland, and agroforestry, streamlining the previously GIS-based process. It features a DASH dashboard for interactive visualisation, allowing users to input LUCAS datasets from 2009 onwards for analysis and visualisation. The tool supports updates with new datasets and data export, enhancing efficiency in studying EU agroforestry patterns.

For a better understanding of my dashboard and its solutions to the automation challenges in geoinformatics, please find the report located in the `SRC` folder.


#####------------ FOR ONLINE USE OF DASHBOARD ------------#####
Due to the limited processing capabilities of the server, you may experience slower response times and restricted functionality while using the dashboard online. For a basic overview and quick access, the online version is suitable. However, for optimal performance and full access to all features, I recommend running the dashboard locally by following the instructions provided below.


#####------------ INSTRUCTIONS FOR LOCAL USE OF DASHBOARD ------------#####

### Download Instruction 
1. Navigate to the `my-dash-app` repository.
2. Click on the `<> Code` button and select **Download ZIP** to download the repository to your local machine.
3. Extract the ZIP file.
4. For local use, only utilise the files within the `src` folder.

### File Order:
1. dependencies.txt
2. `initial-dataframe.py`   # Optional: Use if processing initial data for app.py is required.
3. `app.py`

### 1. `dependencies.txt`:
- Go into your terminal and type: pip install -r dependencies.txt

### 2. `initial-dataframe.py`:
- Processes the initial data for the five countries to be displayed in `app.py`.

### 3. `app.py`:
- Preloaded test data can be found under the directory (data/testData).
    -> This data has been sourced directly from the Eurostat website.
    -> To use custom datasets, visit https://ec.europa.eu/eurostat/web/lucas/overview. 
       Note: Only datasets from 2009 onwards are compatible.

- Upon executing 'run', the console will display: "Dash is running on http://127.0.0.1:8050/"
- Access the dashboard application by clicking the provided link.


Note: In case of encountering multiple errors within the dashboard application after accessing the link, a simple page refresh should resolve the issue.