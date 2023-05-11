import json
import time
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


testnet_rpc_url = os.getenv('testnet_rpc_url')
w3_client = Web3(Web3.HTTPProvider(testnet_rpc_url))

if not w3_client.is_connected():
    exit(-1)


currency_contract_address = os.getenv('currency_contract_address')
print(currency_contract_address)
with open('currency_contract_abi.json') as f:
    currency_contract_abi = json.load(f)
currency = w3_client.eth.contract(address=currency_contract_address, abi=currency_contract_abi)


manager_contract_address = os.getenv('manager_contract_address')
with open('manager_contract_abi.json') as f:
    manager_contract_abi = json.load(f)
manager = w3_client.eth.contract(address=manager_contract_address, abi=manager_contract_abi)


token_contract_address = os.getenv('token_contract_address')
with open('token_contract_abi.json') as f:
    token_contract_abi = json.load(f)
token = w3_client.eth.contract(address=token_contract_address, abi=token_contract_abi)


owner_address = currency.functions.owner().call()
owner_private_key = os.getenv('owner_private_key')
chain_id = w3_client.eth.chain_id
nonce = w3_client.eth.get_transaction_count(owner_address)


def op_create_account(wallet):
    acc = w3_client.eth.account.create(wallet)
    return (acc.address, acc._private_key)


def op_approve_user(wallet, private_key):
    tx = token.functions.setApprovalForAll(manager_contract_address, True).build_transaction(
        {
            "chainId": chain_id,
            "from": wallet,
            "nonce": w3_client.eth.get_transaction_count(wallet),
        }
    )
    signed_tx = w3_client.eth.account.sign_transaction(tx, private_key)
    send_tx = w3_client.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3_client.eth.wait_for_transaction_receipt(send_tx)


op_approve_user(owner_address, owner_private_key)


def op_emit_token(tokenid, amount, series):
    nonce = w3_client.eth.get_transaction_count(owner_address)
    tx = token.functions.emitTokens(
        tokenid,
        amount,
        {
            "serialNumber": series.id,
            "expirationTime": int(series.expiration_datetime.timestamp()),
            "price": series.cost,
            "profit": series.dividends,
            "isPresented": True,
        }
    ).build_transaction(
        {
            "chainId": chain_id,
            "from": owner_address,
            "nonce": nonce,
        }
    )
    signed_tx = w3_client.eth.account.sign_transaction(tx, owner_private_key)
    send_tx = w3_client.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3_client.eth.wait_for_transaction_receipt(send_tx)


def op_emit_currency(wallet, amount):
    nonce = w3_client.eth.get_transaction_count(owner_address)
    tx = currency.functions.mint(
        wallet,
        amount,
    ).build_transaction(
        {
            "chainId": chain_id,
            "from": owner_address,
            "nonce": nonce,
        }
    )
    signed_tx = w3_client.eth.account.sign_transaction(tx, owner_private_key)
    send_tx = w3_client.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3_client.eth.wait_for_transaction_receipt(send_tx)


def op_get_balance(wallet):
    return currency.functions.balanceOf(wallet).call()


def op_expire_token(left_id, right_id):
    tx = currency.functions.increaseAllowance(
        manager_contract_address,
        cost,
    ).build_transaction(
        {
            "from": wallet,
            "nonce": w3_client.eth.get_transaction_count(wallet),
        }
    )
    signed_tx = w3_client.eth.account.sign_transaction(tx, user_private_key)
    send_tx = w3_client.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3_client.eth.wait_for_transaction_receipt(send_tx)


    tx = manager.functions.expireToken(
        left_id,
        right_id,
    ).build_transaction(
        {
            "from": owner_address,
            "nonce": w3_client.eth.get_transaction_count(owner_address),
        }
    )
    signed_tx = w3_client.eth.account.sign_transaction(tx, owner_private_key)
    send_tx = w3_client.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3_client.eth.wait_for_transaction_receipt(send_tx)


def op_buy_token(wallet, private_key, left_id, right_id, cost):

    tx = currency.functions.increaseAllowance(
        manager_contract_address,
        cost,
    ).build_transaction(
        {
            "from": wallet,
            "nonce": w3_client.eth.get_transaction_count(wallet),
        }
    )

    signed_tx = w3_client.eth.account.sign_transaction(tx, private_key)
    send_tx = w3_client.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3_client.eth.wait_for_transaction_receipt(send_tx)

    tx = manager.functions.buyToken(
        left_id,
        right_id,
    ).build_transaction(
        {
            "from": wallet,
            "nonce": w3_client.eth.get_transaction_count(wallet),
        }
    )

    signed_tx = w3_client.eth.account.sign_transaction(tx, user_private_key)
    send_tx = w3_client.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3_client.eth.wait_for_transaction_receipt(send_tx)
