## Configuração do Ambiente

1.  **Instalar pacotes de sistema (Linux/WSL):**
    ```bash
    sudo apt update
    sudo apt install python3-venv python3-pip
    ```

2.  **Criar o Ambiente Virtual:**
    ```bash
    python3 -m venv venv
    ```

3.  **Ativar o Ambiente Virtual:**
    ```bash
    source venv/bin/activate
    ```

4.  **Instalar Dependências Python (com o venv ativo):**
    ```bash
    pip install grpcio grpcio-tools
    ```

5.  **Gerar Código gRPC:**
    Verifique se o arquivo `print.proto` está no diretório e execute:
    ```bash
    python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. print.proto
    ```
---

## Como Executar Manualmente

Para executar o sistema, você precisará de **4 terminais** abertos no diretório do projeto.

**Importante:** Em *cada um* dos 4 terminais ative o ambiente virtual:
```bash
source venv/bin/activate
Depois, execute os seguintes comandos, um em cada terminal:

Terminal 1: Servidor "Burro"
```Bash

python3 printer_server.py
```

Terminal 2: Cliente 1
(Ouve na 50052, conecta na 50053 e 50054)

```Bash

python3 printing_client.py --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054
```

Terminal 3: Cliente 2
(Ouve na 50053, conecta na 50052 e 50054)

```Bash

python3 printing_client.py --id 2 --server localhost:50051 --port 50053 --clients localhost:50052,localhost:50054
```
Terminal 4: Cliente 3
(Ouve na 50054, conecta na 50052 e 50053)

```Bash

python3 printing_client.py --id 3 --server localhost:50051 --port 50054 --clients localhost:50052,localhost:50053
```
Obs importante: Se o seu sistema usa python em vez de python3, substitua o comando em todas as linhas.


## Execução com Scripts

Tornar o script executável:

```Bash
chmod +x setup.sh
```
Executar o script:

```Bash
./setup.sh
```
Após a conclusão, siga as instruções do script para abrir os 4 terminais e usar os scripts gerados (ex: ./iniciar_servidor.sh, ./iniciar_cliente1.sh, etc.).
