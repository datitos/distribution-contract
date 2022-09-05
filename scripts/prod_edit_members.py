from brownie.network import priority_fee
priority_fee('auto')

from brownie import Unit, accounts

def ether(value):
    return value * 10**18

CONTRACT = Unit.at('0x09364b188f062cce8dec8dd1022111aa643bf33a')

BATTO = '0x915194409e7b22dfab38c3942855eb826c41816d'
MOYA  = '0xe63c92dc89b4fb6ea8ea04cf8bf8df6c8f1bf823'
GUS   = '0x1d3c45d3e1cec96730a3ab7e314d6d4bea303a2f'
TOMI  = '0xc1a4977d1a9abd797196fc4409cc25bd79f9bfc1'
GONZA = '0xc81167615bd6b5486d0c20981a4f09d7c6f8f608'
IMRE  = '0x9d36ec9da23ef8d32479cc51ffd44c8b5c380331'
ZERO  = '0x0000000000000000000000000000000000000000'

OWNER = accounts.load('test_account')

def main():
    CONTRACT.change_members_and_equities(
        [BATTO, MOYA,  GUS, TOMI, GONZA, ZERO, ZERO],
        [ 1538, 3846, 2308, 1154,  1154,    0,    0],
        {'from': OWNER}
    )

    CONTRACT.change_vendors_and_fees(
        [      IMRE, ZERO, ZERO],
        [ether(150),    0,    0],
        {'from': OWNER}
    )
