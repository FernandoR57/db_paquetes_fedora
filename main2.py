#!/usr/bin/env python3

import subprocess
import sys
from db import GestorDB
from datetime import datetime

def buscar_flatpak(db):
    try:
        # Verificar si hay datos existentes
        if db.consultar('flatpak'):
            print("Se encontraron datos existentes de FLATPAK. Actualizando...")

        print("Iniciando búsqueda de flatpaks...")
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        indicador = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0

        # Obtener lista de flatpaks instalados
        installed = subprocess.run(['flatpak', 'list', '--app', '--columns=application,name,version'], 
                                 capture_output=True, 
                                 text=True)

        # Procesar flatpaks instalados
        if installed.returncode == 0:
            installed_lines = installed.stdout.strip().split('\n')
            total_installed = len(installed_lines)
            
            for idx, line in enumerate(installed_lines, 1):
                print(f"\rProcesando flatpaks instalados: {indicador[i % len(indicador)]} {idx}/{total_installed}", 
                      end='', flush=True)
                i += 1
                if line.strip():
                    campos = line.split()
                    if len(campos) >= 2:
                        datos_flatpak = {
                            'repositorio': 'flathub',
                            'paquete': campos[0],
                            'aplicacion': campos[1],
                            'instalado': 1,
                            'fecha_actualizacion': fecha_actual
                        }
                        db.insertar('flatpak', datos_flatpak)
            print()  # Nueva línea después del progreso

        # Obtener lista de flatpaks disponibles
        available = subprocess.run(['flatpak', 'remote-ls', '--app', '--columns=application'], 
                                 capture_output=True, 
                                 text=True)

        # Procesar flatpaks disponibles
        if available.returncode == 0:
            available_lines = available.stdout.strip().split('\n')
            total_available = len(available_lines)
            
            for idx, line in enumerate(available_lines, 1):
                print(f"\rProcesando flatpaks disponibles: {indicador[i % len(indicador)]} {idx}/{total_available}", 
                      end='', flush=True)
                i += 1
                if line.strip():
                    app_id = line.strip()
                    # Verificar si ya existe como instalado
                    if not db.consultar('flatpak', f"paquete = '{app_id}' AND instalado = 1"):
                        datos_flatpak = {
                            'repositorio': 'flathub',
                            'paquete': app_id,
                            'aplicacion': app_id,
                            'instalado': 0,
                            'fecha_actualizacion': fecha_actual
                        }
                        db.insertar('flatpak', datos_flatpak)
            print()  # Nueva línea después del progreso

        # Asegurar que se guarden todos los datos
        db.ejecutar_lote()
        print("\n✓ Datos de flatpak actualizados correctamente.")

    except FileNotFoundError:
        print("Error: Flatpak no está instalado en el sistema")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Inicializar la conexión a la base de datos
        db = GestorDB()
        
        # Ejecutar la búsqueda y guardado
        buscar_flatpak(db)
        
        # Cerrar la conexión correctamente
        db.cerrar()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
