# Proyecto

Actualización: 11 de noviembre de 2026.

## Objetivo y disponibilidad de los robots

El objetivo original es construir una arquitectura modular sobre ROS 2 que permita ejecutar una misma aplicación de interacción humano-robot en NAO y Pepper, cambiando configuración y proveedores o adaptadores específicos, y conservando la lógica de alto nivel.

**La validación física actual continúa únicamente con NAO.** El autor informó el 11 de noviembre de 2026 que Pepper sufrió un accidente y quedó fuera de funcionamiento. Esta es la fecha del reporte; no se dispone de la fecha exacta del accidente ni de una previsión de recuperación. La repetición de la aplicación integrada actual en Pepper queda impedida por la indisponibilidad del equipo, no registrada como un fallo de portabilidad del software.

Se conserva la evidencia física obtenida anteriormente con Pepper: voz mediante el contrato común `Speak` y Capabilities2, una primera aplicación YASMIN de voz y desplazamiento relativo. Estas pruebas acreditan recorridos concretos anteriores; no validan automáticamente el seguimiento y la escucha de la versión integrada actual. La cronología y los resultados están en [[Semana 7 - Verificación NAO]] y [[Seguimiento NAO - pruebas con y sin Whisper]].

La limitación de hardware delimita la evidencia disponible. No se presenta esta nota como una modificación formalmente aprobada de los objetivos académicos. La propuesta y el contexto técnico completo se conservan fuera de este vault público.

## Estado de implementación y evaluación

La aplicación se inicia con `aplicacion_hri.launch.py`. El driver ROS 2/NAOqi permanece como dependencia externa. El lanzamiento integrado organiza los procesos de percepción y voz; YASMIN coordina los comportamientos y Capabilities2 administra los proveedores. La aplicación consume contratos comunes, mientras los proveedores encapsulan el hardware y los motores de percepción.

| Componente | Estado al 11 de noviembre de 2026 |
| --- | --- |
| Contratos y proveedores | Implementados `Speak`, `DetectPeople`, `MoveRelative`, `MoveVelocity`, `OrientCamera` y `TranscribeSpeech`; la existencia del contrato no equivale a validación física de todas sus opciones. |
| `FollowPerson` en NAO | Combina `DetectPeople` y `MoveVelocity`. El autor confirmó movimiento, parada al perder la persona o aparecer varias y recuperación al volver una detección válida. |
| Imágenes antiguas | El seguimiento solicita velocidad cero y espera recuperación; los cortes transitorios ya no requieren reiniciar el programa. Los errores críticos conservan una salida de fallo. |
| Whisper | Transcripción desde el micrófono de NAO implementada y observada. Se añadieron segmentación por actividad de voz y captura continua con cola acotada. Su ejecución conjunta con YOLO y seguimiento fue medida el 4 de noviembre: elevada carga de CPU y esperas prolongadas por imágenes antiguas. |
| Seguimiento sin Whisper | Ensayo físico medido el 4 de noviembre: mayor frecuencia de detecciones, menor antigüedad y ninguna espera registrada por imágenes antiguas en esa ejecución. |
| Vosk y respuestas `Speak` | Alternativa implementada en la copia local de la rama de trabajo para órdenes acotadas; sus cambios aún no están publicados al consolidar esta nota. Existe una confirmación inicial del autor de reconocimiento y respuesta hablada cerca del robot. **Evaluación formal en espera por decisión del autor**; sin resultados comparativos de CPU, alcance o precisión. |
| Pepper | Pruebas previas conservadas; nuevas pruebas físicas suspendidas por indisponibilidad tras el accidente. |

Las pruebas ya están en marcha. Los comandos, criterios, resultados numéricos, fallos de cierre y límites de interpretación se reúnen en [[Seguimiento NAO - pruebas con y sin Whisper]]. Esta nota distingue observación física, registros instrumentados y pruebas de software; no declara concluida toda la evaluación de la aplicación.

## Organización de documentación y código

El vault mantiene tres carpetas: `01 Proyecto` para alcance y decisiones, `02 Entorno` para instalación y uso, y `03 Pruebas` para experimentos y resultados. Cada nota de prueba debe incluir objetivo, fecha, comando repetible, criterio, evidencia, fallos y límites. Se actualiza la nota correspondiente; se crea una nueva para un experimento o decisión diferente.

| Repositorio | Responsabilidad |
| --- | --- |
| [portable-hri-docs](https://github.com/jumafe1/portable-hri-docs) | Este registro de alcance, decisiones y pruebas. |
| [portable-hri-interfaces](https://github.com/jumafe1/portable-hri-interfaces) | Contratos ROS 2 y descripciones de capacidades. |
| [portable-hri-providers](https://github.com/jumafe1/portable-hri-providers) | Adaptadores NAOqi y proveedores perceptivos. |
| [portable-hri-reference-system](https://github.com/jumafe1/portable-hri-reference-system) | Aplicación YASMIN, lanzamientos, configuración, pruebas y resultados técnicos. |

[[Semana 6 - Capacidades y servicios]] conserva la caracterización inicial de NAO/Pepper y los candidatos estudiados; no es una lista de funcionalidades terminadas. [[Docker]], [[ROS 2]] y [[Capabilities2]] documentan verificaciones históricas con sus fechas. Los resultados posteriores no convierten retrospectivamente una prueba simulada en física.

## Cierre pendiente y límites

- Continuar consolidando los ensayos en NAO y su evidencia reproducible; la repetición física actual en Pepper depende de que vuelva a estar disponible.
- Mantener en espera la optimización de Whisper y la evaluación formal de Vosk. La comparación existente con/sin Whisper permanece como resultado del equipo y las condiciones ensayadas.
- Fijar los commits, modelos, dependencias, perfiles y procedimiento de la versión entregable. Documentar qué contrato debe cumplir cada adaptador de otro robot.
- Contrastar el alcance final con la propuesta aprobada, especialmente las referencias iniciales a ROS4HRI, obstáculos y gestos. Los mensajes propios de detección y la parada por pérdida visual no acreditan por sí solos ROS4HRI ni evitación de obstáculos.
- Conservar los defectos de cierre observados como limitaciones: `Ctrl+C` puede producir `application_failed` por cancelación, una carrera `InvalidHandle` y, con Whisper, un aborto del worker. El acuse de parada y la liberación son evidencia de software; no son una medición de frenado físico.

La arquitectura permite adaptar proveedores sin cambiar la lógica de alto nivel. La compatibilidad efectiva con cada nuevo robot requiere comprobar sus interfaces y comportamiento; no se promete funcionamiento físico automático por cambiar el nombre del perfil.

