import hashlib
import json
from time import time
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from urllib.parse import urlparse
from uuid import uuid4

class Blockchain:
    def __init__(self):
        self.current_posts = []
        self.chain = []
        self.new_block(previous_hash='1', proof=100)
        self.nodes = set()

    def new_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'posts': self.current_posts,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_posts = []
        self.chain.append(block)
        return block

    def new_transaction(self, Tweet):
        self.current_posts.append({
            'Time':  time(),
            'Tweet': Tweet
        })
        return self.last_block['index'] + 1

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = request.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True

        return False
    def valid_chain(self, chain):       
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True
    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

# Instantiate the Node
app = Flask(__name__)
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'posts': block['posts'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200
    
@app.route('/chain', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/tweets', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def get_tweets():
    post = []

    for b in blockchain.chain:
        for t in b["posts"]:
            post.append(t)

    print(post)
    return jsonify(post), 200

@app.route('/transactions/new', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def new_transaction():
    values = request.get_json()
    required = ['Tweet']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['Tweet'])
    print(values)
    response = {'message': f'Tweet will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

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

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port)