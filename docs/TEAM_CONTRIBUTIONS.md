# Distribución de tareas y contribuciones

## 1. Propósito

Este documento registra la distribución del trabajo del proyecto **Supervivencia Universitaria: La Vida Da Vueltas**.

Sus objetivos son:

* identificar las responsabilidades asignadas a cada integrante;
* distinguir entre trabajo planificado, implementado e integrado;
* facilitar la evaluación individual del proyecto;
* conservar trazabilidad mediante ramas, commits, archivos y pruebas;
* evitar atribuciones ambiguas o duplicadas;
* documentar las actividades realizadas conjuntamente.

Este documento debe actualizarse durante la integración final. Una funcionalidad no se considera integrada únicamente porque exista en una rama individual.

---

## 2. Criterios de atribución

La contribución de un integrante se sustenta mediante una o varias de las siguientes evidencias:

1. Rama de trabajo identificable.
2. Commits con mensajes descriptivos.
3. Pull Request hacia `develop`.
4. Archivos o módulos implementados.
5. Pruebas relacionadas con su funcionalidad.
6. Revisión o resolución documentada de conflictos.
7. Participación comprobable en la integración final.

No debe atribuirse una funcionalidad solo porque:

* el nombre del integrante aparezca en un comentario;
* haya creado inicialmente un archivo vacío;
* haya copiado código desarrollado por otra persona;
* el módulo se encuentre finalmente en `main` después de una integración.

La autoría se determina mediante el historial de Git y los entregables comprobables.

---

## 3. Flujo de trabajo del equipo

El proyecto emplea el siguiente flujo:

```text
rama personal
    ↓
Pull Request
    ↓
develop
    ↓
pruebas de integración
    ↓
main
```

Ramas principales:

| Rama                   | Propósito                          |
| ---------------------- | ---------------------------------- |
| `main`                 | Versión estable o entregable       |
| `develop`              | Integración del trabajo del equipo |
| `dev-alan`             | Desarrollo del Integrante 1        |
| `dev-bianca`           | Desarrollo individual de Bianca    |
| `[rama por confirmar]` | Desarrollo del integrante restante |

Cada integrante debe trabajar principalmente en su rama y evitar confirmar directamente en `main`.

---

# 4. Integrante 1

## 4.1. Identificación

| Campo          | Información                                                     |
| -------------- | --------------------------------------------------------------- |
| Nombre         | Alan Espinoza                                                   |
| Rol            | Integrante 1                                                    |
| Rama principal | `dev-alan`                                                      |
| Área principal | Jugabilidad, escenas e integración del núcleo                   |
| Estado         | Implementación terminada; pendiente de integración en `develop` |

---

## 4.2. Responsabilidades asignadas

Las responsabilidades iniciales del Integrante 1 fueron:

1. Implementar la clase `Player`.
2. Incorporar movimiento mediante flechas y WASD.
3. Utilizar movimiento independiente de FPS.
4. Limitar al jugador dentro del área jugable.
5. Implementar objetos recolectables.
6. Detectar colisiones y eliminar objetos recogidos.
7. Comunicar los efectos al sistema de estadísticas.
8. Implementar el escenario Campus.
9. Implementar el cambio de Campus a Transición y Finales.
10. Integrar el flujo principal mediante `main.py`.

No le correspondía implementar internamente:

* estadísticas definitivas;
* HUD definitivo;
* sistema completo de eventos aleatorios;
* recursos gráficos finales;
* reglas finales de victoria y derrota.

---

## 4.3. Funcionalidades implementadas

### Jugador

* Clase basada en `pygame.sprite.Sprite`.
* Movimiento con flechas.
* Movimiento opcional con WASD.
* Uso de `pygame.Vector2`.
* Movimiento mediante delta time.
* Normalización del vector diagonal.
* Conservación de precisión subpíxel.
* Restricción mediante los límites de la escena.
* Validación de velocidad y delta time.

### Recolectables

* Clase `Collectible`.
* Efectos declarativos mediante diccionarios.
* Normalización de las claves:

  * `energy`;
  * `money`;
  * `grades`.
