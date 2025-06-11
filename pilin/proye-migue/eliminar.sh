#!/bin/bash

# Verifica si hay contenedores
if [ "$(docker ps -aq)" ]; then
    echo "Eliminando todos los contenedores de Docker..."
    docker rm -f $(docker ps -aq)
    echo "Todos los contenedores han sido eliminados."
else
    echo "No hay contenedores para eliminar."
fi

