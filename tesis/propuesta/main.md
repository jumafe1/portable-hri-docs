:::: titlepage
::: center
**Arquitectura modular de capacidades para aplicaciones de interacción
humano-robot con NAO y Pepper sobre ROS 2**\
**Proyecto de Grado: Propuesta**\
**Julián Mauricio Ferreira Velásquez**\
**Autor**\
**Mario Fernando De la Rosa Rosero**\
**Profesor Asesor**\
**19 de agosto de 2026**\
**Universidad de los Andes**\
**Departamento de Ingeniería de Sistemas y Computación**\
**Bogotá, Colombia**
:::
::::

::: center
**Capítulo 1: Introducción**
:::

**1.1 Motivación**

Existe un interés creciente en utilizar robots humanoides para apoyar
actividades realizadas por personas en contextos educativos,
asistenciales, domésticos y de servicio. Plataformas como NAO y Pepper
ofrecen cámaras, micrófonos, parlantes, articulaciones y mecanismos de
locomoción que permiten investigar interacción humano-robot (HRI). Sin
embargo, transformar estos recursos en aplicaciones robustas suele
requerir integrar numerosas herramientas de software: transcripción de
audio, síntesis de voz, procesamiento de imágenes, percepción de
personas y objetos, navegación, detección de obstáculos, control
corporal, manipulación básica y generación de gestos.

Aunque existen soluciones de calidad para varias de estas funciones, con
frecuencia se distribuyen como componentes aislados, utilizan interfaces
diferentes o se construyen para un robot y un escenario particular. En
consecuencia, nuevos proyectos deben repetir tareas de integración,
adaptar formatos de datos y programar directamente contra las APIs del
hardware. Esta situación dificulta la reutilización y hace que una
aplicación desarrollada para un robot no pueda trasladarse con facilidad
a otro, incluso cuando ambos pertenecen al mismo ecosistema tecnológico.

NAO y Pepper comparten servicios del ecosistema NAOqi y cuentan con
mecanismos de acceso desde ROS 2. Esto crea una oportunidad para diseñar
una plataforma común en la que las aplicaciones de alto nivel no
dependan directamente del modelo de robot. La aplicación debería
solicitar capacidades abstractas, como escuchar, hablar, detectar una
persona, orientarse, navegar o ejecutar un gesto, mientras una capa
inferior selecciona la implementación apropiada para NAO o Pepper. De
esta manera, los desarrollos posteriores podrían concentrarse en
funcionalidades más complejas sin volver a resolver la comunicación con
el robot ni la coordinación elemental de sus capacidades.

La motivación del proyecto es, por tanto, construir una base técnica
sólida, extensible y verificable sobre ROS 2. Esta base no pretende
reemplazar algoritmos existentes, sino integrarlos mediante contratos
estables, proveedores intercambiables y herramientas de prueba. Su
utilidad se comprobará mediante aplicaciones comunes ejecutadas sobre
los dos robots disponibles.

**1.2 Enunciado del problema**

Actualmente existe interés en emplear robots humanoides para apoyar
actividades desarrolladas por personas. Para facilitar la construcción
de estas aplicaciones se requieren herramientas computacionales que
funcionen con robots humanoides y permitan desarrollar interacción
humano-robot. Entre las capacidades fundamentales se encuentran la
transcripción de audio, el procesamiento de visión e imágenes, la
navegación, la detección de obstáculos, la manipulación y la generación
de gestos. El desarrollo debe realizarse sobre ROS 2 y se dispone de un
robot NAO y un robot Pepper para las pruebas.

El problema no se limita a la ausencia de algoritmos para cada
capacidad. Existen paquetes de ROS 2 y herramientas externas que
resuelven individualmente varias de estas funciones. La dificultad
principal es la falta de una arquitectura común que permita
incorporarlas de forma coherente, sustituir sus implementaciones,
conocer cuáles están disponibles en cada robot y reutilizar las mismas
aplicaciones de alto nivel en NAO y Pepper.

Si una aplicación se conecta directamente con servicios de NAOqi,
nombres particulares de tópicos o detalles de un algoritmo, queda
fuertemente acoplada al robot y al componente utilizado. Cambiar de NAO
a Pepper, reemplazar un sistema de reconocimiento de voz o introducir un
nuevo detector puede requerir modificar toda la aplicación. Además, NAO
y Pepper presentan diferencias físicas que impiden suponer una
equivalencia total: Pepper dispone de una base móvil y una tableta,
mientras NAO utiliza locomoción bípeda; sus sensores, articulaciones y
comportamientos de movimiento tampoco son idénticos.