* Separación entre efectos y progreso del objetivo.
* Colisiones mediante `pygame.sprite.spritecollide`.
* Eliminación del objeto al recogerlo.
* Tiempo de vida limitado.
* Eliminación automática de objetos caducados.
* Figuras y colores provisionales para pruebas.

### Campus

* Área jugable independiente del espacio reservado para el HUD.
* Jugador y objetos administrados por grupos de sprites.
* Aparición inicial de objetos.
* Generación periódica.
* Máximo de objetos simultáneos.
* Posiciones aleatorias con separación básica.
* Objetos académicos y distracciones.
* Distribución ponderada de apariciones.
* Objetivo de 15 materiales académicos.
* Temporizador de 120 segundos.
* Progreso separado de las estadísticas.
* Detención de la escena al completarse.
* Reinicio completo.

### Transición

* Escena independiente.
* Temporizador de tres segundos.
* Animación circular provisional.
* Cambio automático hacia Semana de Finales.
* Reinicio de la transición.

### Semana de Finales

* Escena jugable independiente.
* Temporizador de 150 segundos.
* Objetos positivos y negativos.
* Generación de objetos con mayor frecuencia que en Campus.
* Distribución ponderada aproximada:

  * 40 % positivos;
  * 60 % negativos.
* Caducidad de objetos.
* Aplicación desacoplada de efectos.
* Conteo informativo de objetos recogidos.
* Objetivo correctamente definido como supervivencia temporal.
* Detención de movimiento y generación al finalizar.
* Eliminación de los objetos restantes al agotarse el tiempo.

### Controlador y flujo general

* Enumeración `GameState`.
* Uso de un único estado global.
* `GameController` como coordinador.
* Flujo funcional:

```text
CAMPUS → TRANSITION → FINALS
```

* Delegación de eventos.
* Delegación de actualización y dibujo.
* Reinicio completo mediante `R`.
* Cierre mediante `Esc`.
* Preparación de los estados:

  * `MENU`;
  * `VICTORY`;
  * `DEFEAT`.
* Adaptador temporal para efectos.
* Título diagnóstico con:

  * progreso de Campus;
  * temporizador;
  * estado actual;
  * objetivo temporal de Finales.

---

## 4.4. Archivos principales trabajados

| Archivo                       | Contribución                                   |
| ----------------------------- | ---------------------------------------------- |
| `player.py`                   | Movimiento, posición y límites                 |
| `collectibles.py`             | Recolectables, efectos, colisiones y caducidad |
| `scenes.py`                   | Campus, Transición y Semana de Finales         |
| `game_logic.py`               | Máquina de estados y controlador               |
| `main.py`                     | Game loop e integración del núcleo             |
| `constants.py`                | Parámetros técnicos y balance provisional      |
| `requirements.txt`            | Dependencia de PyGame                          |
| `requirements-dev.txt`        | Dependencias de pruebas                        |
| `tests/conftest.py`           | Configuración de pruebas de PyGame             |
| `tests/test_player.py`        | Pruebas del jugador                            |
| `tests/test_collectibles.py`  | Pruebas de objetos y colisiones                |
| `tests/test_scenes.py`        | Pruebas de escenas                             |
| `tests/test_game_logic.py`    | Pruebas de cambios de estado                   |
| `tests/test_configuration.py` | Protección de valores definitivos              |
| `tests/test_main.py`          | Pruebas de información diagnóstica             |
| `docs/ARCHITECTURE.md`        | Documentación arquitectónica                   |
| `docs/INSTALLATION.md`        | Instalación y ejecución                        |

---

## 4.5. Validación realizada

El subsistema del Integrante 1 cuenta con pruebas de:

* movimiento mediante delta time;
* normalización diagonal;
* teclas opuestas;
* límites;
* validación de efectos;
* colisiones;
* eliminación;
* caducidad;
* progreso de Campus;
* distracciones sin progreso;
* temporizadores;
* reinicio;
* cambios de estado;
* configuración definitiva;
* presentación del objetivo de Finales.

