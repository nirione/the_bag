"""
A program designed to represent a Book of Transactions, made as a fun exercise in relation to supposed crypto trading.

Allows to record transactions, positive number as buy, negative number as sell.
Displays all the data as a table of summed up transactions.
Allows for display of all recorded trades.

Designed to work mainly on Windows, however exceptions are made to make it work on Linux machines

~~~Jakub Swiercz in 2021
"""

import json
import os
import pandas as pd
from datetime import datetime
import urllib.request

pd.set_option("display.precision", 10)

init_now = datetime.now()
init_date = init_now.strftime('%d/%m/%Y %H:%M:%S')

if 'tb_src' not in os.listdir():
    os.makedirs('tb_src')
    os.chdir('tb_src')
    print('Created folder for the files: tb_src !')
else:
    os.chdir('tb_src')

# defining the file paths for json data
book_src = './book_of_sales.json'
assets_src = './assets.json'
coins_src = './coins.json'
prices_src = 'https://api3.binance.com/api/v3/ticker/price'

# checks if the required files exist, creates them if not
if 'book_of_sales.json' not in os.listdir():
    with open('book_of_sales.json', 'x') as f_temp:
        json.dump([], f_temp, indent=2)
    print('Created trade book file: book_of_sales.json !')
if 'assets.json' not in os.listdir():
    with open('assets.json', 'x') as f_temp:
        json.dump([], f_temp, indent=2)
    print('Created asset file: assets.json !')
if 'coins.json' not in os.listdir():
    with open('coins.json', 'x') as f_temp:
        json.dump([], f_temp, indent=2)
    print('Created coin file: coins.json !')


try:
    page = urllib.request.urlopen(prices_src).read().decode()
except Exception as exception:
    print(str(exception) + " reading " + prices_src)
    exit(1)
    
for j in json.loads(page):
    if j['symbol'] == 'BTCUSDT':
        usd_price = float(j['price'])
        
for j in json.loads(page):
    if j['symbol'] == 'BTCUSD':
        USD_price = float(j['price'])

class Sale:     # Sale class to help manage transaction info
    info = ()
    now = datetime.now()
    date = now.strftime('%d/%m/%Y %H:%M:%S')
    symbols = []
    for i in json.loads(page):
        if i['symbol'] not in symbols:
            symbols.append(i['symbol'])

    with open(book_src, 'r') as f:
        temp_trades = json.load(f)

    def __init__(self, symbol, amount, price):
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.value = round(amount*price, 8)
        self.date = str(Sale.date)
        Sale.temp_trades.append(self.__dict__)
        with open(book_src, 'w') as ff:
            json.dump(Sale.temp_trades, ff, indent=2)

    @classmethod
    def from_string(cls, sale_str):
        symbol, amount, price = sale_str.split('/')
        if (symbol + 'btc').upper() not in Sale.symbols:
            print('{0} is an incorrect symbol. '
                  'Check the spelling and make sure the asset can be traded to BTC.'.format(symbol.upper()))
        else:
            print('Successfully recorded a trade of {0} {1} coins.'.format(amount, symbol.upper()))
            return cls(symbol, float(amount), float(price))


class Asset:        # Asset class to help display and store coin info
    display_assets = []
    prices = json.loads(page)

    def __init__(self, symbol, amount, value):
        self.Symbol = symbol.upper()
        self.Amount = amount
        self.Current_Value = amount * self.get_price(self.Symbol)
        self.Purchase_Value = float(value)
        self.Current_Price = self.get_price(self.Symbol)
        self.Balance = self.Current_Value - self.Purchase_Value
        self.Ratio = self.Current_Value / self.Purchase_Value
        if self.__dict__ not in self.display_assets:
            self.display_assets.append(self.__dict__)

    @classmethod
    def from_dict(cls, asset_dict):
        symbol, amount, value, = asset_dict.values()
        return cls(symbol, amount, value)

    @classmethod
    def get_price(cls, symbol):
        for i in Asset.prices:
            if (symbol + 'btc').upper() == i['symbol']:
                return float(i['price'])


def draw_table(data):       # draws table with given data
    cols = []
    content = reversed(data)
    for i in data:
        cols.append(list(i.keys()))
    print(pd.DataFrame(data=content, columns=cols[0]))


def update_assets():    # updates all assets based on the list of trades and list of coins
    with open(book_src, 'r') as f:
        trades_list = json.load(f)

    if len(trades_list) == 0:
        print('No trades recorded to update assets from!')
        with open(assets_src, 'w') as f:
            json.dump([], f, indent=2)
    else:
        asset_list = []

        for i in trades_list:
            with open(coins_src, 'r') as f:
                coins = json.load(f)
                if i['symbol'] not in coins:
                    update_coins(i['symbol'])

        for i in coins:
            total_amount = 0
            total_value = 0
            for d in trades_list:
                if i == d['symbol']:
                    total_amount += d['amount']
                    total_value += d['value']
            asset_list.append({"Symbol": i, "Amount": total_amount, "Purchase Value": total_value})

        with open(assets_src, 'w') as f:
            json.dump(asset_list, f, indent=2)