Por lo tanto, el reto consiste en establecer el nivel correcto de
abstracción. Se busca que la lógica de interacción y la descripción de
las capacidades sean comunes, mientras las diferencias inevitables se
encapsulan en proveedores específicos. También se requiere que el
sistema pueda declarar capacidades no disponibles, cancelar ejecuciones,
reportar errores, recuperarse de fallas y facilitar pruebas sin depender
permanentemente de los robots físicos.

**1.3 Discusión de lo que debería ser la solución**

La solución propuesta consiste en una arquitectura modular basada en
capacidades o *skills* sobre ROS 2. La arquitectura separará las
aplicaciones HRI, la orquestación de comportamientos, los contratos
comunes de capacidades y los adaptadores de hardware. Una aplicación
podrá combinar operaciones como escuchar una instrucción, detectar una
persona, desplazarse u orientarse, producir una respuesta y ejecutar un
gesto, sin invocar directamente APIs específicas de NAO o Pepper.

Cada capacidad deberá contar con una descripción estable de entradas,
salidas, estados de ejecución y errores. Cuando sea pertinente, también
deberá expresar precondiciones, condiciones que deben mantenerse durante
la ejecución y postcondiciones. Por ejemplo, una capacidad de navegación
puede exigir que la localización y los sensores de seguridad estén
disponibles, y verificar que el destino fue alcanzado dentro de una
tolerancia. Una capacidad de transcripción puede exigir la
disponibilidad del canal de audio y finalizar con texto reconocido, un
*timeout* o un error explícito.

La descripción común se implementará mediante uno o más proveedores.
Algunas implementaciones podrán compartirse totalmente entre los robots,
como un nodo externo de detección de objetos que procese imágenes
estandarizadas. Otras requerirán adaptadores: la capacidad de
orientación puede utilizar la base móvil en Pepper y una combinación de
cabeza y cuerpo en NAO. Cuando una capacidad no exista en un robot, el
sistema deberá indicarlo y permitir que la aplicación seleccione una
alternativa o degrade su comportamiento de forma controlada.

Esta separación está respaldada por SkiROS2, que diferencia la
descripción semántica de una *skill* de sus implementaciones
dependientes del hardware y utiliza precondiciones, condiciones de
mantenimiento y postcondiciones [@skiros2]. Capabilities2 traslada a ROS
2 el concepto de interfaces, proveedores e interfaces semánticas para
representar y ejecutar capacidades de manera extensible
[@capabilities2]. Sin embargo, la adopción directa de cualquiera de
estos sistemas deberá decidirse mediante pruebas técnicas, pues SkiROS2
fue presentado con una implementación principal en ROS 1 y un port a ROS
2 en desarrollo, mientras Capabilities2 es reciente y todavía tiene una
adopción limitada.

En el nivel de acceso al hardware se utilizarán como punto de partida
`naoqi_driver2` y los paquetes desarrollados por SinfonIA. Encima de
esta capa se podrán integrar implementaciones existentes, como
`whisper_ros` para transcripción, `yolo_ros` para visión, el TTS de
NAOqi o `piper_ros` para síntesis, y Nav2 cuando la configuración física
del robot lo permita. ROS4HRI se considera una referencia para
normalizar la representación de rostros, cuerpos, voces y personas.
YASMIN o un mecanismo equivalente permitirá componer las capacidades en
comportamientos observables y cancelables.

La arquitectura deberá incluir además descripciones de capacidades por
robot, espacios de nombres, configuración, gestión del ciclo de vida,
diagnóstico, registro de eventos, simulación o *mocks*, pruebas
unitarias e integración mediante *rosbags*. La documentación deberá
explicar cómo añadir un nuevo proveedor, sustituir un algoritmo o
incorporar otra plataforma robótica.

La validación principal consistirá en ejecutar una misma aplicación HRI
de alto nivel en NAO y Pepper, conservando sin cambios la lógica de la
aplicación y reemplazando solamente los proveedores específicos del
hardware. Este criterio permitirá demostrar portabilidad real, en lugar
de limitar la evaluación a comprobar que cada robot ejecuta funciones
independientes.

