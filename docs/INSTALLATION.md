# Instalación y ejecución

## 1. Propósito

Este documento explica cómo preparar, ejecutar y validar **Supervivencia Universitaria: La Vida Da Vueltas** en:

* Ubuntu Linux;
* Windows 11.

El proyecto está desarrollado con Python y PyGame. No requiere una base de datos, servidor web ni servicios externos para ejecutar el prototipo actual.

---

## 2. Requisitos

### Software requerido

* Git.
* Python 3.11 o Python 3.12.
* `pip`.
* Soporte para entornos virtuales de Python.

### Dependencias del juego

Las dependencias de ejecución se encuentran en:

```text
requirements.txt
```

Actualmente incluyen:

```text
pygame>=2.5,<3
```

Las herramientas utilizadas para desarrollo y pruebas se encuentran en:

```text
requirements-dev.txt
```

Este archivo instala también:

```text
pytest>=8,<9
```

### Recomendación

Debe utilizarse un entorno virtual. No se recomienda instalar las dependencias directamente en el Python global del sistema.

---

## 3. Obtener el proyecto

Clonar el repositorio:

```bash
git clone https://github.com/BiancaMT957/supervivencia-universitaria.git
cd supervivencia-universitaria
```

### Seleccionar una rama

Para trabajar con la rama de integración:

```bash
git switch develop
git pull origin develop
```

Para revisar el aporte del Integrante 1 antes de su integración:

```bash
git switch dev-alan
git pull origin dev-alan
```

Para una entrega final publicada, debe utilizarse la rama:

```bash
git switch main
git pull origin main
```

No deben copiarse manualmente archivos entre ramas. La integración debe realizarse mediante Pull Requests.

---

# 4. Instalación en Ubuntu

## 4.1. Instalar herramientas del sistema

En Ubuntu 22.04, Ubuntu 24.04 o una versión compatible:

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv
```

Comprobar las versiones:

```bash
git --version
python3 --version
python3 -m pip --version
```

Se recomienda utilizar Python 3.11 o Python 3.12.

---

## 4.2. Crear el entorno virtual

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
```

Activarlo:

```bash
source .venv/bin/activate
```

Cuando el entorno está activo, la terminal normalmente muestra:

```text
(.venv)
```

al inicio de la línea.

---

## 4.3. Actualizar pip

```bash
python -m pip install --upgrade pip
```

Debe utilizarse:

```bash
python -m pip
```

en lugar de ejecutar `pip` directamente, porque así se garantiza que las dependencias se instalen en el Python del entorno virtual activo.

---

## 4.4. Instalar las dependencias del juego

```bash
python -m pip install -r requirements.txt
```

Comprobar la instalación de PyGame:

```bash
python -c "import pygame; print(pygame.version.ver)"
```

---

## 4.5. Ejecutar el juego

```bash
python main.py
```

Debe abrirse una ventana de PyGame con el escenario activo.

### Controles actuales

| Acción                   | Teclas                                |
| ------------------------ | ------------------------------------- |
| Mover hacia arriba       | Flecha arriba o `W`                   |
| Mover hacia abajo        | Flecha abajo o `S`                    |
| Mover hacia la izquierda | Flecha izquierda o `A`                |
| Mover hacia la derecha   | Flecha derecha o `D`                  |
| Reiniciar la sesión      | `R`                                   |
| Cerrar el juego          | `Esc` o botón de cierre de la ventana |

---

## 4.6. Desactivar el entorno virtual

Al terminar:

```bash
deactivate
```

---

# 5. Instalación en Windows 11

## 5.1. Instalar Python

Se recomienda instalar Python desde su instalador oficial.

Durante la instalación debe activarse la opción:

```text
Add python.exe to PATH
```

Después, abrir PowerShell y comprobar:

```powershell
py --version
```

También puede comprobarse:

```powershell
python --version
```

Se recomienda utilizar Python 3.11 o Python 3.12.

