# Usar una imagen base de Node.js
FROM node:14

# Crear el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copiar los archivos package.json y package-lock.json (si existe)
COPY package*.json ./

# Instalar las dependencias
RUN npm install

# Copiar el resto de los archivos de la aplicación
COPY . .

# Comando para ejecutar la aplicación
CMD ["node", "server.js"]