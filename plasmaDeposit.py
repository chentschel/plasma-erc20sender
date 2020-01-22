#!/usr/bin/env python3

from web3 import Web3, WebsocketProvider
from eth_account import Account

NETWORK="mainnet"
PLASMA_ROOT="0xb3Fe6f0eB663DbE4D4813Ee32d6f30d64640D2f8"

INFURA_APPID='4427dca984be4ed983bba5a77f3855b4'
PROVIDER="wss://{}.infura.io/ws/v3/{}".format(NETWORK, INFURA_APPID)

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
            { "internalType": "address", "name": "_token", "type": "address" },\
            { "internalType": "address", "name": "_user", "type": "address" },\
            { "internalType": "uint256", "name": "_amount", "type": "uint256" }\
        ],\
        "name": "depositERC20ForUser",\
        "outputs": [],\
        "payable": false,\
        "stateMutability": "nonpayable",\
        "type": "function"\
    }\
]'

if __name__ == "__main__":

    tokenAddress = input("{} Token (ERC20) address: ".format(NETWORK))
    tokenAmount = input("Amount (wei): ")

    key = input("Private key (from): ")
    mappedAddress = input("Mapped plasma (to) address: ")

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
    transferTx = plasmaRoot.functions.depositERC20ForUser(
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