---

## 5.2. Instalar Git

Instalar Git para Windows y comprobar desde PowerShell:

```powershell
git --version
```

Cerrar y volver a abrir PowerShell si el comando no es reconocido inmediatamente después de instalar Git.

---

## 5.3. Clonar el repositorio

En PowerShell:

```powershell
git clone https://github.com/BiancaMT957/supervivencia-universitaria.git
cd supervivencia-universitaria
```

Seleccionar la rama correspondiente:

```powershell
git switch develop
git pull origin develop
```

Para revisar específicamente la rama del Integrante 1:

```powershell
git switch dev-alan
git pull origin dev-alan
```

---

## 5.4. Crear el entorno virtual

```powershell
py -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Cuando el entorno se active correctamente, PowerShell mostrará:

```text
(.venv)
```

al inicio de la línea.

---

## 5.5. Error de ejecución de scripts en PowerShell

Si PowerShell muestra un mensaje indicando que la ejecución de scripts está deshabilitada, puede habilitarse solo para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después:

```powershell
.\.venv\Scripts\Activate.ps1
```

La opción `-Scope Process` no modifica permanentemente la política del sistema.

### Alternativa con Símbolo del sistema

Desde `cmd.exe` puede activarse el entorno mediante:

```bat
.venv\Scripts\activate.bat
```

---

## 5.6. Actualizar pip

Con el entorno virtual activo:

```powershell
python -m pip install --upgrade pip
```

---

## 5.7. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

Comprobar PyGame:

```powershell
python -c "import pygame; print(pygame.version.ver)"
```

---

## 5.8. Ejecutar el juego

```powershell
python main.py
```

También puede ejecutarse mediante:

```powershell
py main.py
```

Sin embargo, cuando el entorno virtual está activo, se recomienda usar:

```powershell
python main.py
```

para asegurarse de emplear el intérprete correcto.

---

## 5.9. Desactivar el entorno virtual

```powershell
deactivate
```

---

# 6. Instalación para desarrollo

Los colaboradores que ejecutarán pruebas automatizadas deben instalar:

```bash
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` incluye tanto las dependencias del juego como las herramientas de prueba.

No es necesario ejecutar primero:

```bash
python -m pip install -r requirements.txt
```

si se instalará directamente `requirements-dev.txt`.

---

## 6.1. Ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python -m pytest
```

El resultado correcto debe terminar sin errores ni pruebas fallidas.

El número total de pruebas puede aumentar durante el desarrollo, por lo que no debe utilizarse una cantidad fija como único criterio de éxito.

Ejemplo de resultado válido:

```text
============================== tests passed ==============================
```

Las pruebas configuran controladores SDL sin interfaz gráfica, por lo que pueden ejecutarse sin abrir la ventana del juego.

---

## 6.2. Comprobar la sintaxis

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

En PowerShell puede escribirse en una sola línea:

```powershell
python -m compileall main.py player.py collectibles.py scenes.py game_logic.py constants.py tests
```

La ausencia de mensajes de error indica que Python pudo compilar los archivos.

---

## 6.3. Validación recomendada antes de un commit

```bash
git status
git diff --check
python -m pytest
```

Después deben añadirse solo los archivos correspondientes al cambio:

```bash
git add archivo1.py archivo2.py
git commit -m "tipo: descripcion breve"
```

No se recomienda usar automáticamente:

```bash
git add .
```

porque podría incluir entornos virtuales, archivos temporales, capturas o recursos no relacionados.

---

# 7. Actualizar una instalación existente

Ingresar al repositorio:

```bash
cd supervivencia-universitaria
```

Activar el entorno virtual.

Ubuntu:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Actualizar la rama:

```bash
git pull
```

Actualizar las dependencias:

```bash
python -m pip install -r requirements.txt
```

Para desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

Ejecutar nuevamente:

```bash
python main.py
```

---

