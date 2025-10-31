Como executar o codigo manualmente:

python3 -m venv venv
source venv/bin/activate

terminal 1(Servidor)
python3 printer_server.py

terminal 2(cliente 1)
python3 printing_client.py --id 1 --server localhost:50051 --port 50052 --clients localhost:50053,localhost:50054

terminal 3(cliente 2)
python3 printing_client.py --id 2 --server localhost:50051 --port 50053 --clients localhost:50052,localhost:50054

terminal 4(cliente 3)
python3 printing_client.py --id 3 --server localhost:50051 --port 50054 --clients localhost:50052,localhost:50053
