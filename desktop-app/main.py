import sys
import requests
import pandas as pd
from io import StringIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                              QTableWidget, QTableWidgetItem, QMessageBox, 
                              QTabWidget, QGroupBox, QGridLayout, QListWidget,
                              QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


API_BASE_URL = 'http://localhost:8000/api'


class UploadThread(QThread):
    """Thread for uploading files without blocking the UI"""
    upload_complete = pyqtSignal(dict)
    upload_error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f'{API_BASE_URL}/datasets/upload_csv/', files=files)
                
                if response.status_code == 201:
                    self.upload_complete.emit(response.json())
                else:
                    error_msg = response.json().get('error', 'Unknown error')
                    self.upload_error.emit(error_msg)
        except Exception as e:
            self.upload_error.emit(str(e))


class MatplotlibCanvas(FigureCanvas):
    """Canvas for embedding matplotlib figures"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.figure)
        self.setParent(parent)


class ChemicalEquipmentVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_dataset = None
        self.history = []
        self.init_ui()
        self.load_history()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Chemical Equipment Parameter Visualizer')
        self.setGeometry(100, 100, 1400, 900)
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #000000;
                color: white;
                border: 2px solid #000000;
                padding: 14px 30px;
                border-radius: 0px;
                font-weight: 600;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                border-color: #cccccc;
                color: #666666;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
            }
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e0e0e0;
                border-radius: 0px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fafafa;
                color: #000000;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #000000;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #ffffff;
                color: #666666;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                padding: 12px 30px;
                font-weight: 500;
                font-size: 13px;
                min-width: 90px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #000000;
                border-bottom: 2px solid #000000;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                color: #000000;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #000000;
                color: white;
                padding: 10px;
                border: none;
                font-weight: 600;
                font-size: 13px;
            }
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 0px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                color: #333333;
            }
            QListWidget::item:hover {
                background-color: #fafafa;
            }
            QListWidget::item:selected {
                background-color: #f0f0f0;
                color: #000000;
            }
        """)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_label = QLabel('Chemical Equipment Parameter Visualizer')
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont('Arial', 28, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet('color: #000000; padding: 30px; background-color: #ffffff; border-bottom: 2px solid #000000;')
        main_layout.addWidget(header_label)

        # Upload section
        upload_group = QGroupBox('Upload CSV File')
        upload_layout = QHBoxLayout()
        
        self.file_label = QLabel('No file selected')
        self.file_label.setStyleSheet('color: #666666; font-size: 14px;')
        upload_layout.addWidget(self.file_label)
        
        self.select_file_btn = QPushButton('Choose File')
        self.select_file_btn.clicked.connect(self.select_file)
        upload_layout.addWidget(self.select_file_btn)
        
        self.upload_btn = QPushButton('Upload & Analyze')
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        upload_layout.addWidget(self.upload_btn)
        
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)

        # Tab widget for main content
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Summary Tab
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.summary_tab, 'Summary')

        # Visualizations Tab
        self.viz_tab = QWidget()
        self.setup_visualizations_tab()
        self.tabs.addTab(self.viz_tab, 'Visualizations')

        # Data Table Tab
        self.table_tab = QWidget()
        self.setup_table_tab()
        self.tabs.addTab(self.table_tab, 'Data Table')

        # History Tab
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, 'History')

        self.show()

    def setup_summary_tab(self):
        """Setup the summary statistics tab"""
        layout = QVBoxLayout()
        
        # Stats grid
        stats_group = QGroupBox('Key Statistics')
        stats_layout = QGridLayout()
        
        self.total_count_label = QLabel('0')
        self.total_count_label.setAlignment(Qt.AlignCenter)
        self.total_count_label.setStyleSheet('font-size: 32px; font-weight: bold; color: #000000;')
        
        self.avg_flowrate_label = QLabel('0.00')
        self.avg_flowrate_label.setAlignment(Qt.AlignCenter)
        self.avg_flowrate_label.setStyleSheet('font-size: 32px; font-weight: bold; color: #000000;')
        
        self.avg_pressure_label = QLabel('0.00')
        self.avg_pressure_label.setAlignment(Qt.AlignCenter)
        self.avg_pressure_label.setStyleSheet('font-size: 32px; font-weight: bold; color: #000000;')
        
        self.avg_temperature_label = QLabel('0.00')
        self.avg_temperature_label.setAlignment(Qt.AlignCenter)
        self.avg_temperature_label.setStyleSheet('font-size: 32px; font-weight: bold; color: #000000;')
        
        stats_layout.addWidget(QLabel('Total Equipment'), 0, 0)
        stats_layout.addWidget(self.total_count_label, 1, 0)
        stats_layout.addWidget(QLabel('Avg Flowrate'), 0, 1)
        stats_layout.addWidget(self.avg_flowrate_label, 1, 1)
        stats_layout.addWidget(QLabel('Avg Pressure'), 0, 2)
        stats_layout.addWidget(self.avg_pressure_label, 1, 2)
        stats_layout.addWidget(QLabel('Avg Temperature'), 0, 3)
        stats_layout.addWidget(self.avg_temperature_label, 1, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Equipment types
        self.types_list = QListWidget()
        self.types_list.setStyleSheet('background-color: white;')
        types_group = QGroupBox('Equipment Type Distribution')
        types_layout = QVBoxLayout()
        types_layout.addWidget(self.types_list)
        types_group.setLayout(types_layout)
        layout.addWidget(types_group)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        self.pdf_btn = QPushButton('Download PDF Report')
        self.pdf_btn.setEnabled(False)
        self.pdf_btn.clicked.connect(self.download_pdf)
        btn_layout.addWidget(self.pdf_btn)
        layout.addLayout(btn_layout)
        
        self.summary_tab.setLayout(layout)

    def setup_visualizations_tab(self):
        """Setup the visualizations tab with matplotlib charts"""
        layout = QVBoxLayout()
        
        # Create matplotlib canvases
        self.canvas1 = MatplotlibCanvas(self, width=6, height=4)
        self.canvas2 = MatplotlibCanvas(self, width=6, height=4)
        self.canvas3 = MatplotlibCanvas(self, width=6, height=4)
        
        layout.addWidget(self.canvas1)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.canvas2)
        h_layout.addWidget(self.canvas3)
        layout.addLayout(h_layout)
        
        self.viz_tab.setLayout(layout)

    def setup_table_tab(self):
        """Setup the data table tab"""
        layout = QVBoxLayout()
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        self.data_table.setStyleSheet('background-color: white;')
        self.data_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.data_table)
        self.table_tab.setLayout(layout)

    def setup_history_tab(self):
        """Setup the history tab"""
        layout = QVBoxLayout()
        
        header = QLabel('Recent Uploads (Last 5)')
        header.setStyleSheet('font-size: 16px; font-weight: bold; color: #2d3748;')
        layout.addWidget(header)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet('background-color: white;')
        self.history_list.itemDoubleClicked.connect(self.load_dataset_from_history)
        layout.addWidget(self.history_list)
        
        self.history_tab.setLayout(layout)

    def select_file(self):
        """Open file dialog to select CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f'Selected: {file_path.split("/")[-1]}')
            self.upload_btn.setEnabled(True)

    def upload_file(self):
        """Upload the selected CSV file"""
        if not hasattr(self, 'selected_file'):
            return
        
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText('Uploading...')
        
        # Start upload in separate thread
        self.upload_thread = UploadThread(self.selected_file)
        self.upload_thread.upload_complete.connect(self.on_upload_success)
        self.upload_thread.upload_error.connect(self.on_upload_error)
        self.upload_thread.start()

    def on_upload_success(self, data):
        """Handle successful upload"""
        self.current_dataset = data
        self.update_ui_with_dataset(data)
        self.load_history()
        
        # Create and show success dialog with detailed info
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Upload Successful')
        msg.setText('File uploaded and analyzed successfully!')
        msg.setInformativeText(f"Total Equipment: {data.get('total_count', 0)}\n"
                               f"Equipment Types: {len(data.get('equipment_types', {}))}\n"
                               f"Average Flowrate: {data.get('avg_flowrate', 0):.2f}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #000000;
                color: #ffffff;
                border: none;
                padding: 8px 24px;
                font-weight: 600;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #333333;
            }
        """)
        msg.exec_()
        
        self.upload_btn.setText('Upload & Analyze')
        self.upload_btn.setEnabled(True)
        self.file_label.setText('No file selected')

    def on_upload_error(self, error_msg):
        """Handle upload error"""
        QMessageBox.critical(self, 'Error', f'Upload failed: {error_msg}')
        self.upload_btn.setText('Upload & Analyze')
        self.upload_btn.setEnabled(True)

    def update_ui_with_dataset(self, dataset):
        """Update all UI elements with dataset information"""
        # Update summary statistics
        self.total_count_label.setText(str(dataset['total_count']))
        self.avg_flowrate_label.setText(f"{dataset['avg_flowrate']:.2f}")
        self.avg_pressure_label.setText(f"{dataset['avg_pressure']:.2f}")
        self.avg_temperature_label.setText(f"{dataset['avg_temperature']:.2f}")
        
        # Update equipment types list
        self.types_list.clear()
        for eq_type, count in dataset['equipment_types'].items():
            item = QListWidgetItem(f'{eq_type}: {count}')
            self.types_list.addItem(item)
        
        # Update data table
        equipment_items = dataset.get('equipment_items', [])
        self.data_table.setRowCount(len(equipment_items))
        
        for row, item in enumerate(equipment_items):
            self.data_table.setItem(row, 0, QTableWidgetItem(item['equipment_name']))
            self.data_table.setItem(row, 1, QTableWidgetItem(item['type']))
            self.data_table.setItem(row, 2, QTableWidgetItem(f"{item['flowrate']:.2f}"))
            self.data_table.setItem(row, 3, QTableWidgetItem(f"{item['pressure']:.2f}"))
            self.data_table.setItem(row, 4, QTableWidgetItem(f"{item['temperature']:.2f}"))
        
        # Update visualizations
        self.update_visualizations(dataset)
        
        # Enable PDF button
        self.pdf_btn.setEnabled(True)

    def update_visualizations(self, dataset):
        """Update matplotlib visualizations"""
        # Chart 1: Equipment Type Distribution (Pie Chart)
        self.canvas1.figure.clear()
        ax1 = self.canvas1.figure.add_subplot(111)
        
        types = list(dataset['equipment_types'].keys())
        counts = list(dataset['equipment_types'].values())
        colors = ['#667eea', '#764ba2', '#48bb78', '#ed8936', '#e53e3e', '#319795']
        
        ax1.pie(counts, labels=types, autopct='%1.1f%%', colors=colors[:len(types)], 
                startangle=90, textprops={'color': 'black', 'fontweight': 'bold'})
        ax1.set_title('Equipment Type Distribution', fontsize=14, fontweight='bold', color='#000000')
        self.canvas1.figure.patch.set_facecolor('#ffffff')
        ax1.set_facecolor('#ffffff')
        self.canvas1.draw()

        # Chart 2: Average Parameters (Bar Chart)
        self.canvas2.figure.clear()
        ax2 = self.canvas2.figure.add_subplot(111)
        
        parameters = ['Flowrate', 'Pressure', 'Temperature']
        values = [dataset['avg_flowrate'], dataset['avg_pressure'], dataset['avg_temperature']]
        colors_bar = ['#667eea', '#764ba2', '#48bb78']
        
        ax2.bar(parameters, values, color=colors_bar, edgecolor='#ffffff', linewidth=1.5)
        ax2.set_title('Average Parameters', fontsize=12, fontweight='bold', color='#000000')
        ax2.set_ylabel('Value', fontweight='bold')
        ax2.grid(axis='y', alpha=0.2, color='#e0e0e0')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        self.canvas2.figure.patch.set_facecolor('#ffffff')
        ax2.set_facecolor('#ffffff')
        self.canvas2.draw()

        # Chart 3: Parameter Comparison for First 10 Items (Line Chart)
        self.canvas3.figure.clear()
        ax3 = self.canvas3.figure.add_subplot(111)
        
        equipment_items = dataset.get('equipment_items', [])[:10]
        if equipment_items:
            names = [item['equipment_name'][:10] for item in equipment_items]
            flowrates = [item['flowrate'] for item in equipment_items]
            pressures = [item['pressure'] for item in equipment_items]
            temperatures = [item['temperature'] for item in equipment_items]
            
            ax3.plot(names, flowrates, marker='o', label='Flowrate', color='#667eea', linewidth=2, markersize=8)
            ax3.plot(names, pressures, marker='s', label='Pressure', color='#764ba2', linewidth=2, markersize=8)
            ax3.plot(names, temperatures, marker='^', label='Temperature', color='#48bb78', linewidth=2, markersize=8)
            
            ax3.set_title('Parameters Comparison (First 10)', fontsize=12, fontweight='bold', color='#000000')
            ax3.set_xlabel('Equipment', fontweight='bold')
            ax3.set_ylabel('Value', fontweight='bold')
            ax3.legend(frameon=True, fancybox=False, edgecolor='#e0e0e0')
            ax3.grid(alpha=0.2, color='#e0e0e0')
            ax3.spines['top'].set_visible(False)
            ax3.spines['right'].set_visible(False)
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
            self.canvas3.figure.patch.set_facecolor('#ffffff')
            ax3.set_facecolor('#ffffff')
            self.canvas3.figure.tight_layout()
        
        self.canvas3.draw()

    def load_history(self):
        """Load dataset history from API"""
        try:
            response = requests.get(f'{API_BASE_URL}/history/')
            if response.status_code == 200:
                self.history = response.json()
                self.update_history_list()
        except Exception as e:
            print(f'Error loading history: {e}')

    def update_history_list(self):
        """Update the history list widget"""
        self.history_list.clear()
        for dataset in self.history:
            item_text = f"{dataset['name']} - {dataset['total_count']} items - {dataset['uploaded_at'][:10]}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, dataset['id'])
            self.history_list.addItem(item)

    def load_dataset_from_history(self, item):
        """Load a dataset when clicked in history"""
        dataset_id = item.data(Qt.UserRole)
        try:
            response = requests.get(f'{API_BASE_URL}/datasets/{dataset_id}/')
            if response.status_code == 200:
                self.current_dataset = response.json()
                self.update_ui_with_dataset(self.current_dataset)
                self.tabs.setCurrentIndex(0)  # Switch to summary tab
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load dataset: {e}')

    def download_pdf(self):
        """Download PDF report for current dataset"""
        if not self.current_dataset:
            return
        
        try:
            dataset_id = self.current_dataset['id']
            response = requests.get(f'{API_BASE_URL}/datasets/{dataset_id}/generate_pdf/', stream=True)
            
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    'Save PDF Report', 
                    f'equipment_report_{dataset_id}.pdf',
                    'PDF Files (*.pdf)'
                )
                
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', 'PDF report downloaded successfully!')
            else:
                QMessageBox.critical(self, 'Error', 'Failed to generate PDF report')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error downloading PDF: {e}')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    window = ChemicalEquipmentVisualizerApp()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