<figure id="fig:arquitectura" data-latex-placement="htbp">
<span class="image placeholder"
data-original-image-src="arquitectura_portable.pdf"
data-original-image-title="" width="96%"></span>
<figcaption>Arquitectura preliminar orientada a la reutilización entre
NAO y Pepper. Elaboración propia.</figcaption>
</figure>

**1.4 Reconocimientos y Agradecimientos**

El desarrollo de este proyecto de grado cuenta con el acompañamiento del
profesor Mario Fernando De la Rosa Rosero, del Departamento de
Ingeniería de Sistemas y Computación de la Universidad de los Andes, en
Bogotá, Colombia. Su orientación académica y técnica será fundamental
para delimitar el alcance, evaluar las decisiones arquitectónicas y
conducir el proceso investigativo y de desarrollo. Asimismo, se agradece
a David Cuevas Alba por su apoyo y capacitación en los fundamentos
técnicos necesarios para el uso y la programación de los robots
humanoides. También se reconoce el respaldo del Departamento de
Ingeniería de Sistemas y Computación y del grupo SinfonIA, cuyos
recursos y desarrollos previos constituyen una base importante para la
realización de las pruebas con NAO y Pepper.

::: center
**Capítulo 2: Descripción General**
:::

**2.1 Objetivos**

El proyecto busca establecer una plataforma base para el desarrollo de
aplicaciones de interacción humano-robot sobre ROS 2. La plataforma
deberá encapsular las diferencias entre NAO y Pepper, reutilizar
componentes existentes para las capacidades fundamentales y permitir que
trabajos posteriores incorporen algoritmos más complejos sin modificar
la lógica común de las aplicaciones ni reconstruir la integración con el
hardware.

**2.1.1 Objetivo General**

Diseñar, implementar y evaluar una arquitectura modular basada en
capacidades sobre ROS 2 que permita reutilizar las mismas aplicaciones
de interacción humano-robot en NAO y Pepper mediante interfaces comunes,
proveedores específicos para cada plataforma e implementaciones
iniciales de audio, percepción visual, navegación y detección de
obstáculos, manipulación básica y generación de gestos.

**2.1.2 Objetivos específicos**

**2.2 Estado del arte**

El desarrollo de software robótico reutilizable ha evolucionado desde
arquitecturas estrechamente ligadas al hardware hacia enfoques basados
en componentes, capacidades y *skills*. En estos enfoques, las
aplicaciones expresan qué debe hacer el robot, mientras módulos
inferiores determinan cómo ejecutar la operación en una plataforma
específica. Esta separación es especialmente importante para el presente
proyecto porque NAO y Pepper comparten el ecosistema NAOqi, pero
difieren en locomoción, sensores, actuadores y capacidades exclusivas.

Mayr, Rovida y Krueger presentan SkiROS2, una plataforma de control
basada en *skills* que combina planificación automática, ejecución
reactiva mediante Behavior Trees y un modelo semántico del mundo
[@skiros2]. Su formulación define parámetros y precondiciones,
condiciones durante la ejecución y postcondiciones para cada *skill*. Un
aporte directamente relacionado con este proyecto es la separación entre
la descripción de una capacidad y sus implementaciones: distintos
dispositivos pueden implementar la misma descripción, y el sistema puede
escoger la implementación compatible con el hardware. Este mecanismo
constituye un antecedente sólido para compartir comportamientos entre
NAO y Pepper. No obstante, el artículo indica que la versión disponible
se integraba con ROS 1 y que el port a ROS 2 estaba en desarrollo. El
repositorio principal aún conserva instrucciones de construcción con
`catkin` y documentación centrada en Melodic y Noetic. En consecuencia,
SkiROS2 es altamente pertinente como modelo conceptual, pero su adopción
directa requiere una prueba de viabilidad en la distribución ROS 2
seleccionada.

Desde una perspectiva más reciente y nativa de ROS 2, Pritchard et al.
presentan Capabilities2, una reimplementación del antiguo sistema
*Capabilities* para representar y ejecutar capacidades robóticas
[@capabilities2]. El sistema distingue interfaces, proveedores e
interfaces semánticas y agrega una arquitectura de plugins. Esta
separación permite registrar una capacidad independientemente del nodo
que la implementa y seleccionar proveedores durante la ejecución. En el
contexto de NAO y Pepper, una interfaz común de habla podría ser
implementada por NAOqi o Piper, mientras una interfaz de locomoción
podría utilizar proveedores distintos. Capabilities2 no incluye por sí
mismo las capacidades de HRI ni adaptadores para estos robots, y su
adopción pública todavía es limitada; sin embargo, es uno de los
candidatos más cercanos para evitar el desarrollo de un registro de
capacidades completamente nuevo.

