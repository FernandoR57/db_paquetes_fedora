#!/usr/bin/env python3

import subprocess
import sys
from db import GestorDB
from datetime import datetime

def buscar_snap(db):
    try:
        # Verificar si hay datos existentes
        if db.consultar('snap'):
            print("Se encontraron datos existentes de SNAP. Actualizando...")
            # En lugar de borrar, actualizaremos los registros

        print("Iniciando búsqueda de snaps...")

        # Obtener lista de snaps instalados
        resultado_installed = subprocess.run(['snap', 'list'], 
                                          capture_output=True, 
                                          text=True)

        # Obtener lista de snaps disponibles
        resultado_available = subprocess.run(['snap', 'find'], 
                                          capture_output=True, 
                                          text=True)

        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        indicador = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0

        # Procesar snaps instalados
        if resultado_installed.returncode == 0:
            installed_lines = resultado_installed.stdout.strip().split('\n')[1:]
            total_lines = len(installed_lines)
            for idx, line in enumerate(installed_lines, 1):
                print(f"\rProcesando snaps instalados: {indicador[i % len(indicador)]} {idx}/{total_lines}", end='', flush=True)
                i += 1
                if line.strip():
                    campos = line.split()
                    datos_snap = {
                        'repositorio': 'snapcraft',
                        'paquete': campos[0],
                        'aplicacion': campos[0],  # En snap, el paquete suele ser la aplicación
                        'instalado': 1
                    }
                    db.insertar('snap', datos_snap)

        # Procesar snaps disponibles
        if resultado_available.returncode == 0:
            available_lines = resultado_available.stdout.strip().split('\n')[1:]  # Ignorar encabezado
            for line in available_lines:
                print(f"\r{indicador[i % len(indicador)]}", end='', flush=True)
                i += 1
                if line.strip():
                    campos = line.split()
                    if len(campos) >= 1:
                        # Verificar si ya existe como instalado
                        if not db.consultar('snap', f"paquete = '{campos[0]}' AND instalado = 1"):
                            datos_snap = {
                                'repositorio': 'snapcraft',
                                'paquete': campos[0],
                                'aplicacion': campos[0],
                                'instalado': 0
                            }
                            db.insertar('snap', datos_snap)

        print("\nDatos guardados en la base de datos correctamente.")
        
    except FileNotFoundError:
        print("Error: Snap no está instalado en el sistema")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    try:
        # Inicializar la conexión a la base de datos
        db = GestorDB()
        
        # Ejecutar la búsqueda y guardado
        buscar_snap(db)
        
    except Exception as e:
        print(f"Error: {str(e)}")
