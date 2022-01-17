"""
Author: Abhiraj Mengade
Date:   17-01-2022
Description:
A basic blockchain implementation in python
"""
#imports
import time
import hashlib
import json
from flask import Flask, jsonify



class blockchain:
    def __init__(self):
        self.chain = []
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.chain.append(block)
        return block
    
    def last_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, last_proof):
        proof = 0
        check = False
        while check is False:
            hash_operation = hashlib.sha256(str(last_proof**2 - proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check = True
            else:
                proof += 1
        return proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(previous_proof**2 - proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
#starting flask
app = Flask(__name__)
blockybalboa = blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockybalboa.last_block()
    previous_proof = previous_block['proof']
    proof = blockybalboa.proof_of_work(previous_proof)
    previous_hash = blockybalboa.hash(previous_block)
    blockybalboa.new_block(proof, previous_hash)
    response = {
        'message': 'New Block Forged',
        'index': blockybalboa.last_block['index'],
        'proof': blockybalboa.last_block['proof'],
        'previous_hash': blockybalboa.last_block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockybalboa.chain,
        'length': len(blockybalboa.chain),
    }
    return jsonify(response), 200

app.run(host='0.0.0.0', port=5000)

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockybalboa.is_chain_valid(blockybalboa.chain)
    if is_valid:
        response = {
            'message': 'All good. The Blockchain is valid.'
        }
    else:
        response = {
            'message': "Blocky's got a problem. The Blockchain is not valid."
        }
    return jsonify(response), 200

