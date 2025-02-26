import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        # Diccionario para almacenar los saldos de los usuarios
        self.balances = {}
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            #if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
            if not self.valid_proof(last_block['proof'], block['proof'], block['previous_hash']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block
    """
    # Funció original  
    def new_transaction(self, sender, recipient, amount, order):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'order': order,    
        }
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1
    """
    
    def new_transaction(self, sender, recipient, amount, order):
        # Ignorar transacciones de recompensa minera (donde sender="0")
        if sender != "0":
            # Verificar si el remitente tiene suficiente saldo
            if self.balances.get(sender, 0) < amount:
                return 'Insufficient balance', 400  # Devolver error si no hay saldo suficiente
            # Actualizar los saldos del remitente y destinatario
            self.update_balances(sender, recipient, amount)

        # Crear la transacción
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'order': order,
        }

        # Agregar la transacción a la lista de transacciones pendientes
        self.current_transactions.append(transaction)

        # Devolver el índice del próximo bloque donde se incluirá la transacción
        return {'message': f'Transaction will be added to Block {self.last_block["index"] + 1}'}, 201

    def update_balances(self, sender, recipient, amount):

        if sender not in self.balances:
            self.balances[sender] = 0
        if recipient not in self.balances:
            self.balances[recipient] = 0
        self.balances[sender] -= amount
        self.balances[recipient] += amount

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
        order=0,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Verificar que los campos requeridos estén presentes
    required = ['sender', 'recipient', 'amount', 'order']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Crear una nueva transacción
    result = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], values['order'])

    # Manejar la respuesta
    if isinstance(result, tuple):  # Si hay un error (saldo insuficiente)
        message, status_code = result
        return jsonify({'message': message}), status_code

    return jsonify(result), 201


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

    #for node in nodes:
    #    blockchain.register_node(node)
    blockchain.register_node(nodes)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


###################### Funcions afegides 

@app.route('/nodes/list', methods=['GET'])
def list_nodes():
    response = {
        'message': 'List of registered nodes',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 200


@app.route('/validate', methods=['GET'])
def validate_chain():
    is_valid = blockchain.valid_chain(blockchain.chain)
    if is_valid:
        response = {
            'message': 'The blockchain is valid.',
            'chain': blockchain.chain
        }
    else:
        response = {
            'message': 'The blockchain is invalid.',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/manipulate', methods=['POST'])
def manipulate_chain():
    values = request.get_json()
    if not values or 'index' not in values or 'new_data' not in values:
        return 'Invalid input', 400

    index = values['index']
    new_data = values['new_data']

    if index < 0 or index >= len(blockchain.chain):
        return 'Index out of range', 400


    blockchain.chain[index]['transactions'] = new_data

    response = {
        'message': f'Block {index} has been manipulated',
        'chain': blockchain.chain
    }
    return jsonify(response), 200
#####################  

        ## Funcions opcionals

# Mostrem els saldos dels usuaris
@app.route('/balances', methods=['GET'])
def get_balances():
    return jsonify(blockchain.balances), 200
        
@app.route('/balances/add', methods=['POST'])
def add_balance():
    values = request.get_json()
    address = values.get('address')
    amount = values.get('amount')

    if not address or amount is None:
        return "Error: Please provide both 'address' and 'amount'", 400

    blockchain.balances[address] = blockchain.balances.get(address, 0) + amount
    response = {
        'message': 'Balance updated successfully',
        'balances': blockchain.balances,
    }
    return jsonify(response), 200

        ##


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
