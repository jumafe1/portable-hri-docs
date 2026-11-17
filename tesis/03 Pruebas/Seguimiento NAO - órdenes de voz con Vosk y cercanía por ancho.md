# Seguimiento en NAO: órdenes de voz con Vosk y cercanía por ancho de caja

Fecha de consolidación: 17 de noviembre de 2026. Ensayos: 11 y 17 de noviembre de 2026, hora local de Bogotá. Relacionado con [[Proyecto]] y [[Seguimiento NAO - pruebas con y sin Whisper]].

## Objetivo y resultado

Documentar las pruebas de la semana del 11 al 17 de noviembre: los fallos observados el 11 de noviembre con la aplicación integrada, su diagnóstico a partir de los registros, los dos cambios hechos al seguimiento y la sesión física del 17 de noviembre con órdenes de voz.

**Resultado:** el 17 de noviembre NAO siguió a una persona durante unos 150 s, iniciando con «Nao, sígueme» y deteniéndose con «Nao, detente», con una sola orden de lanzamiento. El autor reportó que la sesión funcionó perfectamente. El registro de esa sesión coincide: 129,5 s en seguimiento, dos órdenes aceptadas, voz disponible toda la sesión y ninguna espera por imágenes antiguas.

Es una sesión, no una campaña. No se midió la distancia a la que NAO se detiene, el frenado ni la precisión del reconocimiento.

## Qué falló el 11 de noviembre

Ese día la aplicación no consiguió caminar en dos sesiones registradas con `hri_diagnostics`.

| Sesión | Qué se observó | Qué indica el registro |
| --- | --- | --- |
| 17:10, con Vosk | NAO respondió «Te voy a seguir» y no caminó. | Las detecciones llegaron a cerca de 1 Hz con huecos de hasta 2 s. En el segundo 21 dejaron de llegar durante 18,2 s; a los 4 s el worker de voz reportó `audio_capture_timeout`. Desde ahí el motivo de parada fue `voice_unavailable` durante 62 s. |
| 17:15, sin voz | NAO no caminó. | Cero imágenes recibidas. El driver mostró `Camera Handle is empty - cannot retrieve image`. |

Tres conclusiones del análisis, hecho el 17 de noviembre sobre esos registros:

1. **No fue competencia entre escucha y seguimiento.** En la sesión de las 17:10 la CPU media del sistema fue 26 %; en los segundos alrededor del corte estuvo entre 11 % y 40 %, y el worker de Vosk usó como máximo el 20 % de un núcleo. Durante el corte, YOLO estuvo en 0 % porque no recibía imágenes.
2. **Cámara y micrófono se cortaron a la vez** mientras el computador estaba casi libre. Eso sitúa el corte antes de esta aplicación: robot, driver o red. No se identificó cuál; la hipótesis de la red Wi-Fi sigue abierta.
3. **La aplicación no se recupera de un corte de audio.** El worker falla tras 3 s sin audio válido y la sesión de voz no se reinicia. Con órdenes de voz habilitadas, eso mantiene detenido al robot hasta relanzar. Este punto **sigue sin cambiar** por decisión del autor.

El mismo 11 de noviembre se comparó el flujo de imágenes antes y después de cambiar la suscripción de YOLO a `BEST_EFFORT`: 1,75 Hz con 11 huecos mayores de 0,75 s en 30 s, frente a 2,50 Hz con 5 huecos. Fueron dos sesiones secuenciales; la diferencia no se atribuye solo a ese ajuste. [Comparación conservada][qos].

## Hallazgo: la altura de la caja se satura con la cámara de NAO

El seguimiento estimaba la cercanía con la altura de la caja de la persona respecto a la altura de la imagen, con objetivo 0,75. Al revisar las 1143 cajas de una sola persona grabadas en las sesiones del 4 y el 11 de noviembre se encontró lo siguiente:

| Situación en los registros (valores típicos) | Altura de caja / imagen | Ancho de caja / imagen |
| --- | --- | --- |
| NAO avanzando | 0,55 – 0,69 | 0,16 – 0,20 |
| Zona donde dejaba de avanzar | 0,70 – 0,75 | 0,18 – 0,23 |
| Persona cerca | 0,97 – 0,99 | 0,45 – 0,55 |

La cámara de NAO está baja, así que la caja de una persona de pie llega al borde de la imagen cuando todavía está lejos. Desde ahí la altura ya no cambia, mientras que el ancho sigue creciendo. Además, el controlador devolvía movimiento cero en ambos ejes cuando la caja tocaba cualquier borde. El efecto conjunto era que NAO solo caminaba con la persona lejos y se detenía lejos.

