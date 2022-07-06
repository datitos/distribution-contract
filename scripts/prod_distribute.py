from brownie import Unit, accounts

ME = accounts.load('test_account')

# Datitos contract
CONTRACT = Unit.at('0x09364b188f062cce8dec8dd1022111aa643bf33a')

def main():
    CONTRACT.distribute({'from': ME})
