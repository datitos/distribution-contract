# @version ^0.3.1

'''
Contract is not editable, if something needs to change, deploy a new one.
'''

SIZE: constant(uint8) = 4

rate: public(uint256)
members: public(address[SIZE])
owner: public(address)
equities: public(uint8[SIZE])

event Payment:
    sender: indexed(address)
    amount: uint256

event Distribution:
    receiver: indexed(address)
    amount: uint256

@external
@payable
def __default__():
    log Payment(msg.sender, msg.value)

@external
def __init__(rate: uint256, members: address[SIZE], equities: uint8[SIZE]):
    sum: uint8 = 0

    for ix in range(SIZE):
        sum += equities[ix]

    assert sum == 100

    self.rate = rate
    self.members = members
    self.owner = msg.sender
    self.equities = equities

@internal
@pure
def _calculate(amount: uint256, equities: uint8[4]) -> uint256[4]:
    out: uint256[4] = [0, 0, 0, 0]

    for ix in range(SIZE):
      out[ix] = amount * convert(equities[ix], uint256) / 100

    return out

@external
@view
def calculate(amount: uint256, equities: uint8[4]) -> uint256[4]:
    return self._calculate(amount, equities)

@internal
def _distribute():
    splits: uint256[SIZE] = self._calculate(self.balance, self.equities)

    for ix in range(SIZE):
        member: address = self.members[ix]
        amount: uint256 = splits[ix]

        send(member, amount)

        log Distribution(member, amount)

@external
def distribute():
    self._distribute()

@external
@payable
def pay():
    log Payment(msg.sender, msg.value)

    self._distribute()

@external
def shutdown():
  assert msg.sender == self.owner

  self._distribute()
  selfdestruct(self.owner)
