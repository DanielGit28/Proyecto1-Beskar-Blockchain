# Project to create a private Blockchain for storing and generating unique ids by dna parameters

# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To store data
# in our blockchain
import json
import time

# Flask is for creating the web
# app and jsonify is for
# displaying the blockchain
from flask import Flask, jsonify, request
import uuid
import hashlib


class Block:
    def __init__(self, index, timestamp, previous_hash, data, proof=0):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.data = data
        self.proof = proof
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    def __str__(self):
        return jsonify({
				'index': self.index,
				'timestamp': self.timestamp,
				'proof': self.nonce,
                'data': self.data,
				'previous_hash': self.previous_hash})
    
class DNA:

    def __init__(self, chromosomes, nucleotides, genes, codons):
        self.chromosomes = chromosomes
        self.nucleotides = nucleotides
        self.genes = genes
        self.codons = codons

    def __str__(self):
        return f"DNA(chromosomes={self.chromosomes}, nucleotides={self.nucleotides}, genes={self.genes}, codons={self.codons})"
    

class Blockchain:
    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        self.chain = []
        self.create_block(1,"0",DNA(0,0,0,0))

    # This function is created
    # to add further blocks
    # into the chain
    def create_block(self, proof, previous_hash, dna):
        block = Block(len(self.chain) + 1, time.time(),previous_hash, unique_id(dna), proof)
        self.chain.append(block.toJSON())
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
        return [x for x in self.chain if json.loads(x).get('data') == id]

    def chain_valid(self, chain):
        previous_block = json.loads(chain[0])
        block_index = 1

        while block_index < len(chain):
            block = json.loads(chain[block_index])
            
            if block.get('previous_hash') != self.hash(previous_block):
                return False

            previous_proof = previous_block.get('proof')
            proof = block.get('proof')
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
    dnaV = str(dna.chromosomes) + str(dna.nucleotides) + str(dna.genes) + str(dna.codons) if dna else '0'
    id = uuid.uuid4().hex + dnaV
    return id


# Creating the Web
# App using flask
app = Flask(__name__)

# Create the object
# of the class blockchain
blockchain = Blockchain()


#example: /mine_block?chromosomes=23&nucleotides=500&genes=1300&codons=120450
@app.route('/mine_block', methods=['GET'])
def mine_block():
    dna = DNA(request.args.get('chromosomes'),request.args.get('nucleotides'),request.args.get('genes'),request.args.get('codons'))
    previous_block = json.loads(blockchain.print_previous_block())
    previous_proof = previous_block.get('proof')
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash, dna)
    

    return block.toJSON(), 200

# Display blockchain in json format


@app.route('/block', methods=['GET'])
def get_block():
    id = request.args.get('id')
    wantedBlock = blockchain.get_block(id)
    response = wantedBlock[0] if len(wantedBlock) > 0 else 'No block was found'

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
