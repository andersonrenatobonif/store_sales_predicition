import pandas as pd
import requests
import json

from flask import Flask, request, Response

# constants

token = '5719287128:AAEl2Wkp7khFA9kr1kiQY77K5B6uVihxshk'

#Info about the bot
#https://api.telegram.org/bot5719287128:AAEl2Wkp7khFA9kr1kiQY77K5B6uVihxshk/getMe

# get Updates
#https://api.telegram.org/bot5719287128:AAEl2Wkp7khFA9kr1kiQY77K5B6uVihxshk/getUpdates

# Webrook
#https://api.telegram.org/bot5719287128:AAEl2Wkp7khFA9kr1kiQY77K5B6uVihxshk/setWebhook?url=https://712f-2804-431-c7e3-b4d6-6ccc-3705-73e1-5c73.ngrok-free.app

# Send Message
#https://api.telegram.org/bot5719287128:AAEl2Wkp7khFA9kr1kiQY77K5B6uVihxshk/sendMessage?chat_id=1059094717&text=Oi Anderson


def send_message(chat_id, text):
    
    url = 'https://api.telegram.org/bot{}/'.format( token )
    url = url + 'sendMessage?chat_id={}'.format( chat_id )
    
    r = requests.post( url, json={'text': text})
    print( 'Status Code {}'.format(r.status_code))
    
    return None




def load_data (store_id):
    
    
    #loading dataset
    df10 = pd.read_csv( 'C:/Users/anderson.bonifacio_i/Desktop/Dados/cds/ds_producao/data/test.csv')
    df_store_raw = pd.read_csv( 'C:/Users/anderson.bonifacio_i/Desktop/Dados/cds/ds_producao/data/store.csv')


    #merge datasets
    df_teste = pd.merge( df10, df_store_raw, how='left', on='Store')

    #choose store for prediction
    df_teste = df_teste[df_teste['Store'] == store_id ]
    
    if not df_teste.empty:

        #remove close days
        df_teste = df_teste[df_teste['Open'] != 0 ]
        df_teste = df_teste[~df_teste['Open'].isnull()]
        df_teste = df_teste.drop( 'Id', axis =1)

        # Convert dataframe to json
        data = json.dumps(df_teste.to_dict(orient='records'))
        
    else:
        data = 'error'
    
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

    

def parse_message( message ):
    
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']
    
    store_id = store_id.replace('/', '')
    
    try:
        store_id = int(store_id)
        
    except ValueError:
        store_id = 'error'
    
    return chat_id, store_id
 
# API initialize   
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method=='POST':
        message = request.get_json()
        chat_id, store_id = parse_message(message)
        
        if store_id != 'error':
            #loading data
            data = load_data(store_id)
            
            if data != 'error':
            
                #predict
                d1 = predict(data)
                
                #calculate
                d2 = d1[['store', 'predictions']].groupby('store').sum().reset_index()

                #send message
                msg =  ('Store number {} will sell  ${:,.2f} in the next 6 weeks'.
                        format(d2['store'].values[0], d2['predictions'].values[0]))
                
                send_message(chat_id, msg)
                
                return Response('Ok', status=200)
                
            else:
                send_message(chat_id, 'Número de loja inválido')
                return Response('Ok', status=200)
            
        else:
            send_message(chat_id, 'Store ID is Wrong')
            return Response( 'OK', status=200)
        
    else:
        return '<h1> Rossmann Telegram Bot </h1>'

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=5000 ) 