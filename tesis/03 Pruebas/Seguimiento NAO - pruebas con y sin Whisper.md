# Seguimiento en NAO: pruebas con y sin Whisper

Fecha de consolidación: 11 de noviembre de 2026. Ensayos comparativos: 4 de noviembre de 2026, hora local de Bogotá. Relacionado con [[Proyecto]], [[Semana 6 - Capacidades y servicios]] y [[Semana 7 - Verificación NAO]].

## Objetivo y estado de las pruebas

Documentar el funcionamiento del seguimiento de personas en NAO, la integración de transcripción con Whisper y el efecto observado al ejecutarlos simultáneamente en el computador del laboratorio. Las pruebas físicas ya se ejecutaron; esta actualización organiza sus registros existentes y las confirmaciones del autor. No corresponde a una nueva ejecución ni a una medición posterior a los cambios de Vosk.

El seguimiento sin transcripción funcionó de forma apreciablemente más fluida según el autor y las métricas conservadas. Whisper produjo transcripciones en ensayos previos, pero su integración simultánea con YOLO y movimiento mostró saturación de CPU, menor frecuencia de detección y pausas por percepción antigua. No se declara resuelto ese problema de rendimiento.

La evaluación formal de Vosk queda en espera por decisión del autor. Se registra su implementación y la comprobación inicial, sin asignarle métricas de rendimiento ni presentarlo como solución ya validada al problema de CPU.

## Disponibilidad de Pepper y evidencia anterior

El 11 de noviembre el autor informó que Pepper sufrió un accidente y no está en funcionamiento. La fecha del accidente y el plazo de reparación no están registrados. Por esa razón, las pruebas actuales se realizan exclusivamente con NAO y la repetición de la composición actual en Pepper queda suspendida por disponibilidad de hardware.

Las pruebas anteriores siguen siendo evidencia válida de los recorridos que se ejecutaron:

| Prueba previa | Fecha | Evidencia y resultado |
| --- | --- | --- |
| `Speak` mediante Capabilities2 en Pepper | 17/09/2026 | `technical_success=true`, `audible_confirmation=true`, `passed=true`; se conservó `/hri/speak` y se remapeó el backend a `/pepper/say`. [Resultado de voz][pepper-speak]. |
| Primera aplicación YASMIN de voz en Pepper | Septiembre de 2026 | La nota de semana 7 registra ejecución física, voz audible y liberación de capacidad. No equivale a la aplicación integrada actual. |
| `MoveRelative` en Pepper | 22/09/2026 | Solicitud frontal de 0,10 m; resultado medido por odometría de aproximadamente 0,10435 m, confirmación del observador y liberación. [Resultado de movimiento][pepper-move]. |
| `MoveRelative` en NAO | 22/09/2026 | Solicitud de giro de 0,10 rad; resultado de aproximadamente 0,09779 rad, confirmación del observador y liberación. [Resultado de movimiento][nao-move]. |

Estas evidencias demuestran reutilización de contratos y proveedores en operaciones concretas. No prueban equivalencia completa de seguimiento, audio o rendimiento entre los dos robots. La restricción operativa no se documenta como aprobación académica de un cambio del objetivo original.

## Implementación utilizada y configuración

`FollowPerson` combina `DetectPeople` y `MoveVelocity`. YOLO procesa las imágenes; su proveedor las traduce al flujo común de personas. YASMIN organiza la ejecución y Capabilities2 administra adquisición, vínculo y liberación de proveedores. Whisper se ejecuta en un worker separado y se integra mediante `TranscribeSpeech`. Compartir computador sigue implicando compartir CPU aunque sean procesos separados.

Las pruebas usaron NAO, ROS 2 Jazzy sobre Ubuntu 24.04 x86_64, imagen de 320×240, `CameraTop_optical_frame`, confianza mínima 0,65, `target_height_ratio=0.75`, velocidad máxima de avance 0,1 m/s y orientación de cabeza desactivada. La velocidad es proporcional al error visual hasta ese máximo; 0,1 m/s no significa velocidad constante. La altura objetivo es una proporción de imagen, no una distancia medida en metros.