Resultado registrado antes de la integración:

```text
30 passed
```

Comando utilizado:

```bash
python -m pytest
```

También se comprobó la sintaxis mediante:

```bash
python -m compileall \
    main.py \
    player.py \
    collectibles.py \
    scenes.py \
    game_logic.py \
    constants.py \
    tests
```

---

## 4.6. Pendientes de integración relacionados

La parte del Integrante 1 necesita consumir las interfaces finales de otros módulos:

```python
stats.apply_effect(effect)
```

También debe integrarse con:

* HUD real;
* menú;
* eventos aleatorios;
* victoria;
* derrota;
* imágenes;
* sonidos.

Estas actividades no implican que el Integrante 1 deba reemplazar el trabajo asignado a sus compañeros. Su responsabilidad durante esa etapa será adaptar y verificar la integración del núcleo.

---

# 5. Integrante 2

## 5.1. Identificación

| Campo          | Información                                             |
| -------------- | ------------------------------------------------------- |
| Nombre         | `[Completar]`                                           |
| Rol            | Integrante 2                                            |
| Rama principal | `[Completar]`                                           |
| Área principal | `[Completar según acuerdo del equipo]`                  |
| Estado         | `[Planificado / En desarrollo / Terminado / Integrado]` |

---

## 5.2. Responsabilidades asignadas

Completar únicamente con las responsabilidades realmente acordadas.

Posibles módulos del proyecto que deben distribuirse entre los integrantes restantes:

* `stats.py`;
* `events.py`;
* reglas de victoria y derrota;
* balance de estadísticas;
* Giros de la vida;
* pruebas relacionadas.

Tabla para completar:

| Responsabilidad                         | Asignada | Implementada | Integrada |
| --------------------------------------- | -------: | -----------: | --------: |
| Estadísticas de energía, dinero y notas |    `[ ]` |        `[ ]` |     `[ ]` |
| Límites entre 0 y 100                   |    `[ ]` |        `[ ]` |     `[ ]` |
| Método `apply_effect()`                 |    `[ ]` |        `[ ]` |     `[ ]` |
| Condiciones de derrota                  |    `[ ]` |        `[ ]` |     `[ ]` |
| Condición final de victoria             |    `[ ]` |        `[ ]` |     `[ ]` |
| Eventos aleatorios                      |    `[ ]` |        `[ ]` |     `[ ]` |
| Pruebas del módulo                      |    `[ ]` |        `[ ]` |     `[ ]` |

Eliminar de esta tabla las tareas que pertenezcan a otro integrante.

---

## 5.3. Archivos y evidencias

| Archivo o evidencia | Descripción                  |
| ------------------- | ---------------------------- |
| `[archivo]`         | `[contribución verificable]` |
| `[commit]`          | `[cambio realizado]`         |
| `[Pull Request]`    | `[rama de origen y destino]` |
| `[prueba]`          | `[comportamiento validado]`  |

No marcar una responsabilidad como terminada hasta que exista una implementación ejecutable.

---

# 6. Integrante 3

## 6.1. Identificación

| Campo          | Información                                             |
| -------------- | ------------------------------------------------------- |
| Nombre         | `[Completar]`                                           |
| Rol            | Integrante 3                                            |
| Rama principal | `[Completar]`                                           |
| Área principal | `[Completar según acuerdo del equipo]`                  |
| Estado         | `[Planificado / En desarrollo / Terminado / Integrado]` |

---

## 6.2. Responsabilidades asignadas

Posibles responsabilidades que deben distribuirse de acuerdo con la decisión real del equipo:

* `ui.py`;
* menú principal;
* HUD;
* mensajes;
* pantallas de victoria y derrota;
* recursos gráficos;
* sonidos;
* pruebas visuales o de interfaz.

Tabla para completar:

