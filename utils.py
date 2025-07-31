import os
import pandas as pd


# Functie voor het laden van de .csv files waarin alle data zich bevindt
def load_csv_file(file_path):
    return pd.read_csv(file_path)

# Functie voor het laden van de .parquet files waarin alle data zich bevindt
def load_parquet_file(file_path):
    return pd.read_parquet(file_path)


# Functie voor het opschonen van .csv data
def clean_date(dataframe):
    
    columns_to_convert = dataframe.columns.difference(['Time'])
    
    for column in columns_to_convert:
        dataframe[column] = pd.to_numeric(dataframe[column], errors = 'coerce')
        dataframe[column] = dataframe[column].ffill()
        dataframe[column] = dataframe[column].astype('float16')
        
    dataframe = dataframe.iloc[::50]
    
    dataframe['Time'] = pd.to_datetime(dataframe['Time'], errors = 'coerce')
    dataframe.set_index('Time', inplace = True)
    

# Functie voor het omzetten van opgeschoonde .csv file naar .parquet file
def csv_to_parquet(dataframe):
    dataframe.to_parquet(index = True)


# Functie voor het checken of de folder parquet files bevat
def get_parquet_files(folder_path):
    if not folder_path or not os.path.isdir(folder_path):
        return []
    return [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".parquet") and os.path.isfile(os.path.join(folder_path, f))
    ]

# Functie voor het checken of de folder csv files bevat
def get_csv_files(folder_path):
    """Get all CSV files from a given folder path"""
    if not folder_path or not os.path.isdir(folder_path):
        return []
    return [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".csv") and os.path.isfile(os.path.join(folder_path, f))
    ]