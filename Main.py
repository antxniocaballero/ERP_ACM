import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QTabWidget, QPushButton, QLineEdit,
                               QTableView, QLabel, QHeaderView, QDialog,
                               QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox,
                               QMessageBox, QFileDialog, QSplitter)
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QPixmap

from database import RecordDAO

class RecordTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._headers = ["ID", "Artista", "Álbum", "Formato", "Género", "Precio (€)", "Stock", "Ruta Imagen"]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

class RecordDialog(QDialog):
    def __init__(self, parent=None, record_data=None):
        super().__init__(parent)
        self.setWindowTitle("Guardar Disco")
        self.resize(450, 400)

        layout = QFormLayout(self)

        self.artist_input = QLineEdit()
        self.album_input = QLineEdit()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Vinilo (LP)", "Vinilo (EP)", "CD", "Casete"])
        self.genre_input = QLineEdit()

        self.price_input = QDoubleSpinBox()
        self.price_input.setSuffix(" €")
        self.price_input.setMaximum(999.99)

        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(1000)

        self.image_path = ""
        self.btn_image = QPushButton("📸 Seleccionar Portada...")
        self.btn_image.clicked.connect(self.select_image)
        self.lbl_image_path = QLabel("Ninguna imagen seleccionada")
        self.lbl_image_path.setStyleSheet("color: #d7ccc8; font-size: 11px;")

        layout.addRow("Artista:", self.artist_input)
        layout.addRow("Álbum:", self.album_input)
        layout.addRow("Formato:", self.format_combo)
        layout.addRow("Género:", self.genre_input)
        layout.addRow("Precio:", self.price_input)
        layout.addRow("Stock Actual:", self.stock_input)
        layout.addRow("Portada:", self.btn_image)
        layout.addRow("", self.lbl_image_path)

        if record_data:
            self.artist_input.setText(record_data[1])
            self.album_input.setText(record_data[2])
            self.format_combo.setCurrentText(record_data[3])
            self.genre_input.setText(record_data[4])
            self.price_input.setValue(float(record_data[5]))
            self.stock_input.setValue(int(record_data[6]))
            self.image_path = record_data[7]
            if self.image_path:
                self.lbl_image_path.setText(os.path.basename(self.image_path))

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Guardar")
        self.btn_cancel = QPushButton("Cancelar")

        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addRow(btn_layout)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar Portada", "", "Imágenes (*.png *.jpg *.jpeg)")
        if file_name:
            self.image_path = file_name
            self.lbl_image_path.setText(os.path.basename(file_name))

    def get_data(self):
        return {
            "artist": self.artist_input.text(),
            "album": self.album_input.text(),
            "format": self.format_combo.currentText(),
            "genre": self.genre_input.text(),
            "price": self.price_input.value(),
            "stock": self.stock_input.value(),
            "cover_path": self.image_path
        }

class InventoryWidget(QWidget):
    def __init__(self, dao):
        super().__init__()
        self.dao = dao
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Añadir")
        self.btn_edit = QPushButton("✏️ Modificar")
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_refresh = QPushButton("🔄 Recargar")

        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_refresh.clicked.connect(self.load_data)

        top_layout.addWidget(self.btn_add)
        top_layout.addWidget(self.btn_edit)
        top_layout.addWidget(self.btn_delete)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        splitter = QSplitter(Qt.Horizontal)

        self.table = QTableView()
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.clicked.connect(self.display_cover)
        splitter.addWidget(self.table)

        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        self.lbl_cover = QLabel("Selecciona un disco")
        self.lbl_cover.setAlignment(Qt.AlignCenter)
        self.lbl_cover.setMinimumSize(250, 250)
        self.lbl_cover.setStyleSheet("border: 2px dashed #8d6e63; background-color: #3e2723; color: #efebe9;")

        self.lbl_details = QLabel("")
        self.lbl_details.setAlignment(Qt.AlignCenter)
        self.lbl_details.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px; color: #efebe9;")

        side_layout.addWidget(self.lbl_cover)
        side_layout.addWidget(self.lbl_details)
        side_layout.addStretch()
        splitter.addWidget(side_panel)

        splitter.setSizes([700, 300])
        layout.addWidget(splitter)

        self.load_data()

    def load_data(self):
        data = self.dao.get_all_records()
        self.model = RecordTableModel(data)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnHidden(7, True)

    def display_cover(self, index):
        row = index.row()
        artist = self.model._data[row][1]
        album = self.model._data[row][2]
        image_path = self.model._data[row][7]

        self.lbl_details.setText(f"{artist}\n{album}")

        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.lbl_cover.setPixmap(pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_cover.setStyleSheet("border: none; background-color: transparent;")
        else:
            self.lbl_cover.clear()
            self.lbl_cover.setText("Sin Imagen")
            self.lbl_cover.setStyleSheet("border: 2px dashed #8d6e63; background-color: #3e2723; color: #efebe9;")

    def open_add_dialog(self):
        dialog = RecordDialog(self)
        if dialog.exec():
            d = dialog.get_data()
            if d['artist'] and d['album']:
                self.dao.insert_record(d['artist'], d['album'], d['format'], d['genre'], d['price'], d['stock'], d['cover_path'])
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", "El artista y el álbum son obligatorios.")

    def edit_selected(self):
        selection = self.table.selectionModel().selectedRows()
        if selection:
            row = selection[0].row()
            record_id = int(self.model._data[row][0])
            record_data = self.model._data[row]

            dialog = RecordDialog(self, record_data)
            if dialog.exec():
                d = dialog.get_data()
                if d['artist'] and d['album']:
                    self.dao.update_record(record_id, d['artist'], d['album'], d['format'], d['genre'], d['price'], d['stock'], d['cover_path'])
                    self.load_data()
                    self.display_cover(self.model.index(row, 0))
                else:
                    QMessageBox.warning(self, "Error", "El artista y el álbum son obligatorios.")
        else:
            QMessageBox.information(self, "Aviso", "Selecciona un disco de la tabla para modificarlo.")

    def delete_selected(self):
        selection = self.table.selectionModel().selectedRows()
        if selection:
            row = selection[0].row()
            record_id = self.model._data[row][0]

            confirm = QMessageBox.question(self, "Confirmar", "¿Eliminar este disco de la base de datos?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.dao.delete_record(record_id)
                self.load_data()
                self.lbl_cover.clear()
                self.lbl_details.clear()

class MainWindow(QMainWindow):
    def __init__(self, dao):
        super().__init__()
        self.setWindowTitle("Music Murcia Pro - Base de Datos MySQL")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_inventory = InventoryWidget(dao)
        self.tabs.addTab(self.tab_inventory, "💽 Inventario y Catálogo")

        self.tab_sales = QLabel("Módulo de Caja y Ventas")
        self.tab_sales.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(self.tab_sales, "🛒 Caja y Ventas")

        self.showMaximized()

    def closeEvent(self, event):
        self.centralWidget().widget(0).dao.close_connection()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dao = RecordDAO()

    style_path = os.path.join(os.path.dirname(__file__), "styless.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print("Advertencia: No se encontró el archivo styless.qss")

    window = MainWindow(dao)
    sys.exit(app.exec())