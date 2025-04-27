#!/bin/bash

# Configuración
ENCRYPTED_FILE="credenciales.enc"
LOG_FILE="django_run.log"

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para limpieza segura
cleanup() {
    unset password
    unset ENV_CONTENT
    unset MYSQL_PWD
    history -c
    clear
}

# Verificar archivo encriptado
if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo -e "${RED}Error: No se encuentra $ENCRYPTED_FILE${NC}"
    echo "Primero crea tu archivo credenciales.env y luego encriptalo con:"
    echo -e "${YELLOW}openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -in credenciales.env -out credenciales.enc${NC}"
    echo "Luego elimina el archivo original:"
    echo -e "${YELLOW}rm credenciales.env${NC}"
    exit 1
fi

# Solicitar contraseña de forma segura
stty -echo
printf "🔐 Contraseña para desencriptar credenciales.enc: "
read password
stty echo
printf "\n"

# Desencriptar a memoria
ENV_CONTENT=$(openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 -salt \
              -in "$ENCRYPTED_FILE" -pass pass:"$password" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "\n${RED}❌ Error: Contraseña incorrecta o archivo corrupto${NC}"
    cleanup
    exit 1
fi

# Cargar variables
eval "$(echo "$ENV_CONTENT" | grep -v '^#' | grep '=' | sed 's/^/export /')"

# Configuración especial para MySQL
export MYSQL_PWD="${DB_PASSWORD}"

# Verificar variables requeridas
REQUIRED_VARS=("SECRET_KEY" "DB_NAME" "DB_USER" "DB_PASSWORD")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Error: La variable $var no está configurada${NC}"
        cleanup
        exit 1
    fi
done

# Limpieza de credenciales
cleanup

# Mensaje de inicio
echo -e "\n${GREEN}✅ Credenciales cargadas correctamente${NC}"
echo -e "${YELLOW}⚡ Iniciando servidor Django con MySQL...${NC}"
echo -e "📝 Registros guardados en: $LOG_FILE"
echo -e "${YELLOW}🛑 Presiona Ctrl+C para detener el servidor${NC}\n"

# Función para manejar la señal de salida
trap 'echo -e "\n${RED}✋ Servidor detenido${NC}"; exit 0' INT

# Ejecutar el servidor y guardar logs
python3 manage.py runserver 0.0.0.0:8000

# Mensaje final
echo -e "\n${GREEN}✔ Servidor detenido correctamente${NC}"
