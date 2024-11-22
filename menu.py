#!/usr/bin/env python3
#!/usr/bin/env python3

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTabWidget, 
                            QMessageBox, QGroupBox, QButtonGroup, QRadioButton, 
                            QTableWidget, QTableWidgetItem, QLineEdit, QMenu,
                            QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QClipboard
from db import GestorDB
import sys
import subprocess
import unicodedata

class ActualizacionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Controles de zoom
        zoom_layout = QHBoxLayout()
        
        self.zoom_out_button = QPushButton("A-")
        self.zoom_out_button.setFixedSize(50, 30)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        
        self.zoom_in_button = QPushButton("A+")
        self.zoom_in_button.setFixedSize(50, 30)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addStretch()
        layout.addLayout(zoom_layout)

        # Botones de actualización
        botones = [
            ('Actualizar DNF', 'main.py'),
            ('Actualizar Snap', 'main1.py'),
            ('Actualizar Flatpak', 'main2.py'),
            ('Actualizar RPM', 'main3.py'),
            ('Actualizar AppImage', 'main4.py')
        ]

        for texto, script in botones:
            button = QPushButton(texto)
            button.clicked.connect(lambda checked, s=script: self.ejecutar_script(s))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 15px;
                    font-size: 14pt;
                    border-radius: 5px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            layout.addWidget(button)

        # Área de texto para la salida
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                padding: 10px;
                font-size: 12pt;
            }
        """)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def zoom_in(self):
        current_size = self.output_text.font().pointSize()
        new_size = current_size + 2
        if new_size <= 24:
            self.aplicar_zoom(new_size)

    def zoom_out(self):
        current_size = self.output_text.font().pointSize()
        new_size = current_size - 2
        if new_size >= 8:
            self.aplicar_zoom(new_size)

    def aplicar_zoom(self, new_size):
        font = QFont()
        font.setPointSize(new_size)
        self.output_text.setFont(font)

    def ejecutar_script(self, script):
        try:
            self.output_text.append(f"\nEjecutando {script}...")
            proceso = subprocess.Popen(['python3', script], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
            
            while True:
                output = proceso.stdout.readline()
                if output == '' and proceso.poll() is not None:
                    break
                if output:
                    self.output_text.append(output.strip())
                    QApplication.processEvents()
            
            returncode = proceso.poll()
            if returncode == 0:
                self.output_text.append(f"\n✓ {script} completado exitosamente\n")
                QMessageBox.information(self, "Completado", 
                                      f"El script {script} se ha completado exitosamente",
                                      QMessageBox.Ok)
            else:
                self.output_text.append(f"\n❌ Error al ejecutar {script}\n")
                QMessageBox.critical(self, "Error", 
                                   f"Error al ejecutar {script}",
                                   QMessageBox.Ok)
                
        except Exception as e:
            self.output_text.append(f"\n❌ Error: {str(e)}\n")
            QMessageBox.critical(self, "Error", 
                               f"Error: {str(e)}",
                               QMessageBox.Ok)

class ConsultasTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = GestorDB()
        self.initUI()

    def normalizar_texto(self, texto):
        return ''.join(c for c in unicodedata.normalize('NFD', texto.lower())
                      if unicodedata.category(c) != 'Mn')

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Controles de zoom
        zoom_layout = QHBoxLayout()
        
        self.zoom_out_button = QPushButton("A-")
        self.zoom_out_button.setFixedSize(50, 30)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        
        self.zoom_in_button = QPushButton("A+")
        self.zoom_in_button.setFixedSize(50, 30)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        
        zoom_layout.addWidget(self.zoom_out_button)
        zoom_layout.addWidget(self.zoom_in_button)
        zoom_layout.addStretch()
        layout.addLayout(zoom_layout)

        # Grupos de radio buttons
        self.tablas_group = self.crear_grupo_tablas()
        layout.addWidget(self.tablas_group)
        
        self.campos_group = self.crear_grupo_campos()
        layout.addWidget(self.campos_group)
        
        # Caja de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("Texto a buscar:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Introduce el término de búsqueda y pulsa Enter... (* para comodines)")
        self.search_input.returnPressed.connect(self.realizar_busqueda)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Botón de fijar registro
        self.fix_button = QPushButton("Fijar registro seleccionado")
        self.fix_button.clicked.connect(self.filtrar_por_seleccion)
        self.fix_button.setEnabled(False)
        layout.addWidget(self.fix_button)
        
        # Tabla de resultados
        self.tabla_resultados = QTableWidget()
        self.tabla_resultados.setColumnCount(6)
        self.tabla_resultados.setHorizontalHeaderLabels(
            ["ID", "Repositorio", "Paquete", "Aplicación", "Instalado", "Fecha"])
        self.tabla_resultados.horizontalHeader().setStretchLastSection(True)
        self.tabla_resultados.setAlternatingRowColors(True)
        self.tabla_resultados.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_resultados.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        self.tabla_resultados.itemSelectionChanged.connect(self.seleccion_cambiada)
        layout.addWidget(self.tabla_resultados)
        
        # Etiqueta de estado
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

    def zoom_in(self):
        current_size = self.tabla_resultados.font().pointSize()
        new_size = current_size + 2
        if new_size <= 24:
            self.aplicar_zoom(new_size)

    def zoom_out(self):
        current_size = self.tabla_resultados.font().pointSize()
        new_size = current_size - 2
        if new_size >= 8:
            self.aplicar_zoom(new_size)

    def aplicar_zoom(self, new_size):
        font = QFont()
        font.setPointSize(new_size)
        self.tabla_resultados.setFont(font)
        row_height = max(30, new_size * 2.5)
        self.tabla_resultados.verticalHeader().setDefaultSectionSize(int(row_height))
        header_font = QFont()
        header_font.setPointSize(new_size)
        header_font.setBold(True)
        self.tabla_resultados.horizontalHeader().setFont(header_font)

    def crear_grupo_tablas(self):
        grupo_box = QGroupBox("Tipo de paquete")
        layout = QHBoxLayout()
        
        # Crear el grupo de botones
        self.tablas_button_group = QButtonGroup(self)
        
        tablas = ['DNF', 'Snap', 'Flatpak', 'RPM', 'AppImage']
        
        for i, tabla in enumerate(tablas):
            radio = QRadioButton(tabla)
            if i == 0:
                radio.setChecked(True)
            self.tablas_button_group.addButton(radio)
            layout.addWidget(radio)
        
        grupo_box.setLayout(layout)
        return grupo_box

    def crear_grupo_campos(self):
        grupo_box = QGroupBox("Campo de búsqueda")
        layout = QHBoxLayout()
        
        # Crear el grupo de botones
        self.campos_button_group = QButtonGroup(self)
        
        campos = {
            'Repositorio': 'repositorio',
            'Paquete': 'paquete',
            'Aplicación': 'aplicacion',
            'Instalado': 'instalado'
        }
        
        for i, (mostrar, interno) in enumerate(campos.items()):
            radio = QRadioButton(mostrar)
            radio.setProperty('campo_interno', interno)
            if i == 0:
                radio.setChecked(True)
            self.campos_button_group.addButton(radio)
            layout.addWidget(radio)
        
        grupo_box.setLayout(layout)
        return grupo_box

    def realizar_busqueda(self):
        self.tabla_resultados.setRowCount(0)
        
        # Usar los nuevos nombres de los grupos de botones
        campo_busqueda = self.campos_button_group.checkedButton().property('campo_interno')
        tabla_seleccionada = self.normalizar_texto(self.tablas_button_group.checkedButton().text())
        texto_busqueda = self.search_input.text().strip()
        
        try:
            if texto_busqueda == '*':
                condicion = None
            else:
                if texto_busqueda.startswith('*') and texto_busqueda.endswith('*'):
                    patron = f"%{texto_busqueda.strip('*')}%"
                elif texto_busqueda.startswith('*'):
                    patron = f"%{texto_busqueda.strip('*')}"
                elif texto_busqueda.endswith('*'):
                    patron = f"{texto_busqueda.strip('*')}%"
                else:
                    patron = texto_busqueda

                condicion = f"{campo_busqueda} LIKE '{patron}'"

            resultados = self.db.consultar(tabla_seleccionada, condicion)
            
            if resultados:
                self.mostrar_resultados(resultados)
                self.status_label.setText(f"Se encontraron {len(resultados)} resultados")
            else:
                QMessageBox.information(self, "Búsqueda", "No se encontraron resultados")
                self.status_label.setText("No se encontraron resultados")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la búsqueda: {str(e)}")

    def mostrar_resultados(self, resultados):
        self.tabla_resultados.setRowCount(len(resultados))
        for i, resultado in enumerate(resultados):
            for j, valor in enumerate(resultado):
                if j == 4:  # Columna "Instalado"
                    valor = "Sí" if valor == 1 else "No"
                item = QTableWidgetItem(str(valor))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.tabla_resultados.setItem(i, j, item)

    def mostrar_menu_contextual(self, position):
        menu = QMenu()
        copiar_accion = menu.addAction("Copiar al portapapeles")
        filtrar_accion = menu.addAction("Mostrar solo esta fila")
        
        accion = menu.exec_(self.tabla_resultados.viewport().mapToGlobal(position))
        
        if accion == copiar_accion:
            self.copiar_seleccion()
        elif accion == filtrar_accion:
            self.filtrar_por_seleccion()

    def copiar_seleccion(self):
        items_seleccionados = self.tabla_resultados.selectedItems()
        if items_seleccionados:
            texto = items_seleccionados[0].text()
            clipboard = QApplication.clipboard()
            clipboard.setText(texto)
            self.status_label.setText(f"Copiado al portapapeles: {texto}")

    def filtrar_por_seleccion(self):
        items_seleccionados = self.tabla_resultados.selectedItems()
        if items_seleccionados:
            fila = items_seleccionados[0].row()
            datos_fila = []
            for columna in range(self.tabla_resultados.columnCount()):
                item = self.tabla_resultados.item(fila, columna)
                datos_fila.append(item.text() if item else "")
            
            self.tabla_resultados.setRowCount(1)
            for columna, dato in enumerate(datos_fila):
                self.tabla_resultados.setItem(0, columna, QTableWidgetItem(dato))
            
            self.status_label.setText("Mostrando solo el registro seleccionado")

    def seleccion_cambiada(self):
        items_seleccionados = self.tabla_resultados.selectedItems()
        if items_seleccionados:
            texto = items_seleccionados[0].text()
            self.status_label.setText(f"Seleccionado: {texto}")
            self.fix_button.setEnabled(True)
        else:
            self.status_label.setText("")
            self.fix_button.setEnabled(False)

class GestorPaquetes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gestor de Paquetes')
        self.setGeometry(100, 100, 1200, 800)

        # Crear el widget central con pestañas
        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)

        # Añadir pestañas
        actualizacion_tab = ActualizacionTab()
        central_widget.addTab(actualizacion_tab, "Actualización")

        consultas_tab = ConsultasTab()
        central_widget.addTab(consultas_tab, "Consulta")

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Establecer la fuente predeterminada más grande
    font = QFont()
    font.setPointSize(12)
    app.setFont(font)
    
    window = GestorPaquetes()
    sys.exit(app.exec_())