## Cambios realizados el 17 de noviembre

Los dos cambios están en el controlador puro del seguimiento (`follow_controller.py`) y en el perfil del robot. No se modificaron contratos, proveedores ni el driver.

**1. Cercanía por ancho de caja.** El perfil `nao.yaml` fija `target_width_ratio: 0.33`, es decir, la caja ocupa un tercio del ancho de la imagen (unos 106 px de 320).

| Ancho de caja / imagen | Comportamiento |
| --- | --- |
| Menor que 0,30 | Avanza; la velocidad crece con la distancia hasta el máximo de 0,10 m/s, que se alcanza con ancho 0,18 o menor. |
| Entre 0,30 y 0,36 | No avanza; gira si hace falta centrar. |
| Mayor que 0,36 | Demasiado cerca: no avanza, solo gira para centrar. |

Una caja cortada arriba o abajo se acepta, porque su ancho y su centro siguen siendo válidos. Una caja cortada a izquierda o derecha sigue deteniendo avance y giro. El valor 0,33 depende del campo de visión horizontal de la cámara, por eso vive en el perfil de cada robot y no en el controlador; con `target_width_ratio: 0` un perfil conserva el criterio anterior por altura.

**2. Avance lento mientras corrige la dirección.** Antes NAO dejaba de avanzar cuando la persona se alejaba 60 px del centro y giraba en el sitio. Ahora:

| Persona respecto al centro (imagen de 320 px) | Avance |
| --- | --- |
| Hasta ±24 px | Velocidad completa según la cercanía. |
| De ±24 a ±60 px | Baja progresivamente hasta un tercio. |
| Más de ±60 px | Se mantiene en un tercio, como máximo unos 0,033 m/s, mientras gira. |

Se conservan sin cambios: tres observaciones para adquirir o reanudar, parada con ninguna o varias personas, parada por imagen de más de 0,75 s, límites de 0,10 m/s y ±0,1 rad/s, y el watchdog del proveedor de movimiento.

La idea de usar el ancho y de no detener el avance al girar proviene de revisar un controlador de seguimiento de otro proyecto, escrito para ROS 1. No se copió ese código: no se adoptaron su selección de la persona más cercana, sus pulsos de velocidad sin watchdog ni sus velocidades.

## Comprobaciones de software

Antes de la prueba física se ejecutaron, sin robot ni red:

- 61 pruebas del controlador, incluidas las nuevas del modo por ancho y del avance a un tercio.
- 221 pruebas de sesión, movimiento, cámara, órdenes de voz, launch y diagnóstico.
- Repaso sin conexión de las 1143 cajas grabadas: con el criterio por altura el controlador proponía avance en 528; con ancho 0,33, en 659; con ancho 0,33 y avance a un tercio mientras gira, en 792. Cada caja se evaluó de forma aislada; no es una prueba física.

Todas las pruebas pasaron. Usan dobles de software; no sustituyen la sesión física.

## Sesión física del 17 de noviembre

Con el driver iniciado aparte, se lanzó:

```bash
ros2 launch hri_reference_app aplicacion_hri.launch.py record_diagnostics:=true
```

Este comando inicia YOLO, el worker de Vosk, Capabilities2 y la aplicación, con movimiento y escucha habilitados. El seguimiento arranca en pausa hasta la orden de voz.

**Criterio:** que NAO empiece a seguir tras «Nao, sígueme», avance y gire hacia la persona, y se detenga tras «Nao, detente», sin relanzar.

| Momento | Evento registrado |
| --- | --- |
| 14,0 s | Orden de seguir aceptada; NAO se mantiene detenido y responde con `Speak`. |
| 19,0 s | Empieza a seguir, tras la respuesta, el margen contra eco y tres observaciones nuevas. |
| 170,4 s | Orden de pausa aceptada. |
| 173,4 s | Queda en pausa. |
| 179,8 s | El operador termina con `Ctrl+C`. |

| Medida | Valor |
| --- | ---: |
| Duración del observador | 179,77 s |
| Tiempo observado en seguimiento (`preview_following`) | 129,54 s |
| Órdenes de voz aceptadas | 2 |
| Tiempo con voz no disponible | 0,05 s, al arrancar |
| Detecciones recibidas en `/hri/people` | 829 |
| Frecuencia reciente de `/hri/people`, últimos 30 s | 5,01 Hz |
| Mayor hueco entre detecciones | 0,55 s |
| Esperas por imagen antigua | 0 |
| Recuperaciones tras perder a la persona o ver varias | 6 |
| CPU media del sistema, excluyendo los primeros 10 s | 64,5 % |