| Responsabilidad               | Asignada | Implementada | Integrada |
| ----------------------------- | -------: | -----------: | --------: |
| Menú principal                |    `[ ]` |        `[ ]` |     `[ ]` |
| HUD                           |    `[ ]` |        `[ ]` |     `[ ]` |
| Visualización de estadísticas |    `[ ]` |        `[ ]` |     `[ ]` |
| Mensajes de eventos           |    `[ ]` |        `[ ]` |     `[ ]` |
| Pantalla de victoria          |    `[ ]` |        `[ ]` |     `[ ]` |
| Pantalla de derrota           |    `[ ]` |        `[ ]` |     `[ ]` |
| Recursos gráficos             |    `[ ]` |        `[ ]` |     `[ ]` |
| Sonidos                       |    `[ ]` |        `[ ]` |     `[ ]` |
| Pruebas del módulo            |    `[ ]` |        `[ ]` |     `[ ]` |

Esta distribución es una plantilla y debe ajustarse a los acuerdos reales.

---

## 6.3. Archivos y evidencias

| Archivo o evidencia | Descripción                  |
| ------------------- | ---------------------------- |
| `[archivo]`         | `[contribución verificable]` |
| `[commit]`          | `[cambio realizado]`         |
| `[Pull Request]`    | `[rama de origen y destino]` |
| `[prueba]`          | `[comportamiento validado]`  |

---

# 7. Tareas compartidas

Las siguientes actividades pueden requerir participación de todo el equipo y no deben atribuirse automáticamente a una sola persona:

## 7.1. Diseño del concepto

* definición del tema universitario;
* interpretación de “La vida da vueltas”;
* elección de escenarios;
* definición de objetos positivos y negativos;
* balance inicial.

## 7.2. Integración

* revisión de contratos;
* resolución de conflictos;
* conexión entre escenas, estadísticas, eventos y UI;
* pruebas completas;
* corrección de regresiones.

## 7.3. Recursos

* selección de imágenes;
* revisión de licencias;
* edición de sprites;
* selección o creación de sonidos;
* organización de `assets/` y `sounds/`.

## 7.4. Documentación

* README final;
* arquitectura;
* instalación;
* distribución de tareas;
* instrucciones de exposición;
* capturas finales.

## 7.5. Presentación

* elaboración de diapositivas;
* preparación de demostración;
* distribución del tiempo de exposición;
* explicación técnica;
* ensayo de preguntas.

Cuando una tarea compartida tenga un responsable principal, debe registrarse en la tabla siguiente.

| Tarea compartida         | Responsable principal | Participantes  | Estado        |
| ------------------------ | --------------------- | -------------- | ------------- |
| Concepto del juego       | `[Completar]`         | `[Completar]`  | `[Completar]` |
| Integración en `develop` | `[Completar]`         | Todo el equipo | Pendiente     |
| Pruebas integrales       | `[Completar]`         | Todo el equipo | Pendiente     |
| Recursos visuales        | `[Completar]`         | `[Completar]`  | `[Completar]` |
| Sonidos                  | `[Completar]`         | `[Completar]`  | `[Completar]` |
| README final             | `[Completar]`         | Todo el equipo | Pendiente     |
| Exposición               | `[Completar]`         | Todo el equipo | Pendiente     |

---

# 8. Estado de los módulos

Esta tabla debe actualizarse después de cada integración importante.

| Módulo            | Responsable   | Rama de origen | Implementado | Integrado en `develop` | Validado |
| ----------------- | ------------- | -------------- | -----------: | ---------------------: | -------: |
| `player.py`       | Alan Espinoza | `dev-alan`     |           Sí |                     No |       Sí |
| `collectibles.py` | Alan Espinoza | `dev-alan`     |           Sí |                     No |       Sí |
| `scenes.py`       | Alan Espinoza | `dev-alan`     |           Sí |                     No |       Sí |
| `game_logic.py`   | Alan Espinoza | `dev-alan`     |     Parcial¹ |                     No |  Parcial |
| `main.py`         | Alan Espinoza | `dev-alan`     |     Parcial² |                     No |       Sí |
| `stats.py`        | `[Completar]` | `[Completar]`  |    `[Sí/No]` |                     No |       No |
| `events.py`       | `[Completar]` | `[Completar]`  |    `[Sí/No]` |                     No |       No |
| `ui.py`           | `[Completar]` | `[Completar]`  |    `[Sí/No]` |                     No |       No |
| Recursos gráficos | `[Completar]` | `[Completar]`  |    `[Sí/No]` |                     No |       No |
| Sonidos           | `[Completar]` | `[Completar]`  |    `[Sí/No]` |                     No |       No |

