# @version ^0.3.3

from vyper.interfaces import ERC20

MONTH_TIMEDELTA: constant(uint256) = 2629800

DISTRIBUTION_THRESHOLD: constant(uint256) = 1_000_000_000_000_000_000

MEMBERS: constant(uint8) = 7
SHARES: constant(uint256) = 10000

VENDORS: constant(uint8) = 3

start_timestamp: public(uint256)
distributions_counter: public(uint256)

owner: public(address)

members: public(address[MEMBERS])
equities: public(uint256[MEMBERS])

vendors: public(address[VENDORS])
fees: public(uint256[VENDORS])

token: ERC20

event Distribution:
    receiver: indexed(address)
    amount: uint256

@external
def __init__(
        start_timestamp: uint256,
        token_contract: address,
        members: address[MEMBERS],
        equities: uint256[MEMBERS],
        vendors: address[VENDORS],
        fees: uint256[VENDORS],
    ):
    sum: uint256 = 0

    for ix in range(MEMBERS):
        assert (members[ix] == ZERO_ADDRESS and equities[ix] == 0)  \
            or (members[ix] != ZERO_ADDRESS and equities[ix]  > 0), \
            'Only zero address can have zero equity'

        sum += equities[ix]

    assert sum == SHARES, 'Equities sum not equals total shares'

    for ix in range(VENDORS):
        assert (vendors[ix] == ZERO_ADDRESS and fees[ix] == 0)  \
            or (vendors[ix] != ZERO_ADDRESS and fees[ix]  > 0), \
            'Only zero address can have zero fee'

    self.start_timestamp = start_timestamp
    self.distributions_counter = 0

    self.owner = msg.sender

    self.members = members
    self.equities = equities

    self.vendors = vendors
    self.fees = fees

    self.token = ERC20(token_contract)

@internal
@view
def _pending_distributions() -> uint256:
    assert block.timestamp > self.start_timestamp # dev: Contract start date is in the future

    months_since_start: uint256 = (block.timestamp - self.start_timestamp) / MONTH_TIMEDELTA

    return months_since_start - self.distributions_counter

@external
@view
def pending_distributions() -> uint256:
    return self._pending_distributions()

@external
def distribute():
    token_balance: uint256 = self.token.balanceOf(self)

    assert token_balance > DISTRIBUTION_THRESHOLD, 'Balance below the distribution threshold'

    pending_distributions: uint256 = self._pending_distributions()

    if pending_distributions > 0:
        # Check if there are enough tokens for vendors
        vendors_total: uint256 = 0

        for fee in self.fees:
            vendors_total += fee * pending_distributions

        assert token_balance >= vendors_total, 'Insufficient balance to pay vendors'

        # Update the distributions count
        self.distributions_counter += pending_distributions

        # Pay vendors
        for ix in range(VENDORS):
            vendor: address = self.vendors[ix]
            amount: uint256 = self.fees[ix] * pending_distributions

            if amount > 0:
                self.token.transfer(vendor, amount)

                log Distribution(vendor, amount)

        token_balance -= vendors_total

    # Pay members
    for ix in range(MEMBERS):
        member: address = self.members[ix]
        equity: uint256 = self.equities[ix]

        amount: uint256 = token_balance * equity / SHARES

        if amount > 0:
            self.token.transfer(member, amount)

            log Distribution(member, amount)

@external
def change_owner(new_owner: address):
    assert msg.sender == self.owner # dev: Caller is not the owner

    self.owner = new_owner

@external
def change_members_and_equities(members: address[MEMBERS], equities: uint256[MEMBERS]):
    assert msg.sender == self.owner # dev: Caller is not the owner

    assert self._pending_distributions() == 0, 'There are pending distributions'

    sum: uint256 = 0

    for ix in range(MEMBERS):
        assert (members[ix] == ZERO_ADDRESS and equities[ix] == 0)  \
            or (members[ix] != ZERO_ADDRESS and equities[ix]  > 0), \
            'Only zero address can have zero equity'

        sum += equities[ix]

    assert sum == SHARES, 'Equities sum not equals total shares'

    self.members = members
    self.equities = equities

@external
def change_vendors_and_fees(vendors: address[VENDORS], fees: uint256[VENDORS]):
    assert msg.sender == self.owner # dev: Caller is not the owner

    assert self._pending_distributions() == 0, 'There are pending distributions'

    for ix in range(VENDORS):
        assert (vendors[ix] == ZERO_ADDRESS and fees[ix] == 0)  \
            or (vendors[ix] != ZERO_ADDRESS and fees[ix]  > 0), \
            'Only zero address can have zero fee'

    self.vendors = vendors
    self.fees = fees

@external
def shutdown():
    assert msg.sender == self.owner # dev: Caller is not the owner

    # Return remaining tokens
    token_balance: uint256 = self.token.balanceOf(self)

    if token_balance > 0:
        self.token.transfer(self.owner, token_balance)

    # Return Ether and destroy
    selfdestruct(self.owner)
