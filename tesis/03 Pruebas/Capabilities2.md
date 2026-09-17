# Capabilities2

## Objetivo

Evaluar si el núcleo de Capabilities2 permite gestionar proveedores en ROS 2 Jazzy antes de adoptarlo como dependencia de la arquitectura descrita en [[Proyecto]]. Requiere el entorno [[Docker]] y la verificación de [[ROS 2]].

## Estado

Evaluación ejecutada el 9 de septiembre de 2026: núcleo compilado sin cambios al código externo y dos proveedores ficticios funcionales. Pasaron 12 de 13 comprobaciones. La prueba completa queda **fallida** por un defecto de reporte de error ante proveedor inexistente; no se aprueba aún la adopción sin reservas.

Incremento del 16 de septiembre de 2026: se implementó `hri_naoqi_providers/NaoSpeak`, que Capabilities2 activa para exponer `/hri/speak` y adaptar solicitudes al servicio SinfonIA `/nao/say`. La prueba local con backend simulado pasó **9 de 9** comprobaciones. Esto valida integración y manejo de errores sin robot; la ejecución del mismo proveedor contra NAO físico queda pendiente.

## Criterios de evaluación

- Compilar los paquetes necesarios y arrancar el servidor.
- Registrar o descubrir una interfaz y dos proveedores ficticios.
- Seleccionar y activar cada proveedor con el mismo cliente, cambiando configuración.
- Comprobar su uso y liberación mediante el ciclo de vida de Capabilities2.
- Observar errores ante un proveedor inexistente y un fallo provocado.
- Registrar el mecanismo de ejecución utilizado y sus limitaciones.

El proveedor propio es `hri_mock_runner::MockSpeakRunner`, cargado por pluginlib. Capabilities2 activa y libera el servicio común `/hri/speak`. El cliente llama ese servicio con texto; la respuesta identifica el proveedor y devuelve el texto o un error ficticio. No se utiliza `trigger` ni se simula audio real. `Speak.srv` es un contrato experimental inmediato, no la acción cancelable definitiva de voz.

## Registro de ejecución

- Fuente: copia local `repos/capabilities2-main`, montada en solo lectura. Se comparó con el historial upstream y coincide con la etiqueta `v0.1.0`, commit `67606acbf2fe39e828b03985a2f6881b909c1091`, salvo un archivo `.DS_Store`; esa versión quedó fijada en el manifiesto reproducible.
- Compilados: `capabilities2_msgs`, `capabilities2_runner`, `capabilities2_launch_proxy`, `capabilities2_server` y el paquete propio `hri_mock_runner`.
- Primer intento: faltó seleccionar `capabilities2_launch_proxy`. Se corrigió el comando usando `--packages-up-to`, sin modificar upstream. Registro: `repos_tesis/hri_viability/results/capabilities-build.log`.
- Compilación completa: cinco paquetes terminados; advertencias C++ preexistentes en upstream. Registro: `results/capabilities-build-complete.log` dentro del experimento.
- Prueba: `tests/capabilities_probe.py`; registros y resultado estructurado en `results/capabilities/server.log` y `result.json`.

| Comprobación                                            | Resultado                   |
| ------------------------------------------------------- | --------------------------- |
| Registro y descubrimiento de interfaz y dos proveedores | Pasa                        |
| Selección explícita de mock_nao y mock_pepper           | Pasa para ambos             |
| Mismo cliente y servicio, texto y proveedor correctos   | Pasa para ambos             |
| Texto `__fail__` produce error de proveedor             | Pasa para ambos             |
| Parada y ausencia en catálogo de capacidades activas    | Pasa para ambos             |
| Uso con identificador de bond y liberación explícita    | Pasa                        |
| Proveedor inexistente no queda activo                   | Pasa                        |
| Proveedor inexistente devuelve error en StartCapability | **Falla: result=0 (éxito)** |

El servidor captura el fallo de configuración del proveedor, pero `start_capability_cb` asigna éxito incondicionalmente (`capabilities2_server/include/capabilities2_server/capabilities_server.hpp`). El log muestra `run config is not valid` mientras la respuesta dice éxito. La prueba conserva salida 1; no se relajó la aserción para ocultar el defecto.

