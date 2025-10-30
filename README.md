# COMANDOS PARA RODAR O CÓDIGO
Executar o codigo:
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


# ENUNCIADO DO TRABALHO

Objetivo
Implementar um sistema distribuído onde múltiplos processos clientes disputam o acesso exclusivo a um recurso compartilhado (um servidor de impressão “burro”), utilizando:

1. gRPC para comunicação entre processos

2. Algoritmo de Ricart-Agrawala para exclusão mútua distribuída

3. Relógios Lógicos de Lamport para sincronização e ordenação de eventos

Contextualização
Você deve desenvolver um sistema de impressão distribuído onde múltiplos clientes (processos em terminais diferentes) precisam enviar documentos para um servidor central de impressão.

IMPORTANTE: O servidor de impressão é “burro”: ele não participa do algoritmo de exclusão mútua. Sua única função é:

Receber requisições de impressão via gRPC
Imprimir as mensagens na tela (com ID do cliente e timestamp)
Aguardar um delay para simular o tempo de impressão
Responder com confirmação para o cliente solicitante
Toda a coordenação para exclusão mútua deve ser realizada exclusivamente entre os processos clientes, que precisam atuar como:

Clientes gRPC: Para enviar mensagens para o servidor de impressão e para outros clientes
Servidores gRPC: Para receber e responder mensagens de outros clientes
Requisitos Técnicos
1. Arquitetura do Sistema
Servidor de Impressão “Burro” (Porta 50051):

Executado em um terminal separado na porta 50051
Aguarda passivamente por conexões
Ao receber mensagem via SendToPrinter, imprime e retorna confirmação
Não tem conhecimento sobre a existência de outros clientes
NÃO participa do algoritmo de exclusão mútua
NÃO conhece outros clientes
Clientes Inteligentes (Portas 50052, 50053, 50054, …):

Implementam algoritmo completo de Ricart-Agrawala
Mantêm relógios lógicos de Lamport atualizados
Geram requisições automáticas de impressão
Exibem status local em tempo real
2. Protocolo .proto SUGERIDO
syntax = "proto3";

package distributed_printing;

// Serviço para o servidor de impressão BURRO (implementado no servidor)
service PrintingService {
  rpc SendToPrinter (PrintRequest) returns (PrintResponse);
}

// Serviço para comunicação entre CLIENTES (implementado nos clientes)
service MutualExclusionService {
  rpc RequestAccess (AccessRequest) returns (AccessResponse);
  rpc ReleaseAccess (AccessRelease) returns ();
}

// Mensagens para impressão (cliente -> servidor burro)
message PrintRequest {
  int32 client_id = 1;
  string message_content = 2;
  int64 lamport_timestamp = 3;
  int32 request_number = 4;
}

message PrintResponse {
  bool success = 1;
  string confirmation_message = 2;
  int64 lamport_timestamp = 3;
}

// Mensagens para exclusão mútua (cliente <-> cliente)
message AccessRequest {
  int32 client_id = 1;
  int64 lamport_timestamp = 2;
  int32 request_number = 3;
}

message AccessResponse {
  bool access_granted = 1;
  int64 lamport_timestamp = 2;
}

message AccessRelease {
  int32 client_id = 1;
  int64 lamport_timestamp = 2;
  int32 request_number = 3;
}
Observe que o protocolo acima é uma SUGESTÃO. Grupos que optarem por modificar o formato das mensagens/serviços oferecidos precisam seguir uma lógica semelhante que seja funcional para o algoritmo. Caso tenham dúvidas, entrem em contato com o professor.

3. Funcionamento do Sistema
Servidor de Impressão (Burro):

Implementa apenas o serviço PrintingService
Recebe requisições de impressão via SendToPrinter
Imprime mensagens no formato: [TS: {timestamp}] CLIENTE {id}: {mensagem}
Simula tempo de impressão com delay de 2-3 segundos
Retorna confirmação de impressão
NÃO implementa MutualExclusionService
Clientes (Inteligentes):

Cada cliente executa em terminal separado (portas 50052, 50053, 50054, …)
Implementam MutualExclusionService (como servidores)
Usam PrintingService do servidor burro (como clientes)
Usam MutualExclusionService de outros clientes (como clientes)
Implementam algoritmo de Ricart-Agrawala
Mantêm relógio lógico de Lamport atualizado
Geram pedidos de impressão automaticamente em intervalos aleatórios
Exibem status local em tempo real
NÃO implementam PrintingService
4. Linguagens de Programação
gRPC está disponível para várias linguagens, como C#/.NET, C++, Dart, Go, Java, Node, Python, etc. Cada grupo pode escolher sua linguagem de preferência para utilização no trabalho.   