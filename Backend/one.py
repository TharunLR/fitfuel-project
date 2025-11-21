import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

def scaling(dataframe):
    print("LO")
    scaler=StandardScaler()
    print("LI")
    # Select only the numeric columns for scaling
    numeric_cols = dataframe.select_dtypes(include=np.number).columns.tolist()
    # Assuming the numeric columns for scaling are from 'Calories' to 'ProteinContent'
    # This is safer than hardcoding indices
    nutrition_cols = ['Calories','FatContent','SaturatedFatContent','CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent']
    
    # Ensure all nutrition columns are present
    cols_to_scale = [col for col in nutrition_cols if col in dataframe.columns]
    
    prep_data=scaler.fit_transform(dataframe[cols_to_scale].to_numpy())
    print("_")
    return prep_data,scaler,cols_to_scale

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine',algorithm='brute')
    print("+")
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh,scaler,params):
    print(")")
    transformer = FunctionTransformer(neigh.kneighbors,kw_args=params)
    pipeline=Pipeline([('std_scaler',scaler),('NN',transformer)])
    return pipeline

def extract_data(dataframe,ingredients):
    print("(")
    columns=['RecipeId','Name','CookTime','PrepTime','TotalTime','RecipeIngredientParts','Calories','FatContent','SaturatedFatContent','CholesterolContent','SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent','RecipeInstructions']
    # Ensure the dataframe only has the specified columns
    dataframe=dataframe[columns]
    
    extracted_data=dataframe.copy()
    
    # The strict filtering is removed to allow more flexible recommendations.
    # The model will now find the closest nutritional match without pre-filtering based on arbitrary max values.
    
    # Filter by ingredients if provided
    if ingredients:
        extracted_data=extract_ingredient_filtered_data(extracted_data,ingredients)
        
    return extracted_data
    
def extract_ingredient_filtered_data(dataframe,ingredients):
    print("*")
    extracted_data=dataframe.copy()
    # Handle case where ingredients might be an empty list
    if ingredients:
        try:
            regex_string=''.join(map(lambda x:f'(?=.*{x})',ingredients))
            extracted_data=extracted_data[extracted_data['RecipeIngredientParts'].str.contains(regex_string,regex=True,flags=re.IGNORECASE)]
        except re.error as e:
            print(f"Regex error: {e}")
            # Return the dataframe without ingredient filtering if regex fails
            return extracted_data
    return extracted_data

def apply_pipeline(pipeline,_input,extracted_data):
    print("&")
    _input=np.array(_input).reshape(1,-1)
    # The transform is now on the input, which should match the columns used for fitting the scaler
    indices = pipeline.transform(_input)[0]
    return extracted_data.iloc[indices]

def recommend(dataframe,_input,ingredients=[],params={'n_neighbors':5,'return_distance':False}):
        print("^")
        extracted_data=extract_data(dataframe,ingredients)
        
        # Check if there are enough recipes after filtering
        if extracted_data.shape[0] >= params['n_neighbors']:
            prep_data,scaler,cols_to_scale=scaling(extracted_data)
            neigh=nn_predictor(prep_data)
            
            # The pipeline is now simpler as it doesn't need the scaler for transformation of the dataset itself
            transformer = FunctionTransformer(neigh.kneighbors, kw_args=params)
            pipeline = Pipeline([('NN', transformer)])
            
            # Scale the user input before prediction
            _input_scaled = scaler.transform(np.array(_input).reshape(1, -1))
            
            indices = pipeline.transform(_input_scaled)[0]
            return extracted_data.iloc[indices]
        
        else:
            print(f"Not enough recipes found to recommend. Found {extracted_data.shape[0]}, need at least {params['n_neighbors']}.")
            return None

def extract_quoted_strings(s):
    # Handles cases where the string might not be in the expected format
    if isinstance(s, str):
        strings = re.findall(r'"([^"]*)"', s)
        return strings
    return []

def output_recommended_recipes(dataframe):
    if dataframe is not None and not dataframe.empty:
        output=dataframe.copy()
        output=output.to_dict("records")
        for recipe in output:
            recipe['RecipeIngredientParts']=extract_quoted_strings(recipe['RecipeIngredientParts'])
            recipe['RecipeInstructions']=extract_quoted_strings(recipe['RecipeInstructions'])
        return output
    return [] # Return an empty list if no recipes are recommended

#l=[100,12,2,20,120,50,6,5,40]
#recommendation_dataframe=recommend(dataset,l)
#output=output_recommended_recipes(recommendation_dataframe)
"""lt=[]
for i in output:
    lt.append(i['Name'])"""
#print(output)
