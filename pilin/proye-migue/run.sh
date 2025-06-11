#!/bin/bash

ARCHIVO_ENCRIPTADO="credenciales.enc"
ROJO='\033[0;31m'
AMARILLO='\033[0;33m'
SIN_COLOR='\033[0m'

limpiar() {
    unset contrasena
    unset CONTENIDO_ENV
    unset MYSQL_PWD
    history -c
}

if [ ! -f "$ARCHIVO_ENCRIPTADO" ]; then
    echo -e "${ROJO}Error: No se encuentra $ARCHIVO_ENCRIPTADO${SIN_COLOR}"
    echo "Primero crea tu archivo credenciales.env y luego encríptalo con:"
    echo -e "${AMARILLO}openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -in credenciales.env -out credenciales.enc${SIN_COLOR}"
    echo "Luego elimina el archivo original:"
    echo -e "${AMARILLO}rm credenciales.env${SIN_COLOR}"
    exit 1
fi

# Leer contraseña de forma segura
stty -echo
printf "Contraseña para desencriptar $ARCHIVO_ENCRIPTADO: "
read -r contrasena
stty echo
printf "\n"

# Desencriptar en memoria y cargar variables
if ! CONTENIDO_ENV=$(openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt \
    -in "$ARCHIVO_ENCRIPTADO" -pass pass:"$contrasena" 2>/dev/null); then
    echo -e "${ROJO}Error: Contraseña incorrecta o archivo corrupto${SIN_COLOR}"
    limpiar
    exit 1
fi

# Limpiar contraseña inmediatamente después de usarla
unset contrasena

# Procesar contenido y exportar variables
while IFS= read -r linea; do
    [[ -z "$linea" || "$linea" =~ ^\s*# ]] && continue  # Saltar líneas vacías/comentarios
    
    # Eliminar espacios alrededor del igual y comillas
    clave_valor=$(echo "$linea" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^export[[:space:]]*//')
    clave="${clave_valor%%=*}"
    valor="${clave_valor#*=}"
    echo $clave
    echo $valor
    
    # Eliminar comillas circundantes si existen
    valor=$(echo "$valor" | sed -e "s/^['\"]//" -e "s/['\"]$//")
    
    # Exportar variable de entorno
    export "$clave"="$valor"
done <<< "$CONTENIDO_ENV"

# Verificar si se cargaron variables
if [ -z "$(env | grep -E 'SECRET_KEY|DB_')" ]; then
    echo -e "${ROJO}Error: No se encontraron variables válidas en el archivo${SIN_COLOR}"
    limpiar
    exit 1
fi

# Limpiar el contenido desencriptado de memoria
unset CONTENIDO_ENV

# Ejecutar Docker Compose con las variables cargadas
docker-compose down -v
docker-compose up --build
docker-compose up

# Limpieza final al terminar
#limpiar
