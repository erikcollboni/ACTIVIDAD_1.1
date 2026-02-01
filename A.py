import socket
import threading
import time
import random
import datetime

# Configuración
RESPONDER_PORTS = [5001, 5002, 5003]
REQUESTER_PORT = 5000
N_PERIODS = 3
BUFFER_SIZE = 32

# Códigos ANSI
ITALIC = "\033[3m"
BOLD    = "\033[1m"
RESET = "\033[0m"

# Colores de texto
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"  
ORANGE  = "\033[38;5;208m"  # Naranja intenso

RESPONDERS_COLORS = [ORANGE, YELLOW, MAGENTA]
REQUESTER_COLOR = BLUE

"""
Agente que responde a la solicitud de ayuda con un Ok, No o silencio.

La variable port indica el puerto en el que escucha cada agente y es importante puesto que se 
están simulando múltiples agentes en la misma máquina.
"""
def responder_agent(agent_id, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM para UDP
    sock.bind((socket.gethostname(), port))
    
    color_code = RESPONDERS_COLORS[agent_id - 1]
    print(f"{color_code}[Agente {agent_id}]\tListo en puerto {port}{RESET}")

    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        message = data.decode('utf-8')

        # Verificamos si es una solicitud válida del tipo "#NeedSupport_X"
        if message.startswith("#NeedSupport"):
            try:
                period_id = message.split('_')[1]
            except IndexError:
                continue 

            # Simular tiempo de pensamiento (procesamiento)
            time.sleep(random.uniform(0.5, 3.5))

            decision = random.random()
            response = ""

            if decision < 0.40: # 40% -> Ok
                response = f"Ok_{period_id}"
            elif decision < 0.90: # 50% -> No
                response = f"No_{period_id}"
            else: # 10% -> Silencio
                print(f"{color_code}[Agente {agent_id}]\tIgnorar solicitud {period_id} (Silencio){RESET}")
                continue

            sock.sendto(response.encode('utf-8'), addr)
            print(f"{color_code}[Agente {agent_id}]\tEnviar {ITALIC}{response}{RESET}{color_code} a requester{RESET}")

"""
 Agente que solicita ayuda en intevalos aleatorios. Recibe las respuestas y decide si el periodo ha sido satisfecho (2 Oks).
 
 La variable target_ports hace referencia a los puertos conocidos de los agentes a los que se solicituda ayuda.
"""
def requester_agent(target_ports, total_periods):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM para UDP
    sock.bind((socket.gethostname(), REQUESTER_PORT))
    period_wait_time = 3.0
    sock.settimeout(period_wait_time) # Espera máxima por periodo (importante por si se dieran 3 silencios)

    satisfied_periods = 0

    color_code = REQUESTER_COLOR
    print(f"{color_code}[Solicitante]\tListo en puerto {REQUESTER_PORT}. Periodos a simular: {total_periods}{RESET}")
    
    time.sleep(1) # Esperar a que los respondedores estén listos
 
    for current_period in range(1, total_periods + 1):
        print(f"{BOLD}\n{'-'*15} INICIO PERIODO {current_period} {'-'*15}{RESET}\n")
        
        # Enviar solicitud con la MARCA DE TIEMPO/PERIODO
        request = f"#NeedSupport_{current_period}"
        for port in target_ports:
            sock.sendto(request.encode('utf-8'), (socket.gethostname(), port))
        
        print(f"{color_code}[Solicitante]\tBroadcast {ITALIC}{request}{RESET}")

        oks_received = 0
        start_time = time.time()
        
        while True:
            # Control del tiempo de espera del periodo
            if time.time() - start_time > period_wait_time:
                print(f"{color_code}[Solicitante]\tTiempo de espera agotado para periodo {current_period}.{RESET}")
                break
            
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                resp_str = data.decode('utf-8')
                
                # Formato esperado: "Ok_X" o "No_X"
                if "_" in resp_str:
                    msg_type, msg_period = resp_str.split('_')
                    
                    # Validar periodo
                    if int(msg_period) != current_period:
                        print(f"{color_code}[Solicitante]\tRecibido {ITALIC}{resp_str}{RESET}{color_code} (No válido - Periodo incorrecto){RESET}")
                        continue # Saltamos al siguiente ciclo del while, ignorando este mensaje
                    
                    # Mensaje válido
                    print(f"{color_code}[Solicitante]\tRecibido {ITALIC}{resp_str}{RESET}{color_code} (Válido){RESET}")
                    
                    if msg_type == "Ok":
                        oks_received += 1
                    
                    # Si ya tenemos quórum, dejamos de esperar activamente
                    if oks_received >= 2:
                        print(f"{GREEN}{BOLD}[Solicitante]\t¡QUÓRUM ALCANZADO para periodo {current_period}!{RESET}")
                        satisfied_periods += 1
                        break
                
            except socket.timeout: # Timeout interno del socket
                break

        if oks_received < 2: # Si al finalizar el periodo no se ha alcanzado quórum
             print(f"{RED}[Solicitante]\tPeriodo {current_period} FALLIDO (Solo {oks_received} OKs){RESET}")

        print(f"\n{BOLD}{'-'*15} FIN PERIODO {current_period} {'-'*15}\n{RESET}")

        # Espera aleatoria antes del siguiente periodo
        wait_next = random.uniform(2.0, 4.0)
        print(f"Esperando {wait_next:.2f}s para siguiente ciclo...")
        time.sleep(wait_next)

    # Métricas finales
    satisfaction_degree = (satisfied_periods / total_periods) * 100
    print(f"\n{'='*50}")
    print(f"INFORME FINAL")
    print(f"Periodos Totales: {total_periods}")
    print(f"Periodos Exitosos: {satisfied_periods}")
    print(f"Grado de Satisfacción: {satisfaction_degree}%")
    print(f"{'='*30}")

if __name__ == "__main__":
    # Iniciar hilos de agentes respondedores
    for i, port in enumerate(RESPONDER_PORTS):
        t = threading.Thread(target=responder_agent, args=(i+1, port), daemon=True)
        t.start()

    # Iniciar hilo agente solicitante
    requester_agent(RESPONDER_PORTS, N_PERIODS)