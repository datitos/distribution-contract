# Distribution contract

See the [blog post](https://coinsbench.com/smart-contract-for-distribution-of-payments-within-a-co-op-3c14a78dcc4b) with the project description.

## Requirements

Install Ganache local testnet

```sh
$ npm install -g ganache-cli
```

Install Brownie framework

```sh
$ pip install -r requirements.txt
```

You should create an `env` file with these keys

```txt
WEB3_INFURA_PROJECT_ID=
ETHERSCAN_TOKEN=
```

## Development

Run test suit (local testnet) with

```sh
$ brownie test tests/test_unit.py
```

Interact with the deployed contract at Ropsten testnet

```sh
$ brownie console --network ropsten
```

Deploy to mainnet

```sh
$ brownie run scripts/prod_deploy.py --network mainnet
```

Distribute a payment

```sh
$ brownie run scripts/prod_distribute.py --network mainnet
```
