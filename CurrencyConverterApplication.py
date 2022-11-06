import re
import subprocess,sys

import requests
import json,os
import pandas as pd
from tkinter import *
import tkinter as tk
from tkinter import ttk

class CurrencyConverter():
    def __init__(self,url):
        self.data= requests.get(url).json()
        self.currencies = self.data['rates']

        baseTermFile = os.path.join(os.getcwd(), 'Currency_Pairs_rates.JSON')
        f = open(baseTermFile)
        data = json.load(f)
        self.base_usd = data['USD']
        self.base_eur = data['EUR']

        matrixFile = os.path.join(os.getcwd(), 'Cross-via_matrix.csv')
        self.m = pd.read_csv(matrixFile)
        self.m = self.m.set_index('Unnamed: 0')

    def lookup_matrix(self,currency_from, currency_to, currency_amt):

        val = self.m.loc[currency_from][currency_to]
        pair1_amt = self.convert(currency_from, val, currency_amt)
        pair2_amt = self.convert(val, currency_to, pair1_amt)
        return (pair2_amt)

    def convert(self,currency_from, currency_to, currecny_amt):

        if currency_from == currency_to:
            return (currecny_amt)

        elif (currency_from == 'USD' or currency_to == 'USD'):
            if (currency_from == 'USD' and currency_to in self.base_usd):
                return (self.base_usd[currency_to] * currecny_amt)
            elif (currency_to == 'USD' and currency_from in self.base_usd):
                return ((1 / self.base_usd[currency_from]) * currecny_amt)
            else:
                return (self.lookup_matrix(currency_from, currency_to, currecny_amt))

        elif (currency_from == 'EUR' or currency_to == 'EUR'):
            if (currency_from == 'EUR' and currency_to in self.base_eur):
                return (self.base_eur[currency_to] * currecny_amt)
            elif (currency_to == 'EUR' and currency_from in self.base_eur):
                return ((1 / self.base_eur[currency_from]) * currecny_amt)
            else:
                return (self.lookup_matrix(currency_from, currency_to, currecny_amt))

        else:
            return (self.lookup_matrix(currency_from, currency_to, currecny_amt))

class CurrencyConverterUI(tk.Tk):
    def __init__(self, converter):
        tk.Tk.__init__(self)
        self.title = 'Currency Converter'
        self.currency_converter = converter

        # self.configure(background = 'blue')
        self.geometry("500x200")

        # Label
        self.intro_label = Label(self, text='Welcome to FX Calculator', fg='blue', relief=tk.RAISED,
                             borderwidth=3)
        self.intro_label.config(font=('Courier', 15, 'bold'))
        self.date_label = Label(self,
                            text='Select a currency from and to from dropdown and enter the amount to convert.',relief=tk.GROOVE,
                              font=('Helvetica', 8, 'bold'))
        self.intro_label.place(x=10, y=5)
        self.date_label.place(x=10, y=50)

        # Entry box
        valid = (self.register(self.restrictNumberOnly), '%d', '%P')
        # restricNumberOnly function will restrict thes user to enter invavalid number in Amount field. We will define it later in code
        amt = tk.StringVar()
        amt.set("1")

        self.amount_field = Entry(self, textvariable=amt, bd=3, relief=tk.RIDGE, justify=tk.CENTER, validate='key', validatecommand=valid)
        self.converted_amount_field_label = Label(self, text='', fg='black', bg='white', relief=tk.RIDGE,
                                                  justify=tk.CENTER, width=17, borderwidth=3)

        # dropdown
        self.from_currency_variable = StringVar(self)
        self.from_currency_variable.set("USD")  # default value
        self.to_currency_variable = StringVar(self)
        self.to_currency_variable.set("EUR")  # default value

        font = ("Courier", 12, "bold")
        self.option_add('*TCombobox*Listbox.font', font)
        self.from_currency_dropdown = ttk.Combobox(self, textvariable=self.from_currency_variable,
                                                   values=['USD','EUR','AUD','CAD','CNY','CZK','DKK','GBP','JPY','NOK','NZD'], font=font,
                                                   state='readonly', width=12, justify=tk.CENTER)
        self.to_currency_dropdown = ttk.Combobox(self, textvariable=self.to_currency_variable,
                                                 values=['USD','EUR','AUD','CAD','CNY','CZK','DKK','GBP','JPY','NOK','NZD'], font=font,
                                                 state='readonly', width=12, justify=tk.CENTER)

        # placing
        self.from_currency_dropdown.place(x=30, y=120)
        self.amount_field.place(x=36, y=150)
        self.to_currency_dropdown.place(x=340, y=120)

        self.converted_amount_field_label.place(x=346, y=150)


        # Convert button
        self.convert_button = Button(self, text="Convert", fg="black", command=self.perform)
        self.convert_button.config(font=('Courier', 10, 'bold'))
        self.convert_button.place(x=225, y=135)

    def perform(self, ):
        amount = float(self.amount_field.get())
        from_curr = self.from_currency_variable.get()
        to_curr = self.to_currency_variable.get()

        converted_amount = self.currency_converter.convert(from_curr, to_curr, amount)
        converted_amount = round(converted_amount, 2)

        self.converted_amount_field_label.config(text=str(converted_amount))

    def restrictNumberOnly(self, action, string):
        regex = re.compile(r"[0-9,]*?(\.)?[0-9,]*$")
        result = regex.match(string)
        return (string == "" or (string.count('.') <= 1 and result is not None))

if __name__ == '__main__':

    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    converter = CurrencyConverter(url)

    CurrencyConverterUI(converter)
    mainloop()