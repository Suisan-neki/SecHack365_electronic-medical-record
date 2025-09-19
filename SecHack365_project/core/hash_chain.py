import hashlib
import json

def calculate_hash(data):
    # 辞書をJSON文字列に変換してハッシュを計算
    data_string = json.dumps(data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(data_string).hexdigest()

class HashChain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # 最初のブロック（ジェネシスブロック）を作成
        genesis_data = {"message": "Genesis Block"}
        genesis_hash = calculate_hash(genesis_data)
        self.chain.append({"data": genesis_data, "hash": genesis_hash, "previous_hash": "0"})

    def add_block(self, data):
        previous_hash = self.chain[-1]["hash"]
        current_hash = calculate_hash(data)
        self.chain.append({"data": data, "hash": current_hash, "previous_hash": previous_hash})

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 現在のブロックのハッシュが正しいか検証
            if current_block["hash"] != calculate_hash(current_block["data"]):
                return False

            # 前のブロックのハッシュと一致するか検証
            if current_block["previous_hash"] != previous_block["hash"]:
                return False
        return True
