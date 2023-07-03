# Python program to create Blockchain

# For timestamp
import datetime

# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To store data
# in our blockchain
import json

# Flask is for creating the web
# app and jsonify is for
# displaying the blockchain
from flask import Flask, jsonify, request
import uuid
import hashlib
from binascii import hexlify
import inspect


class Blockchain:
    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0', dna={})

    # This function is created
    # to add further blocks
    # into the chain
    def create_block(self, proof, previous_hash, dna):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'data': unique_id(dna),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    # This function is created
    # to display the previous block
    def print_previous_block(self):
        return self.chain[-1]

    # This is the function for proof of work
    # and used to successfully mine the block
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_block(self, id):
        return [x for x in self.chain if x['data'] == id]

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()

            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1

        return True


# DNA. The parameter should only be DNA
# The future machine should be able to give back the DNA information in a resumed way.
# With this, id can be generated using a UUID and then adding the DNA information.
def unique_id(dna):
    dna = str(dna['chromosomes']) + str(dna['nucleotides']) + str(dna['genes']) + str(dna['codons']) if inspect.isclass(dna) else 0
    id = uuid.uuid4().hex + encrypt(dna, 16)
    return id


def encrypt(string, hash_size):
    hash = hashlib.sha256(string.encode()).hexdigest()
    return hexlify(hash.read(hash_size//2))


def jsonBlock(block):
    return jsonify({'message': 'BLOCK MINED',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'data': block['data'],
                    'previous_hash': block['previous_hash']})


# Creating the Web
# App using flask
app = Flask(__name__)

# Create the object
# of the class blockchain
blockchain = Blockchain()

# Mining a new block


@app.route('/mine_block', methods=['GET'])
def mine_block():
    dna = { 'chromosomes': request.args.get('chromosomes'),
            'timestamp': request.args.get('nucleotides'),
            'genes': request.args.get('genes'),
            'codons': request.args.get('codons')}
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash, dna)
    
    
    response = {'message': 'BLOCK MINED',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'data': block['data'],
                'previous_hash': block['previous_hash']}

    return jsonify(response), 200

# Display blockchain in json format


@app.route('/block', methods=['GET'])
def get_block():
    id = request.args.get('id')
    wantedBlock = blockchain.get_block(id)
    response = jsonBlock(
        wantedBlock) if wantedBlock.__len__ > 0 else 'No block was found'

    return response, 200


@app.route('/chain', methods=['GET'])
def display_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Check validity of blockchain


@app.route('/valid', methods=['GET'])
def valid():
    valid = blockchain.chain_valid(blockchain.chain)

    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200


# Run the flask server locally
app.run(host='127.0.0.1', port=5000)
