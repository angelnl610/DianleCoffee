# Instalación del repositorio de entrega

Cloná el repositorio `DianleCoffee` una vez publicado o descargá su ZIP. No hace falta seleccionar una rama específica. Los comandos de Windows y Linux se detallan en el [README](../README.md).

## Windows

1. Si `py -3.13 --version` falla, instalá Python 3.13 desde [Python para Windows](https://www.python.org/downloads/windows/). Habilitá el launcher si el instalador lo ofrece.
2. Abrí la carpeta del repo en VS Code, instalá la extensión Python y ejecutá **Python: Select Interpreter** desde Ctrl+Shift+P. Seleccioná `.venv\Scripts\python.exe` después de crear el entorno.
3. Seguí los comandos del [README](../README.md). Usá el ejecutable directo del entorno en cada comando de PowerShell.
4. Dependencias instaladas y lote/modelo listos, podés desconectar la red, abrir Streamlit y repetir la [demo](DEMO.md).

El entorno objetivo usa Python 3.13. Se reportó instalación y verificación en Linux; la ejecución independiente en Windows debe confirmarse. Una instalación repetible sin red requiere guardar los wheels para la misma versión de Python y arquitectura previamente.
