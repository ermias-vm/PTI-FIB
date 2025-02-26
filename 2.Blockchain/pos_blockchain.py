import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, jsonify, request
import random

class ProofOfStakeChain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.validators = {}  # Diccionario para almacenar stakes de los validadores
        # Crear el bloque génesis
        self.new_block(previous_hash='1', proof=100)

    def add_validator(self, address, stake):
        self.validators[address] = stake

    def select_validator(self):
        total_stake = sum(self.validators.values())
        rand_num = random.uniform(0, total_stake)
        cumulative_stake = 0
        for validator, stake in self.validators.items():
            cumulative_stake += stake
            if cumulative_stake >= rand_num:
                return validator


    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        # Reiniciar la lista de transacciones actuales
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount, order):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'order': order,
        }
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_stake(self):
        return self.select_validator()


app = Flask(__name__)

# Generar una dirección única para este nodo
node_identifier = str(uuid4()).replace('-', '')

# Instanciar la Blockchain
blockchain = ProofOfStakeChain()

@app.route('/mine', methods=['GET'])
def mine():
    # Seleccionar un validador usando Proof-of-Stake
    validator = blockchain.proof_of_stake()
    if not validator:
        return "No validators available", 400

    # Recompensa por minar un bloque
    blockchain.new_transaction(
        sender="0",  # La red envía la recompensa
        recipient=validator,
        amount=1,
        order=0,
    )

    # Forjar el nuevo bloque añadiéndolo a la cadena
    previous_hash = blockchain.hash(blockchain.last_block)
    block = blockchain.new_block(proof=1, previous_hash=previous_hash)

    response = {
        'message': "New Block Forged by Validator",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'validator': validator,
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount', 'order']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], values['order'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    blockchain.register_node(nodes)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/validators/add', methods=['POST'])
def add_validator():
    values = request.get_json()
    address = values.get('address')
    stake = values.get('stake')
    if not address or not stake:
        return "Error: Please provide both address and stake", 400
    blockchain.add_validator(address, stake)
    response = {
        'message': 'Validator added successfully',
        'validators': blockchain.validators,
    }
    return jsonify(response), 201

@app.route('/validators', methods=['GET'])
def get_validators():
    response = {
        'validators': blockchain.validators
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)