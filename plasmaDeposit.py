#!/usr/bin/env python3

from web3 import Web3, WebsocketProvider
from eth_account import Account

NETWORK="ropsten"
INFURA_APPID='xxxxx'
PROVIDER="wss://{}.infura.io/ws/v3/{}".format(NETWORK, INFURA_APPID)

PLASMA_ROOT="0x60e2b19b9a87a3f37827f2c8c8306be718a5f9b4"

APPROVE_ABI = '[\
    {\
        "constant": false,\
        "inputs": [\
            { "internalType": "address", "name": "spender", "type": "address" },\
            { "internalType": "uint256", "name": "amount", "type": "uint256" }\
        ],\
        "name": "approve",\
        "outputs": [\
            { "internalType": "bool", "name": "", "type": "bool" }\
        ],\
        "payable": false,\
        "stateMutability": "nonpayable",\
        "type": "function"\
    }\
]'

DEPOSIT_ABI = '[\
    {\
        "constant": false,\
        "inputs": [\
            { "internalType": "address", "name": "token", "type": "address" },\
            { "internalType": "address", "name": "user", "type": "address" },\
            { "internalType": "uint256", "name": "amount", "type": "uint256" }\
        ],\
        "name": "deposit",\
        "outputs": [],\
        "payable": false,\
        "stateMutability": "nonpayable",\
        "type": "function"\
    }\
]'

if __name__ == "__main__":

    print('Using network: {}'.format(NETWORK))

    tokenAddress = input("ERC20 addess:")
    tokenAmount = input("Amount:")

    key = input('Private key (from):')
    mappedAddress = input("Plasma (to) address:")

    w3 = Web3(WebsocketProvider(PROVIDER))

    tokenRegistry = w3.eth.contract(
        abi = APPROVE_ABI,
        address = w3.toChecksumAddress(tokenAddress)
    )

    plasmaRoot = w3.eth.contract(
        abi = DEPOSIT_ABI,
        address = w3.toChecksumAddress(PLASMA_ROOT)
    )

    w3Account = Account.privateKeyToAccount(key)

    transferTx = tokenRegistry.functions.approve(
        w3.toChecksumAddress(PLASMA_ROOT),
        w3.toInt(text=tokenAmount)
    ).buildTransaction({
        'nonce': w3.eth.getTransactionCount(w3Account.address),
        'gasPrice': w3.toWei('5', 'gwei'),
        'gas': 5000000
    })

    # Sign with admin account key with TSX tokens
    signed_txn = w3.eth.account.signTransaction(
        transferTx,
        private_key = w3Account.privateKey
    )

    # Broadcast tx to network
    print("Calling approve()")
    txHash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    print("Waiting Tx:{} to be mined".format(txHash.hex()))
    receipt = w3.eth.waitForTransactionReceipt(txHash)

    # Deposit
    transferTx = plasmaRoot.functions.deposit(
        w3.toChecksumAddress(tokenAddress),
        w3.toChecksumAddress(mappedAddress),
        w3.toInt(text=tokenAmount)
    ).buildTransaction({
        'nonce': w3.eth.getTransactionCount(w3Account.address),
        'gasPrice': w3.toWei('5', 'gwei'),
        'gas': 5000000
    })

    signed_txn = w3.eth.account.signTransaction(
        transferTx,
        private_key = w3Account.privateKey
    )

    # Broadcast tx to network
    print("Calling deposit()")
    txHash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    print("Waiting Tx:{} to be mined".format(txHash.hex()))
    receipt = w3.eth.waitForTransactionReceipt(txHash)

    print("Done...")
