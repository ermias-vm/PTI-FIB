#!/bin/bash

# Matar procesos Python en ejecución (para evitar conflictos)
pkill python

# Iniciar dos nodos en los puertos 5000 y 5001
python blockchain.py -p 5000 &
python blockchain.py -p 5001 &

# Esperar a que los nodos se inicien
sleep 3

# Agregar dos transacciones al nodo 1
curl -X POST -H "Content-Type: application/json" -d '{"sender": "A","recipient": "B", "amount": 8, "order": 1}' http://localhost:5000/transactions/new
curl -X POST -H "Content-Type: application/json" -d '{"sender": "B","recipient": "C", "amount": 5, "order": 2}' http://localhost:5000/transactions/new

# Minar 3 bloques en el nodo 1
curl http://localhost:5000/mine
#curl http://localhost:5000/chain
curl http://localhost:5000/mine
#curl http://localhost:5000/chain
curl http://localhost:5000/mine
#curl http://localhost:5000/chain

# Minar 2 bloques en el nodo 2
curl http://localhost:5001/mine
curl http://localhost:5001/mine
#curl http://localhost:5001/chain

# Registrar nodos entre sí
curl -X POST -H "Content-Type: application/json" -d '{"nodes":"http://localhost:5001"}' http://localhost:5000/nodes/register
curl -X POST -H "Content-Type: application/json" -d '{"nodes":"http://localhost:5000"}' http://localhost:5001/nodes/register

# Sincronizar la blockchain entre los nodos
curl http://localhost:5000/nodes/resolve
curl http://localhost:5001/nodes/resolve