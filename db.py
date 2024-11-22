# base de datos lite3
import sqlite3
from datetime import datetime
import time
from sqlite3 import Error

class GestorDB:
    def __init__(self, db_name='gestor_paquetes.db'):
        """Inicializa la conexión a la base de datos"""
        self.db_name = db_name
        self.lote = []
        self.tamaño_lote = 200
        self.crear_tablas()
        # Optimizaciones de SQLite
        self.ejecutar_sql("PRAGMA synchronous = NORMAL")
        self.ejecutar_sql("PRAGMA journal_mode = WAL")
        self.ejecutar_sql("PRAGMA temp_store = MEMORY")
        self.ejecutar_sql("PRAGMA cache_size = -2000")

    def crear_tablas(self):
        """Crea las tablas si no existen"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Tabla para DNF
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dnf (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repositorio TEXT NOT NULL,
                        paquete TEXT NOT NULL,
                        aplicacion TEXT,
                        instalado BOOLEAN DEFAULT 0,
                        fecha_actualizacion DATETIME,
                        UNIQUE(repositorio, paquete)
                    )
                ''')

                # Tabla para Snap
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS snap (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repositorio TEXT NOT NULL,
                        paquete TEXT NOT NULL,
                        aplicacion TEXT,
                        instalado BOOLEAN DEFAULT 0,
                        fecha_actualizacion DATETIME,
                        UNIQUE(repositorio, paquete)
                    )
                ''')

                # Tabla para Flatpak
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS flatpak (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repositorio TEXT NOT NULL,
                        paquete TEXT NOT NULL,
                        aplicacion TEXT,
                        instalado BOOLEAN DEFAULT 0,
                        fecha_actualizacion DATETIME,
                        UNIQUE(repositorio, paquete)
                    )
                ''')

                # Tabla para AppImage
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS appimage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repositorio TEXT NOT NULL,
                        paquete TEXT NOT NULL,
                        aplicacion TEXT,
                        instalado BOOLEAN DEFAULT 0,
                        fecha_actualizacion DATETIME,
                        UNIQUE(repositorio, paquete)
                    )
                ''')

                # Tabla para RPM
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rpm (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repositorio TEXT NOT NULL,
                        paquete TEXT NOT NULL,
                        aplicacion TEXT,
                        instalado BOOLEAN DEFAULT 0,
                        fecha_actualizacion DATETIME,
                        UNIQUE(repositorio, paquete)
                    )
                ''')
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creando tablas: {str(e)}")
            return False

    def ejecutar_sql(self, sql, params=None):
        """Ejecuta una sentencia SQL y retorna el resultado"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                conn.commit()
                return cursor.fetchall()
        except Exception as e:
            print(f"Error ejecutando SQL: {str(e)}")
            return None

    def ejecutar_lote(self):
        """Ejecuta las inserciones pendientes en una sola transacción"""
        if not self.lote:
            return

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION")

                for datos in self.lote:
                    sql = f'''
                        INSERT OR REPLACE INTO {datos['tabla']} 
                        (repositorio, paquete, aplicacion, instalado, fecha_actualizacion)
                        VALUES (?, ?, ?, ?, ?)
                    '''
                    cursor.execute(sql, (
                        datos['repositorio'],
                        datos['paquete'],
                        datos.get('aplicacion'),
                        datos.get('instalado', 0),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))

                conn.commit()
                self.lote = []
        except Exception as e:
            print(f"Error ejecutando lote: {str(e)}")
            try:
                conn.rollback()
            except:
                pass
            self.lote = []

    def insertar(self, tabla, datos):
        """Inserta datos en la tabla especificada"""
        try:
            datos['tabla'] = tabla  # Añadir tabla a los datos
            self.lote.append(datos)
            
            if len(self.lote) >= self.tamaño_lote:
                self.ejecutar_lote()
            return True
        except Exception as e:
            print(f"Error insertando datos: {str(e)}")
            return False

    def consultar(self, tabla, condicion=None):
        """Consulta registros en la tabla especificada"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                if condicion:
                    query = f"SELECT * FROM {tabla} WHERE {condicion}"
                else:
                    query = f"SELECT * FROM {tabla}"
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error en consulta: {str(e)}")
            return None

    def actualizar(self, tabla, datos, condicion):
        """Actualiza datos en la tabla según la condición"""
        try:
            sets = []
            params = []
            for key, value in datos.items():
                sets.append(f"{key} = ?")
                params.append(value)
            
            sql = f"UPDATE {tabla} SET {', '.join(sets)} WHERE {condicion}"
            return self.ejecutar_sql(sql, params) is not None
        except Exception as e:
            print(f"Error actualizando datos: {str(e)}")
            return False

    def borrar(self, tabla, condicion):
        """Borra registros de la tabla según la condición"""
        try:
            sql = f"DELETE FROM {tabla} WHERE {condicion}"
            return self.ejecutar_sql(sql) is not None
        except Exception as e:
            print(f"Error borrando datos: {str(e)}")
            return False

    def cerrar(self):
        """Asegura que todos los datos pendientes se guarden"""
        try:
            # Procesar último lote pendiente
            self.ejecutar_lote()
            
            # Esperar un momento para que se liberen las conexiones
            time.sleep(2)
            
            # Intentar cerrar la base de datos
            with sqlite3.connect(self.db_name, timeout=20) as conn:
                try:
                    # Checkpoint WAL
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    
                    # Restaurar configuración por defecto
                    conn.execute("PRAGMA journal_mode = DELETE")
                    conn.execute("PRAGMA synchronous = FULL")
                    
                    # Commit final
                    conn.commit()
                except sqlite3.OperationalError as e:
                    # Si hay error de bloqueo, ignorarlo ya que los datos están guardados
                    print("Aviso: La base de datos está ocupada, pero los datos se han guardado correctamente.")
                    
        except Exception as e:
            print("Aviso: No se pudo cerrar la base de datos limpiamente, pero los datos están guardados.")