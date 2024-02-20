# Importing the pandas library as pd for data manipulation and analysis
import pandas as pd
# Importing the processLucasData function from the functions module for processing data
from functions import processLucasData

# Loading a dataset of country IDs from a CSV file into a pandas DataFrame
countryID = pd.read_csv('data/raw/country_id/countries_codes_and_coordinates.csv') 

# Defining a list of filenames, each representing a LUCAS dataset for a specific country and year
list_of_files = ['ES_2012_20200213', 'PT_2012_20200213', 'IT_2012_20200213', 
                 'FR_2012_20200213', 'EL_2012_20200213', 'CY_2012_20200213']

# Initializing an empty list to store DataFrames loaded from each file in the list_of_files
df_list = [] 
# Iterating over the list_of_files to load each file as a DataFrame
for i in range(len(list_of_files)):  
    # Reading a CSV file into a DataFrame, specifying low_memory=False to process files with mixed data types more efficiently
    temp_df = pd.read_csv("data/raw/lucas12_raw/"+list_of_files[i]+".csv", low_memory=False)
    # Appending the loaded DataFrame to the df_list
    df_list.append(temp_df)


# Initializing two empty lists to store processed LUCAS data
lucasClassList = []
lucasTableList = []
# Iterating over each DataFrame in df_list to process LUCAS data
for countrydf in df_list:
  # Processing the LUCAS data for a country using the processLucasData function, which returns two DataFrames
  lucas_df, lucasTable = processLucasData(countrydf, countryID, 2012)
  # Appending the processed LUCAS data DataFrame to lucasClassList
  lucasClassList.append(lucas_df)
  # Appending the summary table DataFrame to lucasTableList
  lucasTableList.append(lucasTable)


# Concatenating all DataFrames in lucasClassList into a single DataFrame and converting it to a DataFrame again
lucas12DF = pd.DataFrame(pd.concat(lucasClassList,ignore_index=True))
# Concatenating all DataFrames in lucasTableList into a single DataFrame and converting it to a DataFrame again for summarisation
summarisedDF = pd.DataFrame(pd.concat(lucasTableList,ignore_index=True))


# Saving the concatenated and processed LUCAS data DataFrame to a CSV file
lucas12DF.to_csv('data/filtered/lucas12.csv')
# Saving the concatenated summary table DataFrame to a CSV file
summarisedDF.to_csv('data/filtered/lucasSUM.csv')
# Printing a message to indicate the completion of data processing
print('finished processing')
