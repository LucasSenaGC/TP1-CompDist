import grpc
from concurrent import futures
import time

# import dos arquivos que o print.proto gerou
import print_pb2
import print_pb2_grpc

# PrintingService
class PrintingServiceServicer(print_pb2_grpc.PrintingServiceServicer):
    
    def SendToPrinter(self, request, context):
        
        print(f"[TS: {request.lamport_timestamp}] CLIENTE {request.client_id} (Req N° {request.request_number}): {request.message_content}")
        
        # Pra simular o tempo de impressão (Seção Crítica)
        try:
            print("... Impressora ocupada imprimindo ...")
            time.sleep(2) 
            print("... Impressão concluída.")
            confirmation_msg = f"Servidor burro confirma: Impressão da req N° {request.request_number} do Cliente {request.client_id} concluída."
            success_status = True
            
        except Exception as e:
            print(f"Erro durante a impressão: {e}")
            confirmation_msg = "Falha na impressão."
            success_status = False

        # Retorna a confirmação para o cliente
        return print_pb2.PrintResponse(
            success=success_status,
            confirmation_message=confirmation_msg,
            lamport_timestamp=request.lamport_timestamp 
        )

def serve():
    # Fazer as threads para lidar com requisições
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    print_pb2_grpc.add_PrintingServiceServicer_to_server(
        PrintingServiceServicer(), server
    )
    
    port = "50051"
    server.add_insecure_port(f"[::]:{port}")
    print(f"--- Servidor de Impressão 'Burro' iniciado na porta {port} ---")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Servidor desligando...")
        server.stop(0)

if __name__ == "__main__":
    serve()