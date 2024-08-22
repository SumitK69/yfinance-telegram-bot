import os
from dotenv import load_dotenv
import yfinance as yf
import matplotlib.pyplot as plt

import pandas as pd     


import telebot

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

print("BOT_TOKEN",BOT_TOKEN)

bot = telebot.TeleBot(BOT_TOKEN)

data = {"scrip1":None,"scrip2":None,"scrip1_ratio":None,"scrip2_ratio":None}


#! for testing purpose
# data = {"scrip1":"tcnsbrands.ns","scrip2":"tcs.ns","scrip1_ratio":6,"scrip2_ratio":2}

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message,"Howdy, how  doing?")
    
 
@bot.message_handler(commands=['scrip1'])
def scrip1_handler(message):
    user_id = message.from_user.id
    print(user_id)
    command_text = message.text
    parts = command_text.split(' ', 1)
    if len(parts) > 1:
        data['scrip1'] = parts[1]
        bot.reply_to(message, f"You entered: {data['scrip1'].upper()}")
    else:
        bot.reply_to(message, "You didn't enter the symbol after the command!")




@bot.message_handler(commands=['scrip2'])
def scrip2_handler(message):
    command_text = message.text
    parts = command_text.split(' ', 1)
    if len(parts) > 1:
        data['scrip2'] = parts[1] 
        bot.reply_to(message, f"You entered: {data['scrip2'].upper()}")
    else:
        bot.reply_to(message, "You didn't enter the symbol after the command!")



@bot.message_handler(commands=['scrip1_ratio'])
def scrip1_ratio_handler(message):
    command_text = message.text
    parts = command_text.split(' ', 1)
    if len(parts) > 1:
        data['scrip1_ratio'] = parts[1] 
        bot.reply_to(message, f"You entered: {data['scrip1_ratio']}")
    else:
        bot.reply_to(message, "You didn't enter the ratio value after the command!")

    

@bot.message_handler(commands=['scrip2_ratio'])
def scrip2_ratio_handler(message):
    command_text = message.text
    parts = command_text.split(' ', 1)
    if len(parts) > 1:
        data['scrip2_ratio'] = parts[1] 
        bot.reply_to(message, f"You entered: {data['scrip2_ratio']}")
    else:
        bot.reply_to(message, "You didn't enter the ratio value after the command!")

def has_none_value(d):
  return any(value is None for value in d.values())
    
@bot.message_handler(commands=['get_chart'])
def get_chart(message):
    if  has_none_value(data):
        bot.reply_to(message,f"Few values must be missing scrip1_ratio: {data['scrip1_ratio']}, scrip1: {data['scrip1']}, scrip2_ratio: {data['scrip2_ratio']}, scrip2: {data['scrip2']}")
        
    else:
        ticker_symbol1 = data['scrip1'].upper()
        ticker1 = yf.Ticker(ticker_symbol1)
        history_data_scrip1 = ticker1.history(period='1d', interval='1m')
        
        history_data_scrip1[f'Normalized {data['scrip1']}'] = history_data_scrip1['Close'] / int(data['scrip1_ratio'])
        
        print("history_data_scrip1",history_data_scrip1)
        history_data_scrip1.index = history_data_scrip1.index.tz_localize(None)
        
        # history_data_scrip1.to_csv('history_data_scrip1.csv')

        
        ticker_symbol2 = data['scrip2'].upper()
        ticker2 = yf.Ticker(ticker_symbol2)
        history_data_scrip2 = ticker2.history(period='1d', interval='1m')
     
        history_data_scrip2[f'Normalized {data['scrip2']}'] = history_data_scrip2['Close'] / int(data['scrip2_ratio'])
        
        print("history_data_scrip2",history_data_scrip2)
        history_data_scrip2.index = history_data_scrip2.index.tz_localize(None)

        # history_data_scrip2.to_csv('history_data_scrip2.csv')
        
        
        
        if len(history_data_scrip1) < len(history_data_scrip2):
            combined_data = pd.DataFrame({
                'Date': history_data_scrip1.index,
                f'Normalized {data["scrip1"]}': history_data_scrip1[f'Normalized {data["scrip1"]}'],
                f'Normalized {data["scrip2"]}': history_data_scrip2[f'Normalized {data["scrip2"]}'].reindex(history_data_scrip1.index)
            }).dropna().set_index('Date')
        else:
            combined_data = pd.DataFrame({
                'Date': history_data_scrip2.index,
                f'Normalized {data["scrip1"]}': history_data_scrip1[f'Normalized {data["scrip1"]}'].reindex(history_data_scrip2.index),
                f'Normalized {data["scrip2"]}': history_data_scrip2[f'Normalized {data["scrip2"]}']
            }).dropna().set_index('Date')
        
      
        combined_data['Percent_Diff'] = 100 * (combined_data[f'Normalized {data["scrip2"]}'] - combined_data[f'Normalized {data["scrip1"]}']) / combined_data[f'Normalized {data["scrip1"]}']
        
        # combined_data.to_csv("combined_data.csv")
        
        
        
        combined_data.index = combined_data.index.tz_localize(None)
        plt.figure(figsize=(14, 7))
        plt.plot(combined_data.index, combined_data[f'Normalized {data['scrip1']}'], label=f'{data['scrip1'].upper()}')
        plt.plot(combined_data.index, combined_data[f'Normalized {data['scrip2']}'], label=f'{data['scrip2'].upper()}')
        
        plt.xlabel('Date')
        plt.ylabel('Normalized Price')
        plt.title('Stock Prices and Percentage Difference')
        plt.legend()
        # plt.legend(loc='upper left')
        plt.grid(True)
        
        plt.twinx()
        plt.plot(combined_data.index, combined_data['Percent_Diff'],color="red",linestyle = "--",label="Percentage Difference")
        plt.ylabel('Percentage Difference (%)')
        plt.legend(loc='upper right')
        plt.savefig('plot.png')
        # plt.show()

        with open('plot.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        os.remove('plot.png')


        # print("history_data",history_data)
  
        bot.reply_to(message,f"scrip1_ratio: {data['scrip1_ratio']}, scrip1: {data['scrip1']}, scrip2_ratio: {data['scrip2_ratio']}, scrip2: {data['scrip2']}")

@bot.message_handler(commands=['reset'])
def reset(message):
    for key in data:
        data[key] = None
    bot.reply_to(message,f" Values has been reset scrip1_ratio: {data['scrip1_ratio']}, scrip1: {data['scrip1']}, scrip2_ratio: {data['scrip2_ratio']}, scrip2: {data['scrip2']}")
    


    
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)
    
    
    


bot.infinity_polling()