Se utilizó YOLO en CPU y el modelo local Whisper `base.pt`. El equipo dispone de cuatro CPU lógicas. Los datos que siguen describen ese equipo y esas ejecuciones, no una comparación general de todos los modelos de reconocimiento.

## Recuperación del seguimiento y comprobaciones físicas

El comportamiento inicial terminaba ante `stale_or_future_image`, `person_missing` o `ambiguous_people`. Se introdujeron dos incrementos:

1. **Recuperación de imágenes:** solicitar velocidad cero al caducar la percepción y esperar imágenes nuevas. En la prueba de esa versión, el autor confirmó movimiento y recuperación; el resumen reportó 469 frames, 6 recuperaciones de imagen, acuse de parada y liberación. La ejecución terminó por `person_missing`, que todavía era terminal en ese incremento.
2. **Espera persistente por personas o imágenes:** mantener la aplicación activa cuando no hay persona, hay varias o faltan imágenes recientes; reanudar tras tres observaciones nuevas válidas y el acuse de parada correspondiente. El autor confirmó que NAO paró al salir de cámara, continuó al regresar, paró cuando pasó otra persona y continuó cuando quedó una sola. [Registro de recuperación y confirmación física][person-wait].

El segundo incremento sustituyó el timeout de recuperación de tres segundos del primero. No deben mezclarse las políticas de ambas versiones. Los fallos críticos de proveedores, vínculo, geometría o comandos conservan tratamiento de error. Tampoco hay reconocimiento de identidad: recuperar una única detección no certifica que sea la misma persona anterior.

El criterio funcional de estos ensayos fue observar parada durante la condición inválida y continuidad de la aplicación hasta poder recuperar el seguimiento. La confirmación del autor es cualitativa; no se midieron tiempo ni distancia de frenado. Las pruebas de software del segundo incremento registraron 208 casos aprobados y compilación correcta, con transporte simulado para los casos unitarios. La prueba ROS integral del agente no se ejecutó; no se confunde esa limitación con las comprobaciones físicas que hizo el autor.

## Whisper: funcionamiento y ajustes realizados

El autor observó texto reconocido desde el micrófono de NAO en `/hri/speech/transcript`. Esto confirma un recorrido funcional de captura y transcripción, aunque también reportó errores de reconocimiento. No se calculó tasa de error de palabras ni precisión sobre un corpus.

Se añadió segmentación por actividad de voz con WebRTC VAD, cierre de frase por silencio y captura continua mientras se ejecuta la inferencia. La cola pendiente se limitó a dos fragmentos y descarta el más antiguo cuando se llena, dejando el contador `dropped_segments`. Se conservó el modelo `base.pt`; la configuración documentada usa un hilo de inferencia y dos hilos de CPU de Torch. [Registro del incremento VAD][vad].

Ese registro conserva 264 pruebas unitarias aprobadas entre aplicación, captura y transcripción, compilación y una prueba VAD sin micrófono. La integración ROS del agente quedó bloqueada antes de crear nodos por la restricción del entorno de prueba. Las transcripciones físicas posteriores proceden de los ensayos del autor; no se atribuyen a esas pruebas unitarias.

En una ejecución integrada anterior de aproximadamente 321 s, el resumen enviado por el autor registró 929 frames, 28 recuperaciones de imagen, 3 recuperaciones de persona y 1 transcripción recibida. Se observaron 9 avisos de descarte de frases. Como los logs de seguimiento estaban a nivel `warn`, esa ejecución no permite reconstruir la duración de cada pausa; motivó la comparación instrumentada siguiente. [Revisión de esos logs][early-review].

## Comparación instrumentada del 4 de noviembre

Se ejecutaron dos ensayos consecutivos con el observador `hri_diagnostics`. El primero incluyó Whisper y el segundo desactivó la transcripción. Ambos terminaron por `Ctrl+C` del operador. El criterio de esta comparación exploratoria fue contrastar carga, frescura y frecuencia de percepción y tiempo de espera; no se había fijado un umbral numérico de aprobación ni se mide aquí la precisión del reconocimiento.

