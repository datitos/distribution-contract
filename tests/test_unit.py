import pytest
import brownie
from brownie.network.state import Chain
from datetime import datetime, timedelta

chain = Chain()

## Accounts
#
# 0. Client / Also owner of TST contract
# CLIENT = accounts[0]
#
# 1. Original contract owner
# OWNER = accounts[1]
#
# 2. New contract owner
# NEW_OWNER = accounts[2]
#
# 3. Member A 50% equity
# MEMBER_A = accounts[3]
#
# 4. Member B 30% equity
# MEMBER_B = accounts[4]
#
# 5. Member C 20% equity
# MEMBER_C = accounts[5]
#
# 6. Vendor A 150 TST
# VENDOR_A = accounts[6]
#
# 7. Vendor B  50 TST
# VENDOR_B = accounts[7]

# Zero address
ZERO = '0x0000000000000000000000000000000000000000'

# Contract start date is set to the first day of the next month
# i.e. 2022/06/01
START = datetime(datetime.now().year, datetime.now().month, 1) + timedelta(days=31)

def ether(value):
    return value * 10**18

def chain_sleep(interval):
    chain.sleep( int( interval.total_seconds() ) )
    chain.mine()

@pytest.fixture(scope='module')
def token(Token, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]

    yield Token.deploy('Test Token', 'TST', 18, ether(1_000_000), {'from': CLIENT})

