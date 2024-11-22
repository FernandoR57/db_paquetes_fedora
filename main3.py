#!/usr/bin/env python3

import subprocess
import sys
from db import GestorDB
from datetime import datetime

def buscar_rpm(db):
    try:
        # Verificar si hay datos existentes
        if db.consultar('rpm'):
            print("Se encontraron datos existentes de RPM. Actualizando...")

        print("Iniciando búsqueda de paquetes RPM...")
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        indicador = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0

        # Obtener lista de paquetes RPM instalados con formato específico
        resultado = subprocess.run(
            ['rpm', '-qa', '--queryformat', '%{NAME}\t%{VENDOR}\t%{VERSION}\n'],
            capture_output=True,
            text=True
        )

        if resultado.returncode == 0:
            paquetes = resultado.stdout.strip().split('\n')
            total_paquetes = len(paquetes)
            
            for idx, paquete in enumerate(paquetes, 1):
                print(f"\rProcesando paquetes RPM: {indicador[i % len(indicador)]} {idx}/{total_paquetes}", 
                      end='', flush=True)
                i += 1
                
                if paquete.strip():
                    # Dividir la información del paquete
                    campos = paquete.split('\t')
                    if len(campos) >= 2:
                        nombre = campos[0]
                        vendor = campos[1] if campos[1] != '(none)' else 'desconocido'
                        
                        # Buscar ejecutables del paquete
                        files = subprocess.run(
                            ['rpm', '-ql', nombre],
                            capture_output=True,
                            text=True
                        )
                        
                        ejecutables = []
                        if files.returncode == 0:
                            for file in files.stdout.split('\n'):
                                if file.startswith('/usr/bin/') or file.startswith('/bin/'):
                                    ejecutables.append(file.split('/')[-1])

                        datos_rpm = {
                            'repositorio': vendor,
                            'paquete': nombre,
                            'aplicacion': ', '.join(ejecutables) if ejecutables else nombre,
                            'instalado': 1,  # Todos los RPM listados están instalados
                            'fecha_actualizacion': fecha_actual
                        }
                        db.insertar('rpm', datos_rpm)

            print()  # Nueva línea después del progreso
            
            # Asegurar que se guarden todos los datos
            db.ejecutar_lote()
            print("\n✓ Datos de RPM actualizados correctamente.")

    except FileNotFoundError:
        print("Error: RPM no está instalado en el sistema")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Inicializar la conexión a la base de datos
        db = GestorDB()
        
        # Ejecutar la búsqueda y guardado
        buscar_rpm(db)
        
        # Cerrar la conexión correctamente
        db.cerrar()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)