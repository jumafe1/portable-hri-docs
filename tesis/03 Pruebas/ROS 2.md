# ROS 2

## Objetivo

Comprobar descubrimiento y comunicación básica entre nodos ROS 2 Jazzy dentro del entorno [[Docker]], sin robots ni simulador físico.

## Estado

Verificado el 9 de septiembre de 2026: comunicación real C++ → Python en ROS 2 Jazzy dentro del contenedor. Ocho mensajes únicos publicados y siete recibidos coincidentes. El criterio exige al menos tres coincidencias y ninguna recepción ajena al publicador; se cumplió. No se afirma entrega de todos los mensajes desde el arranque del descubrimiento.

## Criterio de aceptación

Ejecutar publicador y suscriptor, observar recepción de mensajes y conservar comandos y evidencia. Identificar distribución, dominio y ubicación de los procesos. Finalizar los nodos de prueba y registrar cualquier fallo.

## Registro de ejecución

- Fecha: 2026-09-09, inicio 06:36:29 UTC (01:36 Bogotá).
- Dominio: 42; namespace exclusivo de la ejecución: `/tesis_smoke_22`.
- Publicador: `demo_nodes_cpp/talker`; receptor: `demo_nodes_py/listener`.
- Evidencia desde la raíz del proyecto: `repos_tesis/hri_viability/results/ros2/result.json`, `talker.log` y `listener.log`.
- Los procesos de prueba se detuvieron al terminar.

Repetir desde la raíz `tesis`:

```bash
docker compose -f docker/compose.yaml exec -T dev bash -c 'source /opt/ros/jazzy/setup.bash && python3 /workspace/src/hri_viability/tests/ros2_smoke.py'
```

El script termina con código distinto de cero si falla el criterio. Cada ejecución reemplaza la evidencia de esta prueba en `results/ros2`; guardar una copia si se quiere conservar una ejecución anterior.

## Límites

La comunicación dentro de un contenedor no demuestra conectividad con NAO, Pepper ni otras máquinas, ni valida capacidades. La siguiente evaluación es [[Capabilities2]].