| Medida | Con Whisper | Sin transcripción |
| --- | ---: | ---: |
| Duración del observador | 103,80 s | 98,57 s |
| Tiempo de decisiones de seguimiento observado | 101,11 s | 96,19 s |
| CPU media del sistema, excluyendo los primeros 10 s | 92,82 % | 53,53 % |
| CPU mediana del sistema, misma ventana | 98,75 % | 57,40 % |
| Detecciones recibidas durante el registro | 229 | 498 |
| Frecuencia reciente de `/hri/people`, últimos 30 s | 1,89 Hz | 5,01 Hz |
| Antigüedad del frame al recibir `/hri/people`, percentil 95 de los últimos 30 s | 1,046 s | 0,201 s |
| Tiempo observado en `waiting_fresh_images` | 83,55 s | 0,00 s |
| Recuperaciones de imagen registradas | 3 | 0 |
| Recuperaciones de persona registradas | 0 | 4 |
| Fragmentos de voz descartados, último contador | 4 | No aplica |
| Transcripciones recibidas, resumen final de la aplicación | 0 | No aplica |

Fuente numérica: [comparación conservada][comparison], contrastada con los dos `summary.json` locales. Los ceros de recuperaciones de persona no implican mejor seguimiento; dependen de la escena y del tiempo dedicado a esperar imágenes válidas. La ausencia de transcripciones en este ensayo no invalida las transcripciones observadas en otros ensayos.

**Interpretación:** los registros aportan evidencia de contención de CPU durante la ejecución conjunta de Whisper y YOLO. Con Whisper se observó mayor ocupación, detecciones más lentas y antiguas, y más tiempo con el movimiento retenido esperando percepción reciente. Sin transcripción, el autor reportó un seguimiento mucho más fluido, consistente con las métricas. No se atribuye el retraso observado durante la ejecución al error posterior de cierre.

**Límites del método:** fue una pareja de ensayos secuenciales con duraciones distintas, sin control estricto de escena ni carga restante del computador. Las tasas y percentiles corresponden a la ventana final de 30 s, no a toda la ejecución. Los tiempos por motivo son estimaciones del observador. La CPU de la tabla es del sistema completo; en los campos por proceso, 100 % equivale a una CPU lógica y se puede superar ese valor. El observador también consume recursos. No se deduce una mejora garantizada en cualquier entorno ni una medición de parada física.

## Comandos y trazabilidad

Los comandos utilizados el 4 de noviembre, cuando Whisper era la opción de voz del lanzamiento integrado, fueron:

```bash
# Ensayo con Whisper.
ros2 launch hri_reference_app aplicacion_hri.launch.py \
  confirm_listen:=ESCUCHAR \
  enable_motion:=true confirm:=MOVER \
  record_diagnostics:=true

# Ensayo posterior sin transcripción.
ros2 launch hri_reference_app aplicacion_hri.launch.py \
  transcribe_speech:=false \
  enable_motion:=true confirm:=MOVER \
  record_diagnostics:=true
```

Son comandos históricos con el entorno ROS y el driver ya iniciados. La copia local de la rama de trabajo del 11 de noviembre selecciona Vosk por defecto; esos cambios aún no están publicados al consolidar esta nota. Para repetir **Whisper** en esa copia se debe seleccionar expresamente el motor y desactivar las órdenes por voz:

```bash
ros2 launch hri_reference_app aplicacion_hri.launch.py \
  speech_backend:=whisper voice_commands:=false \
  confirm_listen:=ESCUCHAR \
  enable_motion:=true confirm:=MOVER \
  record_diagnostics:=true
```

Este último comando describe cómo solicitar otro ensayo; no se presenta como una prueba nueva ya ejecutada. El comando con `transcribe_speech:=false` sigue siendo la variante sin escucha. El modelo, los paquetes y el driver deben estar preparados según la guía de instalación del sistema de referencia.

Los registros locales de los ensayos medidos se encuentran bajo `~/.ros/log/`:

| Variante | Subdirectorio de ejecución |
| --- | --- |
| Con Whisper | `2026-11-04-18-25-49-422827-robotica-56235/hri_diagnostics/` |
| Sin transcripción | `2026-11-04-18-29-35-115223-robotica-56619/hri_diagnostics/` |

