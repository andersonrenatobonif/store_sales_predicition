import pandas as pd
import requests
import json

from flask import Flask, request, Response


def load_data (store_id):
    
    
    #loading dataset
    df10 = pd.read_csv( 'C:/Users/anderson.bonifacio_i/Desktop/Dados/cds/ds_producao/data/test.csv')
    df_store_raw = pd.read_csv( 'C:/Users/anderson.bonifacio_i/Desktop/Dados/cds/ds_producao/data/store.csv')


    #merge datasets
    df_teste = pd.merge( df10, df_store_raw, how='left', on='Store')

    #choose store for prediction
    df_teste = df_teste[df_teste['Store'] == 22 ]

    #remove close days
    df_teste = df_teste[df_teste['Open'] != 0 ]
    df_teste = df_teste[~df_teste['Open'].isnull()]
    df_teste = df_teste.drop( 'Id', axis =1)



    # Convert dataframe to json

    data = json.dumps(df_teste.to_dict(orient='records'))
    
    return data

def predict(data):


    # API Call
    url = 'https://rossmann-predicition.onrender.com/rossmann/predict'
    header = {'Content-type': 'application/json' } 
    data = data

    r = requests.post( url, data=data, headers=header )
    print( 'Status Code {}'.format( r.status_code ) )

    d1 = pd.DataFrame( r.json(), columns=r.json()[0].keys())
    
    return d1



    # d2 = d1[['store', 'predictions']].groupby('store').sum().reset_index()

    # for i in range( len( d2 )):
    #     print( 'Store number {} will sell  ${:,.2f} in the next 6 weeks'.format(d2.loc[i, 'store'], d2.loc[i, 'predictions']))