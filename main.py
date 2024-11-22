#!/usr/bin/env python3
import subprocess
import sys
from db import GestorDB
from datetime import datetime

def main():
    try:
        db = GestorDB()
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print("Verificando actualizaciones disponibles...")
        check_update = subprocess.Popen(
            ['pkexec', 'dnf', 'check-update'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        while True:
            output = check_update.stdout.readline()
            if output == '' and check_update.poll() is not None:
                break
            if output:
                print(output.strip())
                sys.stdout.flush()

        print("\nIniciando actualización del sistema...")
        update_process = subprocess.Popen(
            ['pkexec', 'dnf', 'upgrade', '-y'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        while True:
            output = update_process.stdout.readline()
            if output == '' and update_process.poll() is not None:
                break
            if output:
                print(output.strip())
                sys.stdout.flush()

        if update_process.returncode == 0:
            print("\nActualización de DNF completada exitosamente")
            
            datos_dnf = {
                'repositorio': 'fedora',
                'paquete': 'system-update',
                'aplicacion': 'dnf',
                'instalado': 1,
                'fecha_actualizacion': fecha_actual
            }
            
            db.insertar('dnf', datos_dnf)
            db.ejecutar_lote()
            db.cerrar()
            return 0
        else:
            print("\nError durante la actualización")
            return 1

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
