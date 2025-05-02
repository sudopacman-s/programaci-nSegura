#!/bin/bash

ARCHIVO_ENCRIPTADO="credenciales.enc"
ARCHIVO_LOG="django_run.log"

ROJO='\033[0;31m'
VERDE='\033[0;32m'
AMARILLO='\033[1;33m'
SIN_COLOR='\033[0m'

limpiar() {
    unset contrasena
    unset CONTENIDO_ENV
    unset MYSQL_PWD
    history -c
    clear
}

if [ ! -f "$ARCHIVO_ENCRIPTADO" ]; then
    echo -e "${ROJO}Error: No se encuentra $ARCHIVO_ENCRIPTADO${SIN_COLOR}"
    echo "Primero crea tu archivo credenciales.env y luego encríptalo con:"
    echo -e "${AMARILLO}openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -in credenciales.env -out credenciales.enc${SIN_COLOR}"
    echo "Luego elimina el archivo original:"
    echo -e "${AMARILLO}rm credenciales.env${SIN_COLOR}"
    exit 1
fi

stty -echo
printf "Contraseña para desencriptar credenciales.enc: "
read contrasena
stty echo
printf "\n"

CONTENIDO_ENV=$(openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt \
              -in "$ARCHIVO_ENCRIPTADO" -pass pass:"$contrasena" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "\n${ROJO}Error: Contraseña incorrecta o archivo dañado${SIN_COLOR}"
    limpiar
    exit 1
fi

eval "$(echo "$CONTENIDO_ENV" | grep -v '^#' | grep '=' | sed 's/^/export /')"

export MYSQL_PWD="${DB_PASSWORD}"

VARIABLES_REQUERIDAS=("SECRET_KEY" "DB_NAME" "DB_USER" "DB_PASSWORD")
for variable in "${VARIABLES_REQUERIDAS[@]}"; do
    if [ -z "${!variable}" ]; then
        echo -e "${ROJO}Error: La variable $variable no está configurada${SIN_COLOR}"
        limpiar
        exit 1
    fi
done

#limpiar

echo -e "\n${VERDE}Credenciales cargadas correctamente${SIN_COLOR}"
echo -e "${AMARILLO}Iniciando servidor Django con MySQL...${SIN_COLOR}"
echo -e "Registros guardados en: $ARCHIVO_LOG"
echo -e "${AMARILLO}Presiona Ctrl+C para detener el servidor${SIN_COLOR}\n"

trap 'echo -e "\n${ROJO}Servidor detenido${SIN_COLOR}"; exit 0' INT

python3 manage.py runserver 0.0.0.0:8000

echo -e "\n${VERDE}Servidor detenido correctamente${SIN_COLOR}"

