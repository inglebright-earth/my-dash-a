
"""
==========================================================================
Standardisation functions
"""

def standardiseColumn(rawDF, country):
    """
    Standardises column names within a DataFrame by renaming specific columns and removing prefixes.
    Renames 'SURVEY_GRAZING' to 'LAND_MNGT' and removes 'SURVEY_' and 'POINT_' prefixes.
    Also, standardises country data, including replacing 'GB' with 'UK' and renaming the United Kingdom.
    """
    import pandas as pd  # Importing the pandas library to manipulate dataframes

    # Standardise country DataFrame columns and values
    country.rename(columns={'alpha-2': "ISO2", 'name': 'Country'}, inplace=True)  # Renaming columns for consistency
    country['ISO2'] = country['ISO2'].replace('GB', 'UK')  # Replacing 'GB' with 'UK' in the ISO2 column
    country['Country'] = country['Country'].replace('United Kingdom of Great Britain and Northern Ireland', 'Great Britain')  # Renaming the country for brevity

    # Standardise rawDF column names and merge with country information based on conditions
    if 'GRAZING' in rawDF.columns:  # If 'GRAZING' column exists, rename it and the 'NUTS0' column
        rawDF.rename(columns={'GRAZING': 'LAND_MNGT', "NUTS0": "ISO2"}, inplace=True)
    elif 'SURVEY_GRAZING' in rawDF.columns:  # If 'SURVEY_GRAZING' column exists, rename it
        rawDF.rename(columns={'SURVEY_GRAZING': 'LAND_MNGT'}, inplace=True)
        # Remove specific prefixes from all columns
        for col in rawDF.columns:
            if col.startswith('SURVEY_'):
                rawDF.rename(columns={col: col.replace('SURVEY_', '')}, inplace=True)  # Removing 'SURVEY_' prefix
            elif col.startswith('POINT_'):
                rawDF.rename(columns={col: col.replace('POINT_', '')}, inplace=True)  # Removing 'POINT_' prefix
        rawDF.rename(columns={"NUTS0": "ISO2"}, inplace=True)  # Renaming 'NUTS0' to 'ISO2'
    elif 'TH_LAT' in rawDF.columns:  # If latitude and longitude columns exist with 'TH_' prefix, rename them
        rawDF.rename(columns={'TH_LAT': 'LAT', 'TH_LONG': 'LONG', "NUTS0": "ISO2"}, inplace=True)

    # Merge DataFrame with country information and return
    df_merged = rawDF.merge(country[['ISO2', 'Country']], on='ISO2', how='left')  # Merging with country info
    return df_merged


"""
==========================================================================
Classification functions 
"""

def extractCountryName(rawDF):
    """
    Extracts the first country name from the specified column in a DataFrame.
    """
    countryName = rawDF['Country'].values[0]  # Extracting the first country name from the 'Country' column
    return countryName

def generateClassIDs():
    """
    Generates and returns lists of Class IDs for various land cover categories: 
    livestock, arable, forest, shrubland, and grassland.
    """
    # Define Class IDs for different land use categories
    livestockClassIDs = ['B' + str(b) for b in range(71, 85)] + ['C' + str(c) for c in range(10, 34)] + ['D10', 'E10']  # Generating IDs for livestock
    arable_LC1 = livestockClassIDs[:-2] + ['D10']  # Shares some IDs with livestock, excludes the last two
    arable_LC2 = ['B' + str(i) for i in range(11, 55)]  # Generating IDs for arable land
    forest_LC1 = ['C10', 'C21', 'C22', 'C23', 'C31', 'C32', 'C33']  # Generating IDs for forest land
    shrubland_LC1 = ['D10', 'D20']  # Generating IDs for shrubland
    grassland_LC1 = ['E10', 'E20', 'E30']  # Generating IDs for grassland

    arableClassIDs = [arable_LC1, arable_LC2]  # Combine both lists for arable agroforestry
    forestClassIDs = [forest_LC1,arable_LC2]
    shrublandClassIDs = [shrubland_LC1, arable_LC2]
    grasslandClassIDs = [grassland_LC1, arable_LC2] 

    return livestockClassIDs, arableClassIDs, forestClassIDs, shrublandClassIDs, grasslandClassIDs

def filterNonAgroforestryClasses(rawDF, arable_LC2, landMngt = 2.0):
    """
    Filters and returns a DataFrame for classes not considered agroforestry, based on the absence of specified arable Class IDs.
    """
    modifiedDF = rawDF.copy()  # Creating a copy of the input DataFrame to modify
    if landMngt:
        # Create a boolean mask for non-agroforestry conditions
        non_agro_mask = modifiedDF.loc[(~modifiedDF['LC2'].isin(arable_LC2)) & (modifiedDF['LAND_MNGT'] == landMngt)]
        
        # Apply the mask to the DataFrame to filter relevant entries
        nonAgroDF = modifiedDF[non_agro_mask].copy()
    
    return nonAgroDF

