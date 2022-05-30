from brownie.network import priority_fee
priority_fee('auto')

from brownie import Unit, accounts
from datetime import datetime

def ether(value):
    return value * 10**18

# 2022/05/01 in seconds
START = int( datetime(2022, 5, 1).timestamp() )

# Dai Token contract on Ethereum mainnet
CONTRACT = '0x6B175474E89094C44Da98b954EedeAC495271d0F'

BATTO = '0x915194409e7b22dfab38c3942855eb826c41816d'
MOYA  = '0xe63c92dc89b4fb6ea8ea04cf8bf8df6c8f1bf823'
VICKY = '0x1d7437c68a942575c2c01801ce6ccf9e9ccd01e4'
GUS   = '0x1d3c45d3e1cec96730a3ab7e314d6d4bea303a2f'
IMRE  = '0x9d36ec9da23ef8d32479cc51ffd44c8b5c380331'
ZERO  = '0x0000000000000000000000000000000000000000'

OWNER = accounts.load('test_account')

def main():
    Unit.deploy(
        START,
        CONTRACT,
        [BATTO, MOYA, VICKY,  GUS, ZERO, ZERO, ZERO],
        [ 1538, 3846,  2308, 2308,    0,    0,    0],
        [      IMRE, ZERO, ZERO],
        [ether(120),    0,    0],
        {'from': OWNER}
    )