Sobre las 595 imágenes con una sola persona elegible:

| Medida | Valor |
| --- | ---: |
| Imágenes con propuesta de avance | 417 |
| Ancho de caja / imagen al avanzar (mínimo, mediana, máximo) | 0,13 – 0,23 – 0,30 |
| Ancho de caja / imagen al quedarse quieto en el objetivo | 0,30 – 0,32 |
| Cajas cortadas arriba o abajo | 262 |
| De ellas, con propuesta de avance | 136 |
| Avances con la persona a 60 px o más del centro | 137 |
| Velocidad máxima en esos avances | 0,033 m/s |

Fuente numérica: [resumen de la sesión][width-voice], calculado a partir de `summary.json` y `events.jsonl` de la ejecución.

**Interpretación:** el registro confirma que los dos cambios actuaron durante el movimiento real. Con el criterio anterior, las 262 cajas cortadas arriba o abajo habrían producido movimiento cero; ahora 136 de ellas tuvieron propuesta de avance. El avance a un tercio se aplicó en 137 imágenes. Las seis recuperaciones muestran que la parada por persona ausente o por varias personas sigue activa. Las imágenes llegaron a 5 Hz sin huecos mayores de 0,75 s, muy distinto de las sesiones del 11 de noviembre; ese cambio de condiciones no se debe a la aplicación.

**Observación del autor:** la sesión funcionó perfectamente. Es una confirmación cualitativa del movimiento, el seguimiento y las dos órdenes de voz.

## Fallos y límites

- **Una sola sesión.** No hubo comparación controlada contra el criterio por altura el mismo día y en la misma escena.
- **Distancia no medida.** 0,33 es una fracción del ancho de la imagen, no metros. La estimación de unos 1,3 m sale de un cálculo con el campo de visión nominal de la cámara y no se verificó con cinta.
- **Recuperación de voz sin cambios.** En esta sesión el audio no se cortó, así que el fallo del 11 de noviembre no se ejercitó. Un corte de más de 3 s volvería a dejar detenido al robot hasta relanzar.
- **Disponibilidad de imagen fuera de alcance.** Los cortes de cámara del 11 de noviembre no tienen causa identificada y el driver no se modifica desde este proyecto.
- **Cierre.** Al terminar con `Ctrl+C`, la aplicación devolvió código 1; YOLO, el worker de Vosk y el observador terminaron limpiamente. Es el defecto de cierre ya registrado, no un fallo durante el seguimiento.
- **Sin identidad.** Tras una recuperación no se garantiza que la persona seguida sea la misma.
- **Evaluación formal de Vosk.** Sigue en espera: no hay medición de aciertos, falsas activaciones ni distancia de habla.
- **Pepper.** Sigue fuera de funcionamiento; estas pruebas son solo de NAO.

## Trazabilidad

Los registros locales de las sesiones están bajo `~/.ros/log/`:

| Sesión | Subdirectorio de ejecución |
| --- | --- |
| 11 de noviembre, con Vosk, sin caminar | `2026-11-11-17-10-46-137435-robotica-24261/hri_diagnostics/` |
| 11 de noviembre, sin voz, sin imágenes | `2026-11-11-17-15-55-912443-robotica-25436/hri_diagnostics/` |
| 17 de noviembre, seguimiento con órdenes de voz | `2026-11-17-11-57-39-339999-robotica-36471/hri_diagnostics/` |

Cada directorio conserva `summary.json` y `events.jsonl`. El observador registra decisiones, tiempos, CPU y estado de voz; no guarda imágenes, audio ni texto reconocido.

Los cambios de Vosk, del perfil y del controlador están en la rama `perf/whisper-follow-cpu`: commit `360065e` del repositorio de proveedores y commit `910c05f` del sistema de referencia, ambos del 17 de noviembre. Los resultados enlazados en esta nota se fijan a ese commit del sistema de referencia. Los commits se crearon en la copia local; los enlaces abrirán cuando esa rama se publique en GitHub. La sesión física se ejecutó con ese mismo código antes de versionarlo.

[qos]: https://github.com/jumafe1/portable-hri-reference-system/blob/910c05faed6aa0c4b02872cb7f4f65ebf25ce669/results/follow_stream_qos_comparison_20261111.json
[width-voice]: https://github.com/jumafe1/portable-hri-reference-system/blob/910c05faed6aa0c4b02872cb7f4f65ebf25ce669/results/follow_width_voice_20261117.json
