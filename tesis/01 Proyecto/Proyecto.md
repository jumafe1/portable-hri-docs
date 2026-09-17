# Proyecto

## Objetivo

Construir una arquitectura modular sobre ROS 2 que permita ejecutar una misma aplicación de interacción humano-robot en NAO y Pepper, cambiando configuración y proveedores o adaptadores específicos, y conservando la lógica de alto nivel.

La propuesta académica y el contexto técnico completo se conservan fuera de este vault público. Estas notas reúnen las decisiones, comandos y evidencias reproducibles y se actualizan cuando una prueba cambia las hipótesis iniciales.

## Organización del trabajo

Este vault se mantiene en tres carpetas: `01 Proyecto` para alcance y decisiones, `02 Entorno` para instalación y uso, y `03 Pruebas` para experimentos y resultados. Cada nota de prueba debe incluir objetivo, fecha, comando repetible, criterio, evidencia, fallos y límites. Actualizar la nota correspondiente al implementar; crear una nueva solo para un experimento o decisión diferente.

Estado actual: [[Docker]] preparado; [[ROS 2]] verificado; [[Capabilities2]] evaluado con un fallo de reporte de errores pendiente de resolver; acceso físico a NAO y Pepper y recorridos `Speak` mediante Capabilities2 registrados en [[Semana 7 - Verificación NAO]]. La primera aplicación YASMIN ya recorre la arquitectura contra servicios simulados y está pendiente de repetición física. Los resultados técnicos versionados viven en `portable-hri-reference-system`; el vault conserva su interpretación y los comandos.

Caracterización documental disponible en [[Semana 6 - Capacidades y servicios]]: matriz NAO/Pepper, interfaces, candidatos externos, brechas de integración y comprobaciones pendientes del laboratorio. Consultar esa nota para distinguir disponibilidad identificada en código de funcionamiento físico probado.

La verificación de semana 7 confirmó conexión ROS 2, sensores seleccionados y voz audible en NAO y Pepper. Después de las llamadas directas, Capabilities2 administró el contrato común y el proveedor `NaoSpeak` en ambos robots; Pepper reutilizó el proveedor mediante remapeo. La aplicación YASMIN se verificó localmente y todavía no se presenta como prueba física; consultar [[Semana 7 - Verificación NAO]].

| Carpeta | Uso |
| --- | --- |
| `docs/` | Propuesta, contexto técnico y bibliografía. |
| `docs/tesis/` | Este vault: registro de implementación y pruebas. |
| `repos/` | Repositorios externos de referencia. |
| `repos_tesis/` | Código propio del proyecto. |
| `docker/` | Entorno reproducible de desarrollo. |

## Decisiones iniciales

- Usar Ubuntu 24.04 ARM64 y ROS 2 Jazzy dentro de Docker para las primeras pruebas en el Mac; ver [[Docker]]. Esta elección experimental no confirma todavía compatibilidad con el laboratorio.
- Comprobar primero comunicación ROS 2 sin robots; ver [[ROS 2]].
- Evaluar registro, selección y ciclo de vida de proveedores con Capabilities2 antes de depender de él; ver [[Capabilities2]].
- Los proveedores ficticios permiten validar software. La integración con NAOqi y el comportamiento físico requieren pruebas posteriores con NAO y Pepper.
- Los contratos comunes definen la comunicación funcional. Capabilities2 administra proveedores; no se presupone que deba transportar todos los datos.

## Pendiente de decidir con evidencia

El computador del laboratorio fue identificado como Ubuntu 24.04.2 x86_64 con ROS 2 Jazzy, Cyclone DDS y el workspace NAOqi de SinfonIA. Capabilities2 y el proveedor `NaoSpeak` ya fueron compilados en un overlay del proyecto; el siguiente paso es actualizarlo con `hri_reference_app` y repetir físicamente la máquina YASMIN. El autor también reporta detección de obstáculos disponible en el laboratorio; su implementación exacta continúa pendiente de verificación.

La revisión local identifica sonar habilitado en las configuraciones NAO y Pepper, láser habilitado para Pepper y deshabilitado para NAO. El driver implementa lecturas de distancia y el manifiesto de bringup referencia `SinfonIAUniandes/naoqi_navigation`, que no está entre los tres repositorios locales. Esto orienta la caracterización; no demuestra todavía evitación de obstáculos ni navegación funcional en hardware.

Permanecen por fijar las versiones o commits del experimento final, la identidad definitiva del proveedor de Pepper y los contratos de percepción, navegación, obstáculos y gestos. `Speak`, Capabilities2 y YASMIN ya tienen un primer incremento verificable; las nuevas capacidades deben conservar la misma separación entre aplicación, contrato, proveedor y driver.
