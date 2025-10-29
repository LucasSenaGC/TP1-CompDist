import grpc
from concurrent import futures
import time
import random
import threading
import argparse 

# import dos arquivos que o print.proto gerou(printProto usado foi o que o professor deixou de SUGESTÃO)
import print_pb2
import print_pb2_grpc

# Exclusão Mútua (pra escutar outros clientes)
class MutualExclusionServicer(print_pb2_grpc.MutualExclusionServiceServicer):
    
    # Construtor para dar acesso ao estado do cliente principal
    def __init__(self, client_id, shared_state):
        self.client_id = client_id
        self.shared_state = shared_state 
        self.lock = self.shared_state["state_cv"] 

        # so pra testar se esta funcionando
        print(f"[Servidor do Cliente {self.client_id}] Servicer de exclusão mútua inicializado.")

    # RequestAccess (quando outro cliente pede acesso)
    def RequestAccess(self, request, context):
        
        with self.lock:
            
            # Atualizar Relógio de Lamport 
            # Regra 3 -> Ao receber uma mensagem (m, t), o processo Pj calcula Cj := max(Cj, t) + 1 e então entrega a mensagem à aplicação
            self.shared_state["clock"] = max(self.shared_state["clock"], request.lamport_timestamp) + 1
            print(f"[Servidor {self.client_id}] Recebeu RequestAccess de {request.client_id} [TS Req: {request.lamport_timestamp}, Meu Relógio: {self.shared_state['clock']}]")

            #Lógica de Ricart-Agrawala
            
            # Pega os estados atuais para tomar a decisão
            my_state = self.shared_state["state"]
            my_ts = self.shared_state["request_ts"]
            
            # Olhar a prioridade -> quem tem o menor timestamp se o timestamp for igual eu olho o menor ID
            i_have_priority = (my_ts, self.client_id) < (request.lamport_timestamp, request.client_id)
            
            # CONDIÇÃO DE ESPERA:
            # Eu devo esperar para responder (DEFER) se:
            # Eu estou na Seção Crítica (HELD)
            # Ou eu QUERO entrar (WANTED) e eu tenho prioridade
            while my_state == "HELD" or (my_state == "WANTED" and i_have_priority):
                
                print(f"[Servidor {self.client_id}] DEFERINDO pedido de {request.client_id} (Meu Estado: {my_state}, Minha Prioridade: {i_have_priority})")
                
                # libera o lock e espera ser notificado
                self.lock.wait() 
                
                # Quando acordar (notificado)
                print(f"[Servidor {self.client_id}] Fui notificado! Re-avaliando pedido de {request.client_id}...")
                my_state = self.shared_state["state"]
                my_ts = self.shared_state["request_ts"]
                i_have_priority = (my_ts, self.client_id) < (request.lamport_timestamp, request.client_id)

            # Como o loop acabou agora eu posso responder
            print(f"[Servidor {self.client_id}] RESPONDENDO OK para {request.client_id}")

            #Regra 1 -> Antes de executar um evento, Pi executa Ci := Ci + 1.
            self.shared_state["clock"] += 1
            
            #Regra 2 -> Quando o processo Pi envia uma mensagem m, ele anexa a essa mensagem o timestamp t = Ci.
            return print_pb2.AccessResponse(
                access_granted=True, 
                lamport_timestamp=self.shared_state["clock"]
            )
            
    # Implementação de ReleaseAccess
    def ReleaseAccess(self, request, context):
        #Atualizar Relógio de Lamport
        with self.lock:
            self.shared_state["clock"] = max(self.shared_state["clock"], request.lamport_timestamp) + 1

        print(f"[Servidor do Cliente {self.client_id}] Recebeu ReleaseAccess de {request.client_id} (Meu Relógio agora é {self.shared_state['clock']})")
        
        return print_pb2.Empty()