Repetir desde la raíz de `tesis`:

```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml up -d
docker compose -f docker/compose.yaml exec -T dev bash -c 'source /opt/ros/jazzy/setup.bash && colcon build --base-paths /opt/reference_repos/capabilities2-main /workspace/src/hri_viability --packages-up-to capabilities2_server hri_mock_runner --parallel-workers 2'
docker compose -f docker/compose.yaml exec -T dev bash -c 'source /opt/ros/jazzy/setup.bash && source /workspace/install/setup.bash && python3 /workspace/src/hri_viability/tests/capabilities_probe.py'
```

Los YAML se registran programáticamente y están visibles en el script. La selección cambia el parámetro `preferred_provider`; ambos proveedores comparten el código del runner. La base SQLite es temporal y el servidor se detiene al finalizar. Cada repetición reemplaza `results/capabilities/`.

## Decisión provisional

Verificación complementaria: Compose válido, scripts Python analizados sintácticamente y `colcon test` ejecutado. Este último reporta **0 tests**, por lo que no aporta cobertura funcional; los resultados de la tabla provienen del script real contra el servidor. No hay type-checker Python ni ESLint configurado; el código C++ fue comprobado por el compilador. Al terminar solo quedaron el proceso init y sleep del contenedor.

Continuar evaluando Capabilities2 con un runner propio es viable para este corte. Antes de integrarlo como base estable, definir una protección cliente que contraste catálogo/estado o una corrección upstream del reporte de errores, conservando esta prueba negativa. No se ha creado fork ni reparado el framework en esta evaluación.

La afirmación del documento de contexto sobre LaunchRunner deshabilitado no describe esta copia: el plugin se incluye/exporta y compiló. Eso **no demuestra que ejecute launch correctamente**; su ejecución no se probó. Tampoco se compilaron ni validaron executor, BT, audio o Nav2.

## Proveedor real `NaoSpeak`

El contrato propio vive en `portable-hri-interfaces`, el runner en `portable-hri-providers` y la prueba en `portable-hri-reference-system`. La cadena diseñada es:

```text
cliente → /hri/speak → NaoSpeakRunner → /nao/say → adaptador SinfonIA → NAOqi
```

El proveedor usa idioma `Spanish` cuando la solicitud no indica idioma y fuerza `animated=false` y `asynchronous=false`. Solo admite una solicitud simultánea. Reporta texto vacío, proveedor ocupado, backend ausente, error del backend y timeout de cinco segundos. Un identificador por solicitud evita que una respuesta tardía interfiera con una llamada posterior. Detener el proveedor no puede cancelar una frase ya aceptada por NAOqi.

La prueba `capabilities_nao_speak_probe.py` registró y seleccionó el proveedor mediante Capabilities2 y comprobó:

| Comprobación | Resultado |
| --- | --- |
| Catálogo y selección de `NaoSpeak` | Pasa |
| Traducción de texto/idioma y flags seguros | Pasa |
| Timeout y recuperación posterior | Pasa |
| Propagación de rechazo del backend | Pasa |
| Liberación explícita | Pasa |
| Backend ausente | Pasa |
| Liberación final | Pasa |

El resultado estructurado conserva nueve aserciones aprobadas en `portable-hri-reference-system/results/nao_speak/result.json`. El backend `/nao/say` fue simulado: no hubo audio ni robot en esta ejecución. El script físico supervisado está preparado, pero no debe presentarse como ejecutado hasta obtener respuesta técnica y confirmación auditiva en el laboratorio.

## Límites

Dos proveedores ficticios aportan evidencia de intercambio de implementaciones en software. No validan síntesis de voz, NAOqi, sensores, actuadores ni portabilidad física entre NAO y Pepper. Integrar un robot temprano una vez resuelta esta evaluación.

No se validaron dependencias entre capacidades, heartbeat con peer de bond, limpieza automática al perder un cliente, cancelación de acciones prolongadas ni desaparición del servicio tras parada (se verificó la lista de runners). Estas pruebas no deben darse por realizadas.