# 8. Recrear el entorno virtual

Si el entorno virtual está dañado o las dependencias presentan conflictos, puede eliminarse y recrearse.

## Ubuntu

Desactivar el entorno si está activo:

```bash
deactivate
```

Eliminarlo:

```bash
rm -rf .venv
```

Recrearlo:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Windows PowerShell

Desactivar:

```powershell
deactivate
```

Eliminar:

```powershell
Remove-Item -Recurse -Force .venv
```

Recrear:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

# 9. Solución de problemas

## 9.1. `python: command not found` en Ubuntu

Utilizar:

```bash
python3 --version
python3 -m venv .venv
```

Después de activar el entorno, el comando `python` debería estar disponible.

---

## 9.2. No se puede crear el entorno virtual en Ubuntu

Si aparece un error relacionado con `ensurepip` o `venv`:

```bash
sudo apt update
sudo apt install python3-venv
```

Después:

```bash
python3 -m venv .venv
```

---

## 9.3. `No module named pygame`

Esto suele indicar que:

* el entorno virtual no está activo;
* las dependencias no fueron instaladas;
* se está usando otro intérprete de Python.

Comprobar el intérprete.

Ubuntu:

```bash
which python
```

Debe apuntar a una ruta semejante a:

```text
.../supervivencia-universitaria/.venv/bin/python
```

Windows PowerShell:

```powershell
Get-Command python
```

Después reinstalar:

```bash
python -m pip install -r requirements.txt
```

---

## 9.4. `No module named pytest`

Instalar las dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

Ejecutar:

```bash
python -m pytest
```

---

## 9.5. `main.py` no existe

Verificar la carpeta actual:

Ubuntu:

```bash
pwd
ls
```

Windows:

```powershell
Get-Location
Get-ChildItem
```

Debe ejecutarse el comando desde la raíz del repositorio, donde se encuentra:

```text
main.py
```

---

## 9.6. La ventana se abre y se cierra inmediatamente

Ejecutar el juego desde una terminal:

```bash
python main.py
```

No abrir `main.py` mediante doble clic. La terminal permitirá observar el mensaje de error.

---

## 9.7. PowerShell no activa el entorno

Aplicar temporalmente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 9.8. Git no reconoce una rama

Actualizar la información remota:

```bash
git fetch origin
git branch -a
```

Después:

```bash
git switch nombre-de-la-rama
```

---

## 9.9. La ventana no aparece en una sesión remota

PyGame necesita una sesión gráfica para mostrar el juego.

En servidores, SSH o entornos sin pantalla, deben ejecutarse únicamente las pruebas:

```bash
python -m pytest
```

La validación visual debe realizarse en Ubuntu de escritorio o Windows 11 con una sesión gráfica activa.

---

# 10. Verificación final de la instalación

Con el entorno activo, ejecutar:

```bash
python -c "import pygame; print('PyGame:', pygame.version.ver)"
python -m pytest
python main.py
```

La instalación se considera correcta cuando:

1. PyGame se importa sin errores.
2. Las pruebas terminan sin fallos.
3. La ventana del juego se abre.
4. El jugador responde a flechas o WASD.
5. `R` reinicia la sesión.
6. `Esc` cierra correctamente la aplicación.

---

# 11. Archivos que no deben confirmarse

No deben subirse al repositorio:

```text
.venv/
__pycache__/
*.pyc
.pytest_cache/
```

Antes de confirmar cambios:

```bash
git status
```

Debe verificarse que el entorno virtual, cachés y archivos generados no estén incluidos.

---

# 12. Documentación relacionada

* [`ARCHITECTURE.md`](ARCHITECTURE.md): arquitectura, responsabilidades y contratos entre módulos.
* `TEAM_CONTRIBUTIONS.md`: distribución del trabajo del equipo, pendiente de elaboración.
* `README.md`: presentación general del proyecto, pendiente de consolidación final.