Cada directorio conserva `summary.json` y `events.jsonl`. Los logs originales son locales; el JSON comparativo enlazado está versionado. El observador registra decisiones, tiempos, CPU y estado de voz; no guarda imágenes, audio ni texto reconocido. Los resultados enlazados en esta nota se fijan al commit publicado `eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932` del sistema de referencia. Ese commit conserva la evidencia posteriormente consolidada, no identifica por sí solo todos los binarios instalados durante cada ensayo del 4 de noviembre.

## Cierre e incidencias observadas

Las dos ejecuciones finalizaron por cancelación del operador. Sus resúmenes indicaron `cancelled_or_ros_shutdown`, `stop_acknowledged=true` y liberación de capacidades. La aplicación puede devolver `application_failed` y código 1 al cancelar; esos campos deben leerse junto al motivo de terminación.

Se observaron además `InvalidHandle` durante destrucción de entidades ROS y, con Whisper, `terminate called without an active exception` y código de salida -6. Son incidencias de cierre que permanecen registradas, no una terminación completamente limpia ni la explicación de las pausas anteriores a `Ctrl+C`. El acuse de parada es telemetría del software; no sustituye una medición del cese físico del movimiento.

## Vosk: implementación disponible, evaluación en espera

La copia local de la rama de trabajo `perf/whisper-follow-cpu` incorpora un proveedor Vosk para vocabulario acotado y respuestas mediante `Speak`, manteniendo los contratos y la gestión de Capabilities2. Sus cambios están pendientes de versionar y publicar al consolidar esta nota. Permite solicitar pausa y seguimiento con variantes como «Nao, detente», «Nao, quédate quieto» y «Nao, sígueme», con respuestas elegidas de grupos configurables. No implementa conversación libre ni un modelo generativo.

El 11 de noviembre el autor confirmó una comprobación inicial: reconoció lo dicho y el robot respondió, aunque tuvo que hablar cerca. Se conserva como observación cualitativa inicial. No demuestra por sí sola precisión, alcance del micrófono, latencia de parada ni reducción de CPU en la aplicación integrada.

**Estado por decisión del autor: evaluación formal de Vosk en espera.** No se añaden ensayos ni resultados comparativos de Vosk en esta actualización. Su desarrollo y esa primera comprobación se distinguen de una campaña de validación cerrada. Cuando se retome podrán medirse reconocimiento, falsas activaciones, distancia de habla, respuesta y CPU durante seguimiento. La optimización de Whisper también continúa en espera.

## Resultado de este corte

El seguimiento físico en NAO y sus recuperaciones cuentan con confirmaciones del autor y registros de ejecución. Whisper cuenta con evidencia de transcripción y de su limitación de rendimiento al compartir el equipo con YOLO. La variante sin transcripción es la referencia medida más fluida de estos dos ensayos. La evaluación continúa abierta: Pepper está indisponible, Vosk permanece en espera y los defectos de cierre y las métricas pendientes se conservan como límites del resultado.

[comparison]: https://github.com/jumafe1/portable-hri-reference-system/blob/eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932/results/follow_whisper_comparison_20261104.json
[person-wait]: https://github.com/jumafe1/portable-hri-reference-system/blob/eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932/results/follow_person_wait_20261104.json
[vad]: https://github.com/jumafe1/portable-hri-reference-system/blob/eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932/results/whisper_vad_stream_20261104.json
[early-review]: https://github.com/jumafe1/portable-hri-reference-system/blob/eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932/results/integrated_follow_log_review_20261104.json
[pepper-speak]: https://github.com/jumafe1/portable-hri-reference-system/blob/eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932/results/pepper_speak_via_nao_provider_physical/result.json
[pepper-move]: https://github.com/jumafe1/portable-hri-reference-system/blob/eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932/results/pepper_move_relative_physical/result.json
[nao-move]: https://github.com/jumafe1/portable-hri-reference-system/blob/eb3c5d1bcca267b3ab746b61d00bb8b7d81c6932/results/nao_move_relative_physical/result.json
