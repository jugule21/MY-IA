import subprocess
import openai
import os
from diff_match_patch import diff_match_patch
import shutil
from datetime import datetime
import logging

# Configurar el registro de logs
logging.basicConfig(filename='mejora_codigo.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configurar la API Key de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


def ejecutar_comando(comando):
    """
    Ejecuta un comando en la terminal y captura la salida.

    Args:
        comando (list): Lista de argumentos del comando.

    Returns:
        subprocess.CompletedProcess: El resultado del comando ejecutado.
    """
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True)
        logging.info(resultado.stdout)
        return resultado
    except Exception as e:
        logging.error(f"Error al ejecutar el comando {comando}: {e}")
        return None


def ejecutar_pruebas():
    """
    Ejecuta las pruebas unitarias usando pytest y captura la salida.

    Returns:
        bool: True si todas las pruebas pasan, False en caso contrario.
    """
    resultado = ejecutar_comando(['pytest', 'tests.py'])
    if resultado and resultado.returncode == 0:
        return True
    return False


def mejorar_codigo(codigo, iteraciones=1):
    """
    Mejora el código proporcionado utilizando la API de OpenAI, iterando varias veces para aumentar su complejidad.

    Args:
        codigo (str): El código original a mejorar.
        iteraciones (int): Número de iteraciones para mejorar el código.

    Returns:
        str: El código mejorado.
    """
    for i in range(iteraciones):
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Mejora el siguiente código:\n\n{codigo}\n\n",
                max_tokens=300,
                n=1,
                stop=None,
                temperature=0.5,
            )
            sugerencia = response.choices[0].text.strip()
            logging.info(f"Iteración {i + 1} - Código mejorado:\n{sugerencia}")
            codigo = sugerencia
        except Exception as e:
            logging.error(f"Error al generar mejoras en el código: {e}")
            return None
    return codigo


def calcular_diferencia(original, mejorado):
    """
    Calcula la diferencia entre el código original y el mejorado.

    Args:
        original (str): El código original.
        mejorado (str): El código mejorado.

    Returns:
        list: Lista de diferencias entre el código original y el mejorado.
    """
    dmp = diff_match_patch()
    diffs = dmp.diff_main(original, mejorado)
    dmp.diff_cleanupSemantic(diffs)
    return diffs


def crear_archivo(ruta, contenido):
    """
    Crea un archivo con el contenido especificado.

    Args:
        ruta (str): La ruta del archivo a crear.
        contenido (str): El contenido del archivo.
    """
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'w') as file:
            file.write(contenido)
        logging.info(f"Archivo creado: {ruta}")
    except Exception as e:
        logging.error(f"Error al crear el archivo {ruta}: {e}")


def listar_archivos(directorio):
    """
    Lista todos los archivos en el directorio especificado.

    Args:
        directorio (str): El directorio a listar.
    """
    try:
        for root, dirs, files in os.walk(directorio):
            for name in files:
                logging.info(os.path.join(root, name))
            for name in dirs:
                logging.info(os.path.join(root, name))
    except Exception as e:
        logging.error(f"Error al listar archivos en el directorio {directorio}: {e}")


def cargar_codigo(ruta):
    """
    Carga el código desde un archivo.

    Args:
        ruta (str): La ruta del archivo a cargar.

    Returns:
        str: El contenido del archivo.
    """
    try:
        with open(ruta, 'r') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error al leer el archivo {ruta}: {e}")
        exit(1)


def guardar_codigo(ruta, codigo):
    """
    Guarda el código en un archivo.

    Args:
        ruta (str): La ruta del archivo.
        codigo (str): El contenido del archivo.
    """
    crear_archivo(ruta, codigo)


def analizar_codigo(ruta):
    """
    Analiza el código utilizando pylint y captura la salida.

    Args:
        ruta (str): La ruta del archivo a analizar.
    """
    resultado = ejecutar_comando(['pylint', ruta])
    if resultado and resultado.returncode != 0:
        logging.warning(f"Issues found by pylint:\n{resultado.stdout}")


def verificar_estilo_codigo(ruta):
    """
    Verifica el estilo del código utilizando flake8 y captura la salida.

    Args:
        ruta (str): La ruta del archivo a verificar.
    """
    resultado = ejecutar_comando(['flake8', ruta])
    if resultado and resultado.returncode != 0:
        logging.warning(f"Issues found by flake8:\n{resultado.stdout}")


def main():
    # Cargar el código original desde un archivo
    codigo_original = cargar_codigo('codigo.py')

    # Ejecutar pruebas en el código original
    if ejecutar_pruebas():
        logging.info("El código original pasa todas las pruebas.")
    else:
        logging.info("El código original no pasa todas las pruebas.")
        exit(1)

    # Generar mejoras iterativas
    iteraciones = 3
    codigo_mejorado = mejorar_codigo(codigo_original, iteraciones)
    if not codigo_mejorado:
        logging.info("No se pudo generar mejoras en el código.")
        exit(1)

    # Guardar el código mejorado en un archivo temporal
    guardar_codigo('temp/codigo_mejorado.py', codigo_mejorado)

    # Calcular la diferencia entre el código original y el mejorado
    diferencia = calcular_diferencia(codigo_original, codigo_mejorado)
    logging.info("Diferencias entre el código original y el mejorado:")
    for diff in diferencia:
        logging.info(diff)

    # Analizar y verificar el estilo del código mejorado
    analizar_codigo('temp/codigo_mejorado.py')
    verificar_estilo_codigo('temp/codigo_mejorado.py')

    # Renombrar el archivo temporal a codigo.py para las pruebas
    try:
        shutil.move('temp/codigo_mejorado.py', 'codigo.py')
    except Exception as e:
        logging.error(f"Error al renombrar el archivo temporal: {e}")
        exit(1)

    # Ejecutar pruebas en el código mejorado
    if ejecutar_pruebas():
        logging.info("El código mejorado pasa todas las pruebas y ha sido aplicado.")
    else:
        logging.info("El código mejorado no pasa todas las pruebas, se mantiene el código original.")
        # Restaurar el código original si las pruebas fallan
        guardar_codigo('codigo.py', codigo_original)

    # Crear un nuevo archivo de ejemplo
    nuevo_codigo = """
def resta(a, b):
    return a - b
"""
    guardar_codigo('nuevas_funciones/resta.py', nuevo_codigo)

    # Listar todos los archivos en el directorio del proyecto
    logging.info("Archivos en el proyecto:")
    listar_archivos('.')


if __name__ == "__main__":
    main()
