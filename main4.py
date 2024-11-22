#!/usr/bin/env python3

import os
import subprocess
import sys
from db import GestorDB
from datetime import datetime

def buscar_appimages(db):
    try:
        # Verificar si hay datos existentes
        if db.consultar('appimage'):
            print("Se encontraron datos existentes de APPIMAGE. Actualizando...")

        print("Iniciando búsqueda de AppImages...")
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Directorios comunes donde buscar AppImages
        directorios_busqueda = [
            os.path.expanduser('~'),
            os.path.expanduser('~/Applications'),
            os.path.expanduser('~/Downloads'),
            os.path.expanduser('~/.local/bin'),
            '/opt',
            '/usr/local/bin'
        ]

        indicador = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        appimages_encontrados = 0
        directorios_totales = len(directorios_busqueda)

        for idx, directorio in enumerate(directorios_busqueda, 1):
            if os.path.exists(directorio):
                print(f"\rEscaneando directorio {idx}/{directorios_totales}: {indicador[i % len(indicador)]} {directorio}", 
                      end='', flush=True)
                i += 1
                
                for root, dirs, files in os.walk(directorio):
                    for archivo in files:
                        ruta_completa = os.path.join(root, archivo)
                        
                        if archivo.lower().endswith('.appimage') and os.access(ruta_completa, os.X_OK):
                            appimages_encontrados += 1
                            print(f"\rAppImages encontrados: {appimages_encontrados}", end='', flush=True)
                            
                            # Obtener el tamaño del archivo
                            tamaño = os.path.getsize(ruta_completa) / (1024*1024)  # Convertir a MB
                            
                            # Guardar en la base de datos
                            datos_appimage = {
                                'repositorio': os.path.dirname(ruta_completa),
                                'paquete': archivo,
                                'aplicacion': archivo.replace('.AppImage', '').replace('.appimage', ''),
                                'instalado': 1,
                                'fecha_actualizacion': fecha_actual
                            }
                            db.insertar('appimage', datos_appimage)

        print()  # Nueva línea después del progreso
        
        # Asegurar que se guarden todos los datos
        db.ejecutar_lote()
        
        if appimages_encontrados > 0:
            print(f"\n✓ Se encontraron y registraron {appimages_encontrados} AppImages.")
        else:
            print("\nNo se encontraron AppImages en el sistema.")

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Inicializar la conexión a la base de datos
        db = GestorDB()
        
        # Ejecutar la búsqueda y guardado
        buscar_appimages(db)
        
        # Cerrar la conexión correctamente
        db.cerrar()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)