const express = require('express');
const fs = require('fs'); // Para leer/escribir archivos
const path = require('path');

const app = express();
const port = 8080;

app.use(express.json());

// PATH  del archivo de datos
const DATA_FILE = path.join(__dirname, 'rentals.json');

// Crear el archivo de datos si no existe
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, '[]', 'utf-8');
  }
  
// Endpoint para registrar un nuevo pedido de alquiler
app.post('/rentals', (req, res) => {
  const { carMaker, carModel, days, units } = req.body;

  if (!carMaker || !carModel || !days || !units) {
    return res.status(400).json({ error: 'Todos los campos son obligatorios: carMaker, carModel, days, units' });
  }

  if (typeof days !== 'number' || typeof units !== 'number' || days <= 0 || units <= 0) {
    return res.status(400).json({ error: 'Los campos "days" y "units" deben ser números positivos mayores que 0' });
  }

  const rentals = JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));

  const newRental = {
    id: rentals.length + 1,
    carMaker,
    carModel,
    days,
    units,
  };

  rentals.push(newRental);
  fs.writeFileSync(DATA_FILE, JSON.stringify(rentals, null, 2));

  res.status(201).json({ message: 'Pedido de alquiler registrado correctamente', rental: newRental });
});

// Endpoint para listar todos los pedidos de alquiler
app.get('/rentals', (req, res) => {
  const rentals = JSON.parse(fs.readFileSync(DATA_FILE, 'utf-8'));
  res.json(rentals);
});

app.listen(port, () => {
  console.log(`API de alquiler de coches escuchando en http://localhost:${port}`);
});