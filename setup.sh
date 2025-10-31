#!/bin/bash

# --- Início do Script de Configuração ---

# 0. Definir cores para os logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

echo -e "${GREEN}--- Iniciando Script de Configuração Completa ---${NC}"

# 1. Instalar dependências do sistema (apt)
echo -e "\n${YELLOW}Passo 1: Instalando pacotes do sistema (python3-venv, python3-pip)...${NC}"
echo "Você precisará digitar sua senha (sudo):"
sudo apt update
sudo apt install -y python3-venv python3-pip
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao instalar pacotes do sistema. Abortando.${NC}"
    exit 1
fi
echo -e "${GREEN}Dependências do sistema instaladas!${NC}"


# 2. Detectar comando Python correto (python vs python3)
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Comando 'python3' não encontrado. Procurando por 'python'...${NC}"
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Nenhum comando 'python' ou 'python3' encontrado. Abortando.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}Usando o comando: ${PYTHON_CMD}${NC}"


# 3. Criar Ambiente Virtual (venv)
echo -e "\n${YELLOW}Passo 2: Criando ambiente virtual 'venv'...${NC}"
$PYTHON_CMD -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao criar o ambiente virtual. Abortando.${NC}"
    exit 1
fi
echo -e "${GREEN}Ambiente virtual criado!${NC}"


# 4. Instalar dependências Python (via pip)
echo -e "\n${YELLOW}Passo 3: Instalando grpcio e grpcio-tools...${NC}"
# Usamos o pip de dentro do venv diretamente para mais robustez
./venv/bin/pip install grpcio grpcio-tools
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao instalar pacotes Python. Abortando.${NC}"
    exit 1
fi
echo -e "${GREEN}Dependências Python instaladas!${NC}"


# 5. Gerar código gRPC
echo -e "\n${YELLOW}Passo 4: Gerando código gRPC a partir de print.proto...${NC}"
if [ ! -f print.proto ]; then
    echo -e "${RED}Arquivo 'print.proto' não encontrado! Abortando.${NC}"
    exit 1
fi
# Usamos o python de dentro do venv
./venv/bin/python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. print.proto
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao gerar código gRPC. Verifique seu arquivo .proto.${NC}"
    exit 1
fi
echo -e "${GREEN}Código gRPC gerado (print_pb2.py e print_pb2_grpc.py)!${NC}"


# 6. Criar Scripts de Execução
echo -e "\n${YELLOW}Passo 5: Criando scripts de execução...${NC}"

# Script do Servidor
cat << EOF > iniciar_servidor.sh
#!/bin/bash
# Script para iniciar o Servidor de Impressão "Burro"
echo "--- Ativando venv e iniciando Servidor (Terminal 1) ---"
source venv/bin/activate
$PYTHON_CMD printer_server.py
EOF

# Script Cliente 1
cat << EOF > iniciar_cliente1.sh
#!/bin/bash
# Script para iniciar o Cliente 1
echo "--- Ativando venv e iniciando Cliente 1 (Terminal 2) ---"
source venv/bin/activate
$PYTHON_CMD printing_client.py --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054
EOF

# Script Cliente 2
cat << EOF > iniciar_cliente2.sh
#!/bin/bash
# Script para iniciar o Cliente 2
echo "--- Ativando venv e iniciando Cliente 2 (Terminal 3) ---"
source venv/bin/activate
$PYTHON_CMD printing_client.py --id 2 --server localhost:50051 --port 50053 --clients localhost:50052,localhost:50054
EOF

# Script Cliente 3
cat << EOF > iniciar_cliente3.sh
#!/bin/bash
# Script para iniciar o Cliente 3
echo "--- Ativando venv e iniciando Cliente 3 (Terminal 4) ---"
source venv/bin/activate
$PYTHON_CMD printing_client.py --id 3 --server localhost:50051 --port 50054 --clients localhost:50052,localhost:50053
EOF

echo -e "${GREEN}Scripts de execução criados!${NC}"


# 7. Tornar Scripts Executáveis
echo -e "\n${YELLOW}Passo 6: Tornando scripts executáveis...${NC}"
chmod +x iniciar_servidor.sh iniciar_cliente1.sh iniciar_cliente2.sh iniciar_cliente3.sh


# --- Fim ---
echo -e "\n${GREEN}--- SUCESSO! Configuração concluída! ---${NC}"
echo -e "O que fazer agora:"
echo "1. Abra 4 terminais."
echo "2. Em cada terminal, execute um dos novos scripts:"
echo -e "   - ${YELLOW}Terminal 1:${NC} ./iniciar_servidor.sh"
echo -e "   - ${YELLOW}Terminal 2:${NC} ./iniciar_cliente1.sh"
echo -e "   - ${YELLOW}Terminal 3:${NC} ./iniciar_cliente2.sh"
echo -e "   - ${YELLOW}Terminal 4:${NC} ./iniciar_cliente3.sh"
echo -e "3. Para parar, pressione Ctrl+C em todos os terminais."