En relación directa con el hardware disponible, Bono et al. proponen
Open Access NAO (OAN), un framework ROS 2 para experimentación HRI con
NAO V6 [@oan]. OAN instala un sistema operativo basado en Ubuntu en el
robot y utiliza ROS 2 de manera nativa, evitando las APIs de alto nivel
del fabricante. El framework reúne caminata, reproducción y enseñanza de
movimientos, captura de cámaras y audio, reconocimiento y síntesis de
voz, detección de caras y objetos y conversación mediante modelos
generativos. También incorpora simulación en Webots con el propósito de
ejecutar el mismo código en el robot real y en el simulador. OAN
demuestra que las capacidades fundamentales solicitadas pueden
organizarse como módulos ROS 2 extensibles. Sin embargo, está diseñado
únicamente para NAO V6, requiere una modificación profunda de su
plataforma de software y no aborda la interoperabilidad con Pepper. Por
ello constituye un antecedente funcional directo, pero no resuelve la
arquitectura común de los dos robots.

González-Santamarta et al. presentan MERLIN2, una arquitectura cognitiva
híbrida completamente integrada con ROS 2 para generar, planificar,
controlar y monitorizar comportamientos autónomos [@merlin2]. MERLIN2
distribuye el sistema en capas de misión, planificación, ejecución y
reacción. En la capa reactiva ubica las capacidades elementales, como
navegación, reconocimiento de objetos, conversión de voz a texto y
síntesis de voz; en capas superiores combina esas capacidades en
acciones y planes. La implementación integra YASMIN, Nav2, herramientas
PDDL y `yolo_ros`, y fue evaluada en simulación y en un TIAGo real
mediante una tarea de RoboCup@Home. El trabajo muestra cómo una base de
skills puede soportar proyectos complejos de autonomía y constituye una
guía valiosa para separar capacidades, acciones y planificación. Sin
embargo, no ofrece adaptadores para NAO o Pepper y adoptar toda su
infraestructura cognitiva podría exceder el alcance inicial del
proyecto.

Cooper et al. introducen una arquitectura ROS 2 abierta y un simulador
para robots sociales situados [@cooper]. El sistema combina percepción
multimodal mediante ROS4HRI, una base de conocimiento, modelos de
lenguaje y un controlador basado en intenciones para ejecutar tareas
paralelas y secuenciales. Este trabajo aporta un referente
específicamente orientado a HRI y muestra cómo integrar percepción,
razonamiento y comportamiento sobre interfaces abiertas. Su uso de
ROS4HRI es relevante porque normaliza la representación de rostros,
cuerpos, voces y personas, evitando que las aplicaciones dependan del
detector concreto. No obstante, la demostración utiliza capacidades
simuladas para parte de la navegación y la manipulación y no valida la
arquitectura sobre NAO o Pepper.

Como complemento práctico, el tutorial de Lemaignan et al. muestra cómo
ensamblar un robot social interactivo con ROS4HRI, ROS 2 y modelos de
lenguaje [@ros4hritutorial]. ROS4HRI implementa las convenciones de
REP-155 y proporciona una representación compartida de humanos
percibidos. Este estándar no reemplaza un sistema de capacidades, pero
sí evita incompatibilidades entre módulos de percepción y aplicaciones.
En la arquitectura propuesta, los proveedores de visión o voz podrán
publicar información bajo estas convenciones para que los
comportamientos superiores sean independientes de YOLO, un detector
facial o un sistema particular de identificación de personas.

La coordinación de las capacidades requiere un mecanismo de ejecución.
YASMIN fue desarrollado para definir comportamientos robóticos mediante
máquinas de estados jerárquicas en ROS 2 y proporciona implementaciones
para Python y C++, estados para acciones, servicios y tópicos, un
*blackboard* compartido y herramientas de visualización [@yasmin]. Su
función en el proyecto no sería ocultar diferencias de hardware, sino
componer capacidades comunes en aplicaciones como escuchar una
instrucción, localizar una persona, desplazarse y responder. La
actividad reciente de su repositorio y su uso dentro de MERLIN2 lo
convierten en un candidato adecuado para la capa de orquestación.