¹ La máquina de estados y las transiciones están implementadas, pero faltan las reglas definitivas de victoria y derrota.

² El game loop está implementado, pero todavía utiliza un adaptador temporal de efectos y un título diagnóstico hasta integrar estadísticas y HUD.

---

# 9. Matriz de integración

| Componente productor   | Contrato                  | Componente consumidor  | Estado                |
| ---------------------- | ------------------------- | ---------------------- | --------------------- |
| `Collectible`          | `effects: dict[str, int]` | Escena                 | Implementado          |
| Escenas                | `effect_handler(effects)` | `stats.apply_effect()` | Pendiente de conexión |
| Campus                 | `objective_reached`       | `GameController`       | Implementado          |
| Transición             | `is_complete()`           | `GameController`       | Implementado          |
| Finales                | `time_expired`            | `GameController`       | Implementado          |
| Estadísticas           | valores actuales          | HUD                    | Pendiente             |
| Estadísticas           | condición de derrota      | `GameController`       | Pendiente             |
| Finales + estadísticas | resultado                 | Victoria/derrota       | Pendiente             |
| Eventos                | mensaje y efectos         | Estadísticas/UI        | Pendiente             |

---

# 10. Registro de Pull Requests

| PR         | Rama origen | Rama destino | Responsable    | Contenido             | Estado     |
| ---------- | ----------- | ------------ | -------------- | --------------------- | ---------- |
| `[número]` | `dev-alan`  | `develop`    | Alan Espinoza  | Núcleo de jugabilidad | Pendiente  |
| `[número]` | `[rama]`    | `develop`    | `[integrante]` | `[contenido]`         | `[estado]` |
| `[número]` | `[rama]`    | `develop`    | `[integrante]` | `[contenido]`         | `[estado]` |

Esta tabla debe usar los números y estados reales de GitHub.

---

# 11. Validación final por integrante

Antes de marcar una contribución como terminada, cada integrante debe comprobar:

```bash
git status
git diff --check
python -m pytest
python main.py
```

Lista de verificación:

* [ ] El código se encuentra en la rama correcta.
* [ ] Los commits tienen mensajes descriptivos.
* [ ] No se confirmaron archivos temporales.
* [ ] No se confirmó `.venv`.
* [ ] No se confirmaron cachés de Python.
* [ ] Las pruebas pasan.
* [ ] La funcionalidad fue validada manualmente.
* [ ] Existe Pull Request hacia `develop`.
* [ ] Otro integrante revisó el cambio.
* [ ] La documentación fue actualizada.

---

# 12. Integración final

La integración final debe seguir este orden recomendado:

```text
1. Núcleo de jugabilidad
2. Estadísticas
3. HUD e interfaz
4. Eventos aleatorios
5. Victoria y derrota
6. Recursos gráficos
7. Sonidos
8. Balance
9. Pruebas integrales
10. Documentación final
```

Después de cada integración:

```bash
git switch develop
git pull origin develop
python -m pytest
python main.py
```

`main` debe actualizarse únicamente cuando `develop` sea estable.

---

# 13. Nota para la evaluación

Este documento diferencia tres conceptos:

### Asignado

La tarea fue acordada como responsabilidad del integrante.

### Implementado

Existe código funcional en la rama del integrante.

### Integrado

El código fue revisado y fusionado en `develop` o `main`.

Por tanto, una tarea puede estar implementada pero todavía no integrada.

La evaluación individual debe considerar:

* responsabilidad asumida;
* calidad del código;
* cumplimiento de contratos;
* pruebas;
* historial de commits;
* revisión;
* participación en la integración;
* capacidad de explicar técnicamente la solución.
