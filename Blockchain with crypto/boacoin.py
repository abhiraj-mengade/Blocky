"""
Author: Abhiraj Mengade
Date:   20-01-2022
Description:
A basic cryptocoin  implementation on a blockchain in python 
"""
#imports
from re import A
import time
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse



class blockchain:
    def __init__(self):
        self.chain = []
        self.transactions=[]
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions=[]
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
    
    def add_transactions(self,sender, receiver, amount):
        self.transactions.append({
            'sender':sender,
            'receiver':receiver,
            'boas': amount
        })
        previous_block = self.last_block()
        return previous_block['index'] + 1


    def add_node(self, address):
        parsed_url= urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code ==200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length=length
                    longest_chain= chain
        if longest_chain:
            self.chain = longest_chain
            return True 
        return False










        



    


#starting flask
app = Flask(__name__)
blockybalboa = blockchain()
node_address = str(uuid4()).replace('-','')

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockybalboa.last_block()
    previous_proof = previous_block['proof']
    proof = blockybalboa.proof_of_work(previous_proof)
    blockybalboa.add_transactions(sender = node_address, receiver='Abhiraj', amount=3.14)
    previous_hash = blockybalboa.hash(previous_block)
    
    block = blockybalboa.new_block(proof, previous_hash)
    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
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

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    request_data = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in request_data for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockybalboa.add_transactions(request_data['sender'], request_data['receiver'], request_data['boas'])
    response = {
        'message': f'This transaction will be added to Blockyboa {index}'
    }
    return jsonify(response), 201
