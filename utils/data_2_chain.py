# -*- coding: utf-8 -*-
"""
@File        : data_2_chain.py
@Author      : liuda
@Time        : 2022/2/11 13:45
@Description :
"""
from time import time

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.exceptions import NotFoundError, TransportError

from scf_project.settings import bdb_chain_config


class ChainUtil:

    def __init__(self, bdb_root_url: str = bdb_chain_config.get('bdb_url')):
        """
        实例化
        :param bdb_root_url:
        """
        self.bdb = BigchainDB(bdb_root_url)

    def transfer(
        self, data: dict, public_key: str = bdb_chain_config.get('public_key'),
        private_key: str = bdb_chain_config.get('private_key')
    ):
        """
        将数据上链
        :param data:
        :param public_key:
        :param private_key:
        :return:
        """
        asset = {
            'data': data,
        }
        asset["data"]["time"] = int(time())
        prepared_creation_tx = self.bdb.transactions.prepare(
            operation='CREATE',
            signers=public_key,
            asset=asset,
            metadata=None
        )
        fulfilled_creation_tx = self.bdb.transactions.fulfill(
            prepared_creation_tx,
            private_keys=private_key
        )
        try:
            _ = self.bdb.transactions.send_commit(fulfilled_creation_tx)
        except TransportError:
            return None
        tx_hash = fulfilled_creation_tx['id']
        return tx_hash

    def get_tx_by_hash(self, tx_hash: str):
        """
        通过哈希获取交易详情
        :param tx_hash:
        :return:
        """
        try:
            tx = self.bdb.transactions.retrieve(tx_hash)
            asset = tx.get("asset")
            return asset.get("data")
        except NotFoundError:
            return None

    def get_block_by_tx_hash(self, tx_hash):
        """
        通过哈希获取所在块高
        :param tx_hash:
        :return:
        """
        return self.bdb.blocks.get(txid=tx_hash)


if __name__ == '__main__':
    # 生成公私钥
    from bigchaindb_driver.crypto import generate_keypair
    alice = generate_keypair()
    print(alice.public_key)
    print(alice.private_key)
    obj = ChainUtil()
    res = obj.get_tx_by_hash("596a478739a6dc2c3c54bd63ad3c3c3459c75110911b847d04dba53547981c47")
    print(res)
    res = obj.transfer({"name": 1})

