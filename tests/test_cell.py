import pytest
import brownie

equities = [60, 20, 10, 10]

@pytest.fixture()
def owner(accounts):
    return accounts[0]

@pytest.fixture()
def cell(Cell, accounts, owner):
    return Cell.deploy(6000, accounts[:4], equities, { 'from': owner })

def test_constructor_members(cell, accounts):
    for i in range(4):
        assert cell.members(i) == accounts[i]

def test_constructor_members_lenght(Cell, accounts, owner):
    with pytest.raises(ValueError):
        Cell.deploy(6000, accounts[:5], equities, { 'from': owner })

def test_constructor_owner(cell, owner):
    assert cell.owner() == owner

def test_constructor_equities(cell, accounts):
    for i in range(4):
        assert cell.equities(i) == equities[i]

def test_constructor_equities_lenght(Cell, accounts, owner):
    with pytest.raises(ValueError):
        Cell.deploy(6000, accounts[:4], [20, 20, 20, 20, 20], { 'from': owner })

def test_constructor_equities_sum_100(Cell, accounts, owner):
    with brownie.reverts():
        Cell.deploy(6000, accounts[:4], [20, 20, 20, 20], { 'from': owner })

def test_constructor_equities_greater_equal_zero(Cell, accounts, owner):
    with pytest.raises(OverflowError):
        Cell.deploy(6000, accounts[:4], [-10, 0, 10, 100], { 'from': owner })

def test_constructor_equities_less_equal_100(Cell, accounts, owner):
    with brownie.reverts():
        Cell.deploy(6000, accounts[:4], [110, 0, 0, 0], { 'from': owner })

def test_calculate_never_exceeds_balance(cell, accounts):
    eth = 1_000_000_000_000_000_000

    equities_list = [
        [25, 25, 25, 25],
        [94,  3,  2,  1],
        [19, 23, 29, 29],
    ]

    for equities in equities_list:
        assert sum(equities) == 100

        splits = cell.calculate(eth, equities, { 'from': accounts[4] })
        assert sum(splits) <= eth

def test_pay_equity_split(cell, accounts):
    expected_balances = [
        account.balance() + split
        for account, split in zip( accounts[:4], [600, 200, 100, 100] )
    ]

    cell.pay({ 'from': accounts[4], 'amount': 1000 })

    new_balances = [ account.balance() for account in accounts[:4] ]

    assert new_balances == expected_balances

def test_shutdown_only_owner(cell, accounts):
    with brownie.reverts():
        cell.shutdown({ 'from': accounts[1] })

def test_shutdown_forward_owner(cell, accounts, owner):
    # according to equities (60, 20, 10, 10) and a balance of 1002,
    # distribution results in these splits (601, 200, 100, 100) due
    # integer division, which sum 1001; 1 spare wei left after distribution
    accounts[4].transfer(to=cell, amount=1002)

    # after shutdown, split of 601 wei and remaining balance of 1 wei
    # should be transferred to the owner
    expected_balance = owner.balance() + 601 + 1

    cell.shutdown({ 'from': owner })

    assert owner.balance() == expected_balance