def filterClasses(rawDF, classIDs, className, landMngt=2.0, option=0):
    """
    Generic filtering function to classify and return LULC classes into DataFrame, based on booleon indexing
    """
    columnName = ['LAT', 'LONG', 'LC1', 'LC2', 'LAND_MNGT']  # Defining the column names to be used in the filtered DataFrame

     # Filter Agroforestry classes
    if option == 0: 
        if landMngt == 2.0:  # Arable agroforestry
            condition = (rawDF['LC1'].isin(classIDs[0])) & (rawDF['LC2'].isin(classIDs[1])) & (rawDF['LAND_MNGT'] == landMngt)
        else:            #  livestock agroforestry
            condition = (rawDF['LC1'].isin(classIDs)) & (rawDF['LAND_MNGT'] == landMngt)
    # Filters Non-Agroforestry classes
    else:  
        condition = (rawDF['LC1'].isin(classIDs[0])) & (~rawDF['LC2'].isin(classIDs[1])) & (rawDF['LAND_MNGT'] == landMngt)

    filteredDF = rawDF.loc[condition, columnName].copy()  # Filtering the DataFrame based on the condition
    filteredDF['CLASS'] = className  # Assigning a class name to the filtered entries

    return filteredDF

def filterLandUseCoverClasses(rawDF, year):
    """
    Filters and merges DataFrames for five land use and cover classes: livestock, arable, forest, 
    shrubland, and grassland. Appends them together with additional metadata such as year and country.
    """
    import pandas as pd  # Importing pandas for DataFrame manipulation
    countryName = extractCountryName(rawDF)  # Extracting the country name

    # Generate Class IDs for filtering
    livestockClassIDs, arableClassIDs, forestClassIDs, shrublandClassIDs, grasslandClassIDs = generateClassIDs()

    # filter agroforestry classes
    livestockDF = filterClasses(rawDF, livestockClassIDs, 'Livestock', landMngt=1.0, option = 0)
    arableDF = filterClasses(rawDF, arableClassIDs, 'Arable', landMngt=2.0, option = 0)
    
    # filter non agroforestry classes
    # nonAgroforestryDF = filterNonAgroforestryClasses(rawDF, arable_LC2, landMngt=2.0)
    forestDF = filterClasses(rawDF, forestClassIDs, 'Forest', option = 1)
    shrublandDF = filterClasses(rawDF, shrublandClassIDs, 'Shrubland', option = 1)
    grasslandDF = filterClasses(rawDF, grasslandClassIDs, 'Grassland', option = 1)

    # Merge all filtered DataFrames
    combinedDF  = pd.concat([livestockDF, arableDF, forestDF, shrublandDF, grasslandDF])  # Concatenating the filtered DataFrames
    # Add additional metadata
    combinedDF .insert(1, 'Year', year)  # Inserting the year column
    combinedDF ['Country'] = countryName  # Assigning the country name to all entries

    return combinedDF

"""
==========================================================================
Create table functions 
"""

def createBinaryClassColumn(df, className):
    """
    Creates a binary column in the DataFrame to indicate the presence (1) or absence (0) of the specified class name.
    """
    binaryDF = df.copy()  # Creating a copy of the DataFrame to modify
    binaryDF[className] = [1 if x == className else 0 for x in binaryDF['CLASS']]  # Generating a binary column for the class
    return binaryDF

def createFrequencyTable(rawDF):
    """
    Computes a frequency table from a DataFrame, summarising the total count of each class per country.
    """
    frequencyDF = rawDF.groupby('Country')[['Livestock', 'Arable', 'Forest', 'Shrubland', 'Grassland']].sum().astype(int).reset_index()  # Grouping by country and summing up the counts
    return frequencyDF

def createPercentageTable(frequencyDF):
    """
    Converts a frequency table into a percentage table, showing the distribution of each class per country as percentages.
    """
    percentageDF = frequencyDF.set_index('Country')  # Setting 'Country' as the index
    percentageDF = round(percentageDF.div(percentageDF.sum(axis=1), axis=0).fillna(0) * 100, 1)  # Calculating percentages
    percentageDF = percentageDF.reset_index()  # Resetting the index to turn 'Country' back into a column
    percentageDF = percentageDF.rename(columns=lambda x: f'{x} %' if x != 'Country' else x)  # Renaming columns to indicate percentages

    return percentageDF

def createSummarisedTable(df, year):
    """
    Generates a summarised table for land use and cover data, including both count and percentage of classes 
    per country, along with the year.
    """
    import pandas as pd  # Importing pandas for DataFrame manipulation
    classIDs = ['Livestock', 'Arable', 'Forest', 'Shrubland', 'Grassland']
    modifiedDF = df.copy()  # Creating a copy of the DataFrame to modify

    # Create binary columns for each class
    for classID in classIDs:
        modifiedDF = createBinaryClassColumn(modifiedDF, classID)  # Creating binary columns for each class

    # Create separate tables
    frequencyDF = createFrequencyTable(modifiedDF)  # Creating a frequency table
    percentageDF = createPercentageTable(frequencyDF)  # Creating a percentage table

    # Merge frequency and percentage tables
    summarisedDF = pd.merge(frequencyDF, percentageDF, on='Country', suffixes=('', ' %'))  # Merging the tables
    summarisedDF.insert(1, 'Year', year)  # Inserting the year column
    summarisedDF['Total'] = summarisedDF[['Livestock', 'Arable', 'Forest', 'Shrubland', 'Grassland']].sum(axis=1)  # Calculating the total counts

    return summarisedDF

"""
==========================================================================
Processing LUCAS data function 
"""

def processLucasData(rawData, countryID, year):
    """
    Main function to process LUCAS data: standardises columns, filters by land use and cover classes, 
    and generates summarised tables.
    """
    modifiedDF = rawData.copy()  # Creating a copy of the raw data
    correctDF = standardiseColumn(modifiedDF, countryID)  # Standardising column names and merging country information
    lucasData = filterLandUseCoverClasses(correctDF, year)  # Filtering by land use and cover classes
    lucasTable = createSummarisedTable(lucasData, year)  # Generating a summarised table

    return lucasData, lucasTable