def update_coins(coin):    # updates the list of coins based on input coin
    with open(coins_src, 'r') as f:
        temp_coins = json.load(f)

    temp_coins.append(coin)

    with open(coins_src, 'w') as f:
        json.dump(temp_coins, f, indent=2)


def view_sales():    # displays all the recorded trades from book_of_sales.json
    with open(book_src, 'r') as ff:
        temp = json.load(ff)
    if len(temp) > 0:
        print('    ______________')
        print('    BOOK OF SALES:')
        print()
        draw_table(temp)
    else:
        print('No sales recorded. Add a new trade record [2]!')


def view_assets():    # displays the existing assets from assets.json without updating the file
    with open(assets_src, 'r') as f:
        temp = json.load(f)
    Asset.display_assets = []
    if len(temp) > 0:
        for i in temp:
            Asset.from_dict(i)
        assets = Asset.display_assets
        sorted_assets = [j for j in sorted(assets, key=lambda v: v['Balance'])]
        top_asset = sorted_assets[len(sorted_assets)-1]
        print('    ________________________________')
        print('    Your current assets: [BTC value]')
        print()
        draw_table(sorted_assets)
        current_total = sum(i['Current_Value'] for i in Asset.display_assets)
        purchase_total = sum(i['Purchase_Value'] for i in Asset.display_assets)
        print()
        print('Current value of all assets: ', round(current_total, 9), 'BTC')
        print('Purchase value of all assets: ', round(purchase_total, 9), 'BTC')        
        print('Current value of assets:', round(float(current_total*usd_price), 2), 'USD')
        print('Current BTC to USD exchange:', usd_price, 'USD = 1 BTC')
        print('Values as of', init_date)
        print()
        if top_asset['Balance'] > 0:
            print('Most profitable asset:', top_asset['Symbol'])
            print('Providing:', '{0:.8f}'.format(top_asset['Balance']), 'BTC profit')
        else:
            print('dude you below !! you losin money !! you in the red... or the black... or whatever the bad one is.')
    else:
        print('No assets recorded. Update assets [3] or add trade records [2]!')


def trade_del():    # removes last added trade
    with open(book_src, 'r') as f:
        temp_trades = json.load(f)

    coins = [i['symbol'] for i in temp_trades]
    coin = temp_trades[len(temp_trades) - 1]['symbol']

    if coins.count(temp_trades[len(temp_trades) - 1]['symbol']) == 1:
        del(coins[coins.index(coin)])

    del(temp_trades[len(temp_trades) - 1])

    with open(book_src, 'w') as f:
        json.dump(temp_trades, f, indent=2)

    new_coins = []
    for i in coins:
        if i not in new_coins:
            new_coins.append(i)

    with open(coins_src, 'w') as f:
        json.dump(new_coins, f, indent=2)


def intro():
    view_assets()
    print()
    print('1 - trade history / '
          '2 - new trade record / '
          '3 - update assets / '
          '4 - delete last trade / '
          'e - exit')

def main():
    os.system('title The_Bag')
    try:
        os.system('cls')
    except:
        os.system('clear')

    while True:
        intro()

        choice = input('What would you want to do?')
        if choice == '1':
            try:
                os.system('cls')
            except:
                os.system('clear')
            view_sales()

        elif choice == '2':
            try:
                os.system('cls')
            except:
                os.system('clear')
            print()
            print('\'e\' or \'exit\' if you want to cancel the operation')
            str_input = input('symbol/amount/price: ')
            if str_input == 'e' or str_input == 'exit':
                print('Cancelled!')
            else:
                Sale.from_string(str_input)
                update_assets()

        elif choice == '3':
            try:
                os.system('cls')
            except:
                os.system('clear')
            update_assets()
            print()
            print('Assets updated!')

        elif choice == '4':
            with open(book_src, 'r') as tempf:
                trades = json.load(tempf)
            if len(trades) == 0:
                print('No trades recorded!')
            else:
                trade = trades[len(trades) - 1]
                print('This will delete the following trade:')
                print(trade)
                confirm = input('Are you sure? [Y/N]')
                if confirm == 'Y' or confirm == 'y':
                    trade_del()
                    update_assets()
                    print('Removed the trade:')
                    print(trade)
                    print('and updated assets!')
                elif confirm == 'N' or confirm == 'n':
                    print('Cancelled. No trade was deleted.')
                else:
                    print('Incorrect input. No trade was deleted.')
        
        elif choice == 'e':
            print()
            print('Goodbye!')
            break

        else:
            try:
                os.system('cls')
            except:
                os.system('clear')
            print()
            print('Incorrect input, use digits (1-4) only!')

if __name__ == "__main__":
    main()
