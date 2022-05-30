from brownie import Daititos, accounts

def ether(value):
    return value * 10**18

# 2022/03/01 (in seconds)
START = 1646092800

# Test Standard Token (TST) contract on Ropsten network
CONTRACT = '0x722dd3F80BAC40c951b51BdD28Dd19d435762180'

FAKE_MOYA  = '0x4604D2f8bD2C232B8a28d5418174F040D8889da6'
FAKE_VICKY = '0xA2200b4919aAD76cFC9Bd7D1dA143E41c1be7EFc'
FAKE_GUS   = '0xd85725b672C443ebD7f87d484D38106b7663F971'
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

owner = accounts.load('test_account', password='40xmax')

def main():
    Daititos.deploy(
        START,
        CONTRACT,
        [owner, FAKE_MOYA, FAKE_VICKY, FAKE_GUS, ZERO_ADDRESS],
        [3000, 3000, 2000, 2000, 0],
        [owner, ZERO_ADDRESS, ZERO_ADDRESS],
        [1000, 0, 0],
        { 'from': owner }
    )