@pytest.fixture(scope='module')
def group(Unit, token, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    yield Unit.deploy(
        int( START.timestamp() ), # seconds
        token,
        [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
        [    5000,     3000,     2000,    0,    0,    0,    0],
        [  VENDOR_A,  VENDOR_B, ZERO],
        [ether(150), ether(50),    0],
        {'from': OWNER}
    )

def test_equities_should_equal_shares_when_deploying(Unit, token, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('Equities sum not equals total shares'):
        Unit.deploy(
            int( START.timestamp() ), # seconds
            token,
            [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
            [    5000,      500,      500,    0,    0,    0,    0], # sums 6000, should be 10000
            [  VENDOR_A,  VENDOR_B, ZERO],
            [ether(150), ether(50),    0],
            {'from': OWNER}
        )

def test_only_zero_address_should_have_zero_equity_when_deploying(Unit, token, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('Only zero address can have zero equity'):
        Unit.deploy(
            int( START.timestamp() ), # seconds
            token,
            [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
            [    5000,     5000,        0,    0,    0,    0,    0],
            [  VENDOR_A,  VENDOR_B, ZERO],
            [ether(150), ether(50),    0],
            {'from': OWNER}
        )

    with brownie.reverts('Only zero address can have zero equity'):
        Unit.deploy(
            int( START.timestamp() ), # seconds
            token,
            [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
            [    4000,      500,      500, 1000,    0,    0,    0],
            [  VENDOR_A,  VENDOR_B, ZERO],
            [ether(150), ether(50),    0],
            {'from': OWNER}
        )

def test_only_zero_address_should_have_zero_fee_when_deploying(Unit, token, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('Only zero address can have zero fee'):
        Unit.deploy(
            int( START.timestamp() ), # seconds
            token,
            [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
            [    5000,     3000,     2000,    0,    0,    0,    0],
            [  VENDOR_A,  VENDOR_B, ZERO],
            [ether(150),         0,    0],
            {'from': OWNER}
        )

    with brownie.reverts('Only zero address can have zero fee'):
        Unit.deploy(
            int( START.timestamp() ), # seconds
            token,
            [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
            [    5000,     3000,     2000,    0,    0,    0,    0],
            [  VENDOR_A,  VENDOR_B,     ZERO],
            [ether(150), ether(50), ether(1)],
            {'from': OWNER}
        )

def test_should_not_distribute_small_balances(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('Balance below the distribution threshold'):
        group.distribute({'from': OWNER})

def test_should_not_distribute_before_start_date(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    token.transfer(group, ether(200), {'from': CLIENT})

    with brownie.reverts('dev: Contract start date is in the future'):
        group.distribute({'from': OWNER})

def test_distribution(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    # Make a time travel to the ~10th day of the month following the start date
    # i.e. 2022/07/10
    interval = START + timedelta(days=40) - datetime.now()
    chain_sleep(interval)

    assert group.pending_distributions({'from': OWNER}) == 1

    token.transfer(group, ether(10000), {'from': CLIENT})

    group.distribute({'from': OWNER})

    assert token.balanceOf(MEMBER_A) == ether(5000)
    assert token.balanceOf(MEMBER_B) == ether(3000)
    assert token.balanceOf(MEMBER_C) == ether(2000)
    assert token.balanceOf(VENDOR_A) == ether( 150)
    assert token.balanceOf(VENDOR_B) == ether(  50)

    assert group.distributions_counter() == 1

def test_skipped_distribution(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    # About two months without triggering a distribution
    # i.e. 2022/09/10
    chain_sleep(timedelta(days=60))

    assert group.pending_distributions({'from': OWNER}) == 2

    token.transfer(group, ether(10400), {'from': CLIENT})

    group.distribute({'from': OWNER})

    # Values add up from previous balance
    assert token.balanceOf(MEMBER_A) == ether(10000)
    assert token.balanceOf(MEMBER_B) == ether( 6000)
    assert token.balanceOf(MEMBER_C) == ether( 4000)
    # Vendors get paid twice (once per month)
    assert token.balanceOf(VENDOR_A) == ether(  450)
    assert token.balanceOf(VENDOR_B) == ether(  150)

    assert group.distributions_counter() == 3

def test_repeated_distribution(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    assert group.pending_distributions({'from': OWNER}) == 0

    token.transfer(group, ether(10000), {'from': CLIENT})

    group.distribute({'from': OWNER})

    # Values add up from previous balance
    assert token.balanceOf(MEMBER_A) == ether(15000)
    assert token.balanceOf(MEMBER_B) == ether( 9000)
    assert token.balanceOf(MEMBER_C) == ether( 6000)
    # Vendors already got paid this month (no balance increase)
    assert token.balanceOf(VENDOR_A) == ether(  450)
    assert token.balanceOf(VENDOR_B) == ether(  150)

    assert group.distributions_counter() == 3

def test_anyone_can_distribute(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    # i.e. 2022/10/10
    chain_sleep(timedelta(days=30))

    assert group.pending_distributions({'from': OWNER}) == 1

    token.transfer(group, ether(10200), {'from': CLIENT})

    group.distribute({'from': CLIENT})

    assert group.distributions_counter() == 4

def test_one_pending_distribution_per_completed_month(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    assert group.pending_distributions({'from': OWNER}) == 0

    # i.e. 2023/11/10
    chain_sleep(timedelta(days=365))

    assert group.pending_distributions({'from': OWNER}) == 12

def test_pay_vendors_first(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    token.transfer(group, ether(10), {'from': CLIENT})

    with brownie.reverts('Insufficient balance to pay vendors'):
        group.distribute({'from': OWNER})

    assert group.distributions_counter() == 4

def test_should_not_change_members_if_there_are_pending_distributions(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('There are pending distributions'):
        group.change_members_and_equities(
            [MEMBER_A, MEMBER_B, ZERO, ZERO, ZERO, ZERO, ZERO],
            [    5000,     5000,    0,    0,    0,    0,    0],
            {'from': OWNER}
        )

def test_should_not_change_vendors_if_there_are_pending_distributions(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('There are pending distributions'):
        group.change_vendors_and_fees(
            [  VENDOR_A, ZERO, ZERO],
            [ether(200),    0,    0],
            {'from': OWNER}
        )

def test_change_members_and_equities(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    # execute pending distributions
    token.transfer(group, ether(2400), {'from': CLIENT})

    group.distribute({'from': OWNER})

    with brownie.reverts('dev: Caller is not the owner'):
        group.change_members_and_equities(
            [MEMBER_A, MEMBER_B, ZERO, ZERO, ZERO, ZERO, ZERO],
            [    5000,     5000,    0,    0,    0,    0,    0],
            {'from': MEMBER_B}
        )

    group.change_members_and_equities(
        [MEMBER_A, MEMBER_B, ZERO, ZERO, ZERO, ZERO, ZERO],
        [    5000,     5000,    0,    0,    0,    0,    0],
        {'from': OWNER}
    )

    assert group.members(0) == MEMBER_A
    assert group.members(1) == MEMBER_B
    assert group.members(2) == ZERO
    assert group.members(3) == ZERO
    assert group.members(4) == ZERO
    assert group.members(5) == ZERO
    assert group.members(6) == ZERO

    assert group.equities(0) == 5000
    assert group.equities(1) == 5000
    assert group.equities(2) == 0
    assert group.equities(3) == 0
    assert group.equities(4) == 0
    assert group.equities(5) == 0
    assert group.equities(6) == 0

def test_equities_should_equal_shares_when_changing_members(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('Equities sum not equals total shares'):
        group.change_members_and_equities(
            [MEMBER_A, MEMBER_B, ZERO, ZERO, ZERO, ZERO, ZERO],
            [    5000,     6000,    0,    0,    0,    0,    0], # sums 6000, should be 10000
            {'from': OWNER}
        )

def test_only_zero_address_should_have_zero_equity_when_changing_members(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('Only zero address can have zero equity'):
        group.change_members_and_equities(
            [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
            [    5000,     5000,        0,    0,    0,    0,    0],
            {'from': OWNER}
        )

    with brownie.reverts('Only zero address can have zero equity'):
        group.change_members_and_equities(
            [MEMBER_A, MEMBER_B, MEMBER_C, ZERO, ZERO, ZERO, ZERO],
            [    4000,      500,      500, 1000,    0,    0,    0],
            {'from': OWNER}
        )

def test_change_vendors_and_fees(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('dev: Caller is not the owner'):
        group.change_vendors_and_fees(
            [  VENDOR_A, ZERO, ZERO],
            [ether(200),    0,    0],
            {'from': VENDOR_A}
        )

    group.change_vendors_and_fees(
        [  VENDOR_A, ZERO, ZERO],
        [ether(200),    0,    0],
        {'from': OWNER}
    )

    assert group.vendors(0) == VENDOR_A
    assert group.vendors(1) == ZERO
    assert group.vendors(2) == ZERO

    assert group.fees(0) == ether(200)
    assert group.fees(1) == 0
    assert group.fees(2) == 0

def test_only_zero_address_should_have_zero_fee_when_chainging_vendors(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('Only zero address can have zero fee'):
        group.change_vendors_and_fees(
            [  VENDOR_A,  VENDOR_B, ZERO],
            [ether(150),         0,    0],
            {'from': OWNER}
        )

    with brownie.reverts('Only zero address can have zero fee'):
        group.change_vendors_and_fees(
            [  VENDOR_A,  VENDOR_B,     ZERO],
            [ether(150), ether(50), ether(1)],
            {'from': OWNER}
        )

def test_change_owner(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    with brownie.reverts('dev: Caller is not the owner'):
        group.change_owner(NEW_OWNER, {'from': NEW_OWNER})

    group.change_owner(NEW_OWNER, {'from': OWNER})

    assert group.owner() == NEW_OWNER

def test_shutdown(token, group, accounts):
    CLIENT = accounts[0]
    OWNER = accounts[1]
    NEW_OWNER = accounts[2]
    MEMBER_A = accounts[3]
    MEMBER_B = accounts[4]
    MEMBER_C = accounts[5]
    VENDOR_A = accounts[6]
    VENDOR_B = accounts[7]

    token.transfer(group, ether(10000), {'from': CLIENT})

    with brownie.reverts('dev: Caller is not the owner'):
        group.shutdown({'from': CLIENT})

    assert token.balanceOf(NEW_OWNER) == 0

    group.shutdown({'from': NEW_OWNER})

    assert token.balanceOf(NEW_OWNER) == ether(10000)