En cuanto a infraestructura, `naoqi_driver2` ofrece el puente entre ROS
2 y NAOqiOS para NAO y Pepper [@naoqidriver]. El grupo SinfonIA ha
extendido este trabajo mediante un fork y un metapaquete de *bringup*
que agrupa acceso a audio, cámaras, movimiento, voz y otras funciones
[@sinfonia]. Estos desarrollos son el punto de partida local más
cercano, pero actúan principalmente como drivers y wrappers. Los
paquetes de navegación, percepción y manipulación no constituyen todavía
una abstracción completa e intercambiable: la navegación envuelve
funciones de NAOqi, la percepción se concentra en tracking y la
manipulación se refiere principalmente a postura, rigidez y control de
manos. Existe, por tanto, espacio para normalizar interfaces, declarar
las diferencias entre robots y agregar pruebas funcionales.

Para las implementaciones iniciales pueden reutilizarse repositorios
activos de ROS 2. `whisper_ros` integra `whisper.cpp`, detección de
actividad de voz y `audio_common` para transcripción local
[@whisperros]; `yolo_ros` ofrece detección, seguimiento, segmentación y
estimación de pose en dos dimensiones, además de variantes
tridimensionales cuando existe información de profundidad [@yoloros]; y
`piper_ros` proporciona síntesis de voz como alternativa al TTS nativo
de NAOqi [@piperros]. Estos repositorios son proveedores potenciales, no
la arquitectura completa. Su encapsulamiento detrás de contratos comunes
permitirá sustituirlos sin modificar las aplicaciones.

La revisión identifica una brecha concreta. SkiROS2 proporciona el
modelo de skills y selección por hardware, pero no una base ROS 2 madura
orientada a HRI; Capabilities2 ofrece mecanismos nativos de interfaces y
proveedores, pero no capacidades para NAO y Pepper; OAN integra
funciones HRI en NAO, pero no busca portabilidad hacia Pepper; MERLIN2 y
el framework de Cooper et al. muestran arquitecturas completas, pero
fueron validados en otras plataformas o en simulación. No se identificó
un trabajo reciente que combine una capa común de capacidades HRI en ROS
2 con implementaciones para NAO y Pepper y que evalúe explícitamente la
ejecución de una misma aplicación de alto nivel en ambos robots. Esta
combinación constituye el aporte propuesto.

<figure id="fig:antecedentes" data-latex-placement="htbp">
<span class="image placeholder"
data-original-image-src="mapa_antecedentes.pdf"
data-original-image-title="" width="96%"></span>
<figcaption>Relación entre los principales antecedentes y la
contribución propuesta. Elaboración propia.</figcaption>
</figure>

**2.3 Metodología**

**2.4 Cronograma**

::: center
**Capítulo 3: Referencias Bibliográficas**
:::

::: thebibliography
99

