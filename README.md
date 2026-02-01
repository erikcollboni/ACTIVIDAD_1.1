# ACTIVIDAD_1.1
# Simulación de Agentes Distribuidos con Sockets UDP

Este proyecto implementa una simulación de un sistema distribuido asíncrono utilizando **Python** y la librería `socket`. El objetivo es modelar la comunicación entre agentes independientes en un canal compartido, gestionando la aleatoriedad, la pérdida de mensajes y la concurrencia mediante hilos (`threading`).

## 1. Descripción del Problema

[cite_start]El sistema simula un entorno con **4 agentes** que se comunican en un mismo canal compartido[cite: 4, 5]:

### El Agente Solicitante (Requester)
* [cite_start]Emite periódicamente una señal de ayuda (`#NeedSupport!`) a los agentes conocidos[cite: 6].
* Espera respuestas durante un intervalo de tiempo limitado.
* [cite_start]Considera su solicitud **satisfecha** si recibe un quórum de al menos **2 respuestas de ayuda** ("ok!")[cite: 11].
* [cite_start]Calcula el **grado de satisfacción** del quórum tras una serie fija de periodos[cite: 15].

### Los Agentes Respondedores (Responders)
* [cite_start]Reciben la solicitud y simulan un tiempo de computación aleatorio[cite: 7].
* Toman una decisión basada en las siguientes probabilidades:
    * [cite_start]**40%**: Responden con ayuda ("ok!")[cite: 8].
    * [cite_start]**50%**: Niegan la ayuda ("no!")[cite: 9].
    * [cite_start]**10%**: No responden (simulación de silencio o fallo de red)[cite: 10].

## 2. Diseño de la Solución

La solución se ha implementado en un único script de Python que orquesta múltiples hilos para simular la ejecución paralela en una sola máquina.

### Estructura del Código

* **Multihilo (Threading):** Se utiliza la librería `threading` para ejecutar a los agentes respondedores en segundo plano (modo `daemon`), permitiendo que funcionen simultáneamente mientras el hilo principal ejecuta la lógica del solicitante.
* **Identificadores de Periodo (`_id`):** Para gestionar la asincronía, cada solicitud lleva una marca de tiempo lógica (ej. `#NeedSupport_3`). Las respuestas incluyen esta marca (`Ok_3`). [cite_start]Esto permite al solicitante **filtrar y descartar mensajes tardíos** que pertenecen a periodos anteriores[cite: 13].
* **Logging Visual:** Se han implementado códigos de escape ANSI para colorear la salida de la consola. Cada agente tiene un color asignado, facilitando la traza de la ejecución y la depuración visual en tiempo real.

### Flujo de Ejecución
1.  Los agentes respondedores inician y escuchan en puertos específicos (`5001`, `5002`, `5003`).
2.  El solicitante envía un *broadcast* manual a estos puertos.
3.  El solicitante entra en un bucle de espera con **Timeout**.
4.  Si se alcanza el quórum o se agota el tiempo, el sistema avanza al siguiente periodo.

## 3. Justificación Técnica: Uso de UDP

[cite_start]Se ha seleccionado el protocolo **UDP (`SOCK_DGRAM`)** en lugar de TCP por las siguientes razones de diseño[cite: 18]:

1.  **Modelo "Fire and Forget" (Disparar y Olvidar):**
    El problema plantea un escenario asíncrono donde el solicitante pide ayuda sin saber si los receptores están disponibles. [cite_start]UDP permite enviar datagramas sin establecer una conexión previa (*handshake*), lo cual es ideal para modelos de difusión o comunicación de grupo ligera[cite: 3].

2.  **Tolerancia a Fallos y Silencios:**
    El requisito de que un agente pueda "no responder el 10% de las veces" se alinea naturalmente con la falta de fiabilidad de UDP. Si un paquete se pierde, el protocolo no intenta retransmitirlo (como haría TCP), permitiendo que la lógica del programa maneje el silencio simplemente agotando el tiempo de espera.

3.  **Preservación de Límites de Mensaje:**
    UDP envía mensajes discretos (datagramas). Esto simplifica el análisis de respuestas cortas ("Ok", "No") sin necesidad de gestionar un flujo de bytes continuo (`stream`) donde múltiples mensajes podrían llegar pegados, algo común en TCP.

## 4. Requisitos y Ejecución

### Requisitos
* Python 3.x
* Librerías estándar: `socket`, `threading`, `time`, `random`, `datetime`.

### Instrucciones
Ejecuta el script principal desde la terminal:

```bash
python distributed_agents.py