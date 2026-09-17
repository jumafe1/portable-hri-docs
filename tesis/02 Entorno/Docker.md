# Docker

Fecha de la verificación original: 2026-09-09. Fuente: `docker/README.md`; esta nota resume esa evidencia, sin atribuirla a una nueva ejecución.

## Preparación implementada

Los archivos `docker/Dockerfile` y `docker/compose.yaml` definen un servicio `dev` con Ubuntu 24.04 ARM64, ROS 2 Jazzy, compiladores C/C++, CMake, Git, colcon, rosdep y vcstool. Docker Desktop debe estar iniciado; no se necesita instalar ROS 2 en macOS.

El servicio tiene límites de 4 CPU y 4 GiB de RAM, utiliza el usuario `ubuntu` con sudo y `ROS_DOMAIN_ID=42`. No publica puertos. El dominio identifica el experimento y no proporciona aislamiento de seguridad.

| Ruta del contenedor | Persistencia |
| --- | --- |
| `/workspace/src` | Montaje de `repos_tesis/`, editable desde el Mac. |
| `/opt/reference_repos` | Montaje de `repos/`, solo lectura. |
| `/workspace/build` | Volumen Linux de compilación. |
| `/workspace/install` | Volumen Linux de instalación. |
| `/workspace/log` | Volumen Linux de registros. |

## Uso reproducible

Desde la raíz de `tesis`:

```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml up -d
docker compose -f docker/compose.yaml exec dev bash
```

La terminal interactiva carga ROS y el workspace cuando esté compilado. Para un comando no interactivo:

```bash
docker compose -f docker/compose.yaml exec -T dev bash -c 'source /opt/ros/jazzy/setup.bash && ros2 --help'
```

Detener y reanudar:

```bash
docker compose -f docker/compose.yaml stop
docker compose -f docker/compose.yaml up -d
```

`docker compose -f docker/compose.yaml down` elimina el contenedor y la red del proyecto, conservando los volúmenes. No añadir `-v` si se quieren conservar compilaciones y registros. Las dependencias permanentes deben incorporarse al Dockerfile; las instaladas manualmente pueden desaparecer al recrear el contenedor.

## Evidencia registrada

- Compose válido; construcción y arranque completados.
- Ubuntu 24.04.4 LTS, arquitectura `aarch64`, ROS `jazzy`, usuario `ubuntu` UID 1000.
- Herramientas disponibles e importación de `rclpy` correcta.
- Límites de recursos, montaje de referencias de solo lectura y persistencia de código y volúmenes comprobados tras recrear el contenedor.
- Imagen de desarrollo mostrada con 1,44 GB; esta cifra excluye el resto del almacenamiento de Docker y cachés.
- Advertencia de deprecación de `pkg_resources` en rosdep, sin impedir su actualización ni consulta de versión.

La imagen base está fijada por digest en el Dockerfile; las dependencias apt y rosdep pueden variar al reconstruir en otra fecha. No hay type-checker ni ESLint aplicable a estos archivos de infraestructura; se verificaron configuración, construcción y ejecución.

## Red host en macOS (2026-09-09)

El usuario habilitó **Enable host networking** en Docker Desktop. Se agregó `network_mode: host` a `dev`, se validó con `docker compose -f docker/compose.yaml config --quiet` y se recreó con `docker compose -f docker/compose.yaml up -d --force-recreate dev`, sin reconstruir la imagen.

Inspección posterior: `State=running Network=host`, mismos montajes y volúmenes, `ros2 --help` operativo, Jazzy y dominio 42. No hay type-checker ni ESLint aplicable al cambio YAML/Markdown.

La comunicación LAN sigue pendiente: el usuario ejecutará `ros2 multicast receive` en un equipo y `ros2 multicast send` en el otro, manteniendo el receptor activo, y luego invertirá los roles. No se han repetido pruebas de mensajes ni Capabilities2 con esta red.

## Alcance y siguiente etapa

En el incremento de pruebas se añadieron al Dockerfile `libtinyxml2-dev`, `libyaml-cpp-dev`, `libsqlite3-dev`, `uuid-dev` y `ros-jazzy-bondcpp`. La imagen se reconstruyó y el contenedor se recreó correctamente conservando los volúmenes. El tamaño y digest anteriores corresponden a la preparación inicial, no a esta imagen ampliada.

La preparación original no incluyó intercambio de mensajes, Capabilities2 ni conexión física. Los resultados posteriores se registran en [[ROS 2]] y [[Capabilities2]]. La comunicación con equipos externos requiere su propia validación.