M. Mayr, F. Rovida y V. Krueger, "SkiROS2: A Skill-Based Robot Control
Platform for ROS," en *2023 IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS)*, pp. 6273--6280, 2023, doi:
[10.1109/IROS55552.2023.10342216](https://doi.org/10.1109/IROS55552.2023.10342216).
\[En línea\]. Disponible en: <https://arxiv.org/abs/2306.17030>.

M. Pritchard, K. Ratnayake, B. Gamage, M. Jayasuriya y D. Herath,
"Capabilities2 for ROS2: Advanced Skill-Based Control for Human-Robot
Interaction," en *2025 20th ACM/IEEE International Conference on
Human-Robot Interaction (HRI)*, pp. 1067--1071, 2025, doi:
[10.1109/HRI61500.2025.10973863](https://doi.org/10.1109/HRI61500.2025.10973863).

A. Bono, K. Brameld, L. D'Alfonso y G. Fedele, "Open Access NAO (OAN): a
ROS2-based software framework for HRI applications with the NAO robot,"
en *2024 33rd IEEE International Conference on Robot and Human
Interactive Communication (RO-MAN)*, 2024, doi:
[10.1109/RO-MAN60168.2024.10731252](https://doi.org/10.1109/RO-MAN60168.2024.10731252).
\[En línea\]. Disponible en: <https://arxiv.org/abs/2403.13960>.

M. Á. González-Santamarta, F. J. Rodríguez-Lera, C. Fernández-Llamas y
V. Matellán-Olivera, "A Hybrid Cognitive Architecture to Generate,
Control, Plan, and Monitor Behaviors for Interactive Autonomous Robots,"
*International Journal of Social Robotics*, vol. 17, pp. 3135--3151,
2025, doi:
[10.1007/s12369-024-01192-4](https://doi.org/10.1007/s12369-024-01192-4).

S. Cooper, R. Ros, S. Lemaignan, F. Gebellí, L. Ferrini y L. Juričić,
"Demonstration of an Open-Source ROS 2 Framework and Simulator for
Situated Interactive Social Robots," en *2025 20th ACM/IEEE
International Conference on Human-Robot Interaction (HRI)*, 2025, doi:
[10.1109/HRI61500.2025.10974109](https://doi.org/10.1109/HRI61500.2025.10974109).

S. Lemaignan, L. Ferrini, F. Gebellí, R. Ros, L. Juričić y S. Cooper,
"Hands-on: From Zero to an Interactive Social Robot Using ROS4HRI and
LLMs," en *2025 20th ACM/IEEE International Conference on Human-Robot
Interaction (HRI)*, 2025, doi:
[10.1109/HRI61500.2025.10974214](https://doi.org/10.1109/HRI61500.2025.10974214).

M. Á. González-Santamarta, F. J. Rodríguez-Lera, C. Fernández-Llamas, F.
Martín Rico y V. Matellán-Olivera, "YASMIN: Yet Another State MachINe
library for ROS 2," en *ROBOT2022: Fifth Iberian Robotics Conference*,
pp. 528--539, 2023, doi:
[10.1007/978-3-031-21062-4_43](https://doi.org/10.1007/978-3-031-21062-4_43).

ros-naoqi, "naoqi_driver2: ROS2 driver for NAO and Pepper robots,"
GitHub. \[En línea\]. Disponible en:
<https://github.com/ros-naoqi/naoqi_driver2>. \[Consultado:
19-ago-2026\].

SinfonIA Uniandes, "naoqi_bringup2_SinfonIA: ROS 2 metapackage for NAO
and Pepper," GitHub. \[En línea\]. Disponible en:
<https://github.com/SinfonIAUniandes/naoqi_bringup2_SinfonIA>.
\[Consultado: 19-ago-2026\].

M. Á. González-Santamarta, "whisper_ros: Speech-to-Text based on
whisper.cpp for ROS 2," GitHub. \[En línea\]. Disponible en:
<https://github.com/mgonzs13/whisper_ros>. \[Consultado: 19-ago-2026\].

M. Á. González-Santamarta, "yolo_ros: ROS 2 wrapper for Ultralytics YOLO
models," GitHub. \[En línea\]. Disponible en:
<https://github.com/mgonzs13/yolo_ros>. \[Consultado: 19-ago-2026\].

M. Á. González-Santamarta, "piper_ros: Text-to-Speech with Piper for ROS
2," GitHub. \[En línea\]. Disponible en:
<https://github.com/mgonzs13/piper_ros>. \[Consultado: 19-ago-2026\].

Collaborative Robotics Lab, "capabilities2," GitHub. \[En línea\].
Disponible en:
<https://github.com/CollaborativeRoboticsLab/capabilities2>.
\[Consultado: 19-ago-2026\].

A. Bono, "Open Access NAO (OAN)," GitHub. \[En línea\]. Disponible en:
<https://github.com/antbono/OAN>. \[Consultado: 19-ago-2026\].

MERLIN2-ARCH, "MERLIN2 cognitive architecture," GitHub. \[En línea\].
Disponible en: <https://github.com/MERLIN2-ARCH/merlin2>. \[Consultado:
19-ago-2026\].

ROS4HRI, "ROS4HRI: Bridging Human-Robot Interaction with ROS," GitHub.
\[En línea\]. Disponible en: <https://github.com/ros4hri>. \[Consultado:
19-ago-2026\].

ULE Robotics Group, "YASMIN (Yet Another State MachINe)," GitHub. \[En
línea\]. Disponible en: <https://github.com/uleroboticsgroup/yasmin>.
\[Consultado: 19-ago-2026\].
:::
