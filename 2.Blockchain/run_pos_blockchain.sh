#!/bin/bash

# Matar procesos Python en ejecución (para evitar conflictos)
pkill python

# Iniciar nodo en el puerto 5000
python pos_blockchain.py -p 5000 &
sleep 3

# Añadir validador Alice con stake de 50
curl -X POST -H "Content-Type: application/json" -d '{"address": "Alice", "stake": 50}' http://localhost:5000/validators/add

# Añadir validador Bob con stake de 30
curl -X POST -H "Content-Type: application/json" -d '{"address": "Bob", "stake": 30}' http://localhost:5000/validators/add

# Crear una transacción de Alice a Bob con 10 unidades
curl -X POST -H "Content-Type: application/json" -d '{"sender": "Alice", "recipient": "Bob", "amount": 10, "order": 1}' http://localhost:5000/transactions/new

# Minar un bloque seleccionará un validador basado en su stake y lo recompensará
curl http://localhost:5000/mine

# Consulta la cadena completa para ver los bloques y las transacciones:
curl http://localhost:5000/chain

# Consulta los validadores registrados y sus stakes:
curl http://localhost:5000/validators