# Função para rodar o SERVIDOR gRPC do cliente em uma thread separada
def run_client_server(servicer, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    print_pb2_grpc.add_MutualExclusionServiceServicer_to_server(
        servicer, server
    )
    server.add_insecure_port(f"[::]:{port}")
    print(f"[Servidor do Cliente] Ouvindo na porta {port}...")
    server.start()
    server.wait_for_termination()


def main():
    parser = argparse.ArgumentParser(description="Cliente de Impressão Distribuída")
    parser.add_argument("--id", type=int, required=True, help="ID único do cliente")
    parser.add_argument("--port", type=str, required=True, help="Porta para este cliente OUVIR")
    parser.add_argument("--server", type=str, required=True, help="Endereço do servidor de impressão burro (ex: localhost:50051)")
    parser.add_argument("--clients", type=str, required=True, help="Lista de endereços dos OUTROS clientes (separados por vírgula, ex: localhost:50053,localhost:50054)")
    
    args = parser.parse_args()

    client_id = args.id
    client_port = args.port
    printer_server_address = args.server
    other_clients_addresses = args.clients.split(',')
    
    lock = threading.Lock()
    state_cv = threading.Condition(lock)

    # Dicionario compartilhado pra que as threads do main e do servicer possam acessar
    shared_state = {
        "clock": 0,
        "state": "RELEASED", # Estados possiveis: RELEASED, WANTED, HELD
        "request_ts": 0,
        "deferred_queue": [],
        "state_cv": state_cv
    }
    
    #Iniciar a THREAD do SERVIDOR (para ouvir outros clientes)
    servicer = MutualExclusionServicer(
        client_id, shared_state
    )
    
    server_thread = threading.Thread(
        target=run_client_server, 
        args=(servicer, client_port),
        daemon=True
    )
    server_thread.start()
    
    # Conexão com o servidor de impressão
    printer_channel = grpc.insecure_channel(printer_server_address)
    printer_stub = print_pb2_grpc.PrintingServiceStub(printer_channel)
    
    # Conexões com os outros clientes
    client_stubs = {}
    for addr in other_clients_addresses:
        channel = grpc.insecure_channel(addr)
        client_stubs[addr] = print_pb2_grpc.MutualExclusionServiceStub(channel)
        
    print(f"--- Cliente {client_id} (Porta {client_port}) INICIADO ---")
    print(f"Conectado ao Servidor Burro em {printer_server_address}")
    print(f"Conectado aos outros clientes em {other_clients_addresses}")
    time.sleep(3) 

    request_num = 0
    while True:
        try:
            # simular um pedido de impressão
            time.sleep(random.uniform(3, 8))
            
            print(f"\n[Cliente {client_id}] ------------------------------------------")
            print(f"[Cliente {client_id}] QUERO IMPRIMIR (Req N° {request_num})")
            
            # --- INÍCIO DA SEÇÃO CRÍTICA ---
            
            cv = shared_state["state_cv"]
            
            # Mudar estado para WANTED
            with cv:
                # Atualizar Relógio de Lamport com a Regra 1(Antes de executar um evento, Pi executa Ci := Ci + 1.)
                shared_state["clock"] += 1
                shared_state["request_ts"] = shared_state["clock"]
                # Vira Wanted
                shared_state["state"] = "WANTED"
                
                print(f"[Cliente {client_id}] Estado -> WANTED (Meu TS: {shared_state['request_ts']})")
            
            # Pedir permissão pra todo mundo        
            replies_ok = 0
            for addr, stub in client_stubs.items():
                try:
                    print(f"[Cliente {client_id}] Pedindo acesso para {addr}...")
                    
                    # Prepara a mensagem de requisição
                    request_msg = print_pb2.AccessRequest(
                        client_id=client_id,
                        lamport_timestamp=shared_state["request_ts"],
                        request_number=request_num
                    )
                    
                    response = stub.RequestAccess(request_msg)
                    
                    # Processa a resposta DENTRO do lock
                    with cv:
                        # Atualizar relógio com a resposta 
                        # Regra 3 -> Ao receber uma mensagem (m, t), o processo Pj calcula Cj := max(Cj, t) + 1 e então entrega a mensagem à aplicação.
                        shared_state["clock"] = max(shared_state["clock"], response.lamport_timestamp) + 1
                        replies_ok += 1
                        print(f"[Cliente {client_id}] Recebeu OK de {addr} ({replies_ok}/{len(client_stubs)}). (Meu Relógio: {shared_state['clock']})")
                        
                except grpc.RpcError as e:
                    print(f"[Cliente {client_id}] Erro ao contatar cliente {addr}: {e.details()}")

            # agora eh HELD e posso imprimir
            with cv:
                shared_state["state"] = "HELD"
                print(f"[Cliente {client_id}] *** Estado -> HELD. Entrando na Seção Crítica ***")
            
            # === SEÇÃO CRÍTICA ===
            try:
                print(f"[Cliente {client_id}] *** Enviando para a Impressora... ***")
                msg_content = f"Este é o pedido {request_num} do cliente {client_id}."
                
                response = printer_stub.SendToPrinter(
                    print_pb2.PrintRequest(
                        client_id=client_id,
                        message_content=msg_content,
                        lamport_timestamp=shared_state["request_ts"],
                        request_number=request_num
                    )
                )
                print(f"[Cliente {client_id}] *** Resposta da Impressora: '{response.confirmation_message}' ***")
            
            except Exception as e:
                print(f"[Cliente {client_id}] *** Erro na Seção Crítica: {e} ***")
            # === FIM DA SEÇÃO CRÍTICA ===


            # Vira release e tenho que avisar
            with cv:
                shared_state["state"] = "RELEASED"
                cv.notify_all() 
                print(f"[Cliente {client_id}] *** Estado -> RELEASED. Notificando todos. ***")
            
            # --- FIM DA SEÇÃO CRÍTICA ---
            
            request_num += 1

        except KeyboardInterrupt:
            print(f"Cliente {client_id} desligando...")
            break
        except Exception as e:
            print(f"Erro GERAL no cliente {client_id}: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()