import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QDateEdit, QLabel, QDateTimeEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt6.QtGui import QIcon, QPixmap
import pandas as pd
import traceback
import csv
from PyQt6.QtCore import QDate, Qt, QDateTime
from PyQt6.QtCore import QPoint
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, SimpleDocTemplate

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Tabs and export")
        widget = QWidget()
        self.setCentralWidget(widget)
        tab_widget = QTabWidget()
        tab = QWidget()
        graph_tab = QWidget()
        tab_layout = QVBoxLayout()
        graph_tab_layout = QVBoxLayout()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.df = pd.read_csv("C:\\Users\\Arpit\\Downloads\\map.csv")
        self.matplotlib_widget = MatplotlinWidget()
        layout.addWidget(self.matplotlib_widget)
        self.legend_lines = {}
        self.plot_data()

        #date start
        # Create the date and time range filter widgets
        self.start_date_time_edit = QDateTimeEdit()
        self.start_date_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_date_time_edit.setDateTime(QDateTime.currentDateTime().addDays(-7))  # Default start date is 7 days ago
        self.start_date_time_edit.dateTimeChanged.connect(self.filter_table)

        self.end_date_time_edit = QDateTimeEdit()
        self.end_date_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_date_time_edit.setDateTime(QDateTime.currentDateTime())  # Default end date is current date
        self.end_date_time_edit.dateTimeChanged.connect(self.filter_table)


        # Create labels for displaying the filter date range
        self.filter_start_label = QLabel()
        self.filter_end_label = QLabel()

        self.toolbar = NavigationToolbar(self.matplotlib_widget.canvas, self)

        num_rows, num_cols = self.df.shape
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_cols)
        col_names = self.df.columns
        self.table.setHorizontalHeaderLabels(col_names)

        for row in range(num_rows):
            row_data = self.df.iloc[row].values.tolist()
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

        export_btn_csv = QPushButton("Export as CSV")
        export_btn_pdf = QPushButton("Export as PDF")
        tab_layout.addWidget(self.table)
        tab_layout.addWidget(QLabel("Start Date:"))
        tab_layout.addWidget(self.start_date_time_edit)
        tab_layout.addWidget(self.filter_start_label)
        tab_layout.addWidget(QLabel("End Date:"))
        tab_layout.addWidget(self.end_date_time_edit)
        tab_layout.addWidget(self.filter_end_label)
        tab_layout.addWidget(export_btn_csv)
        tab_layout.addWidget(export_btn_pdf)
        tab.setLayout(tab_layout)
        tab_widget.addTab(tab, "Table")

        graph_export_btn_png = QPushButton("Export as PNG")
        graph_export_btn_pdf = QPushButton("Export as PDF")
        graph_tab_layout.addWidget(self.toolbar)
        graph_tab_layout.addWidget(self.matplotlib_widget.canvas)
        graph_tab_layout.addWidget(graph_export_btn_png)
        graph_tab_layout.addWidget(graph_export_btn_pdf)

        graph_tab.setLayout(graph_tab_layout)
        tab_widget.addTab(graph_tab, "Graph")

        layout.addWidget(tab_widget)
        widget.setLayout(layout)

        export_btn_csv.clicked.connect(self.export_table_as_csv)
        export_btn_pdf.clicked.connect(self.export_table_as_pdf)
        graph_export_btn_png.clicked.connect(self.export_graph_as_png)
        graph_export_btn_pdf.clicked.connect(self.export_graph_as_pdf)


    def filter_table(self):
        start_date_time = self.start_date_time_edit.dateTime()
        end_date_time = self.end_date_time_edit.dateTime()
        filter_start_date_time_str = start_date_time.toString("yyyy-MM-dd HH:mm:ss")
        filter_end_date_time_str = end_date_time.toString("yyyy-MM-dd HH:mm:ss")

        self.filter_start_label.setText(f"Filter Start Date and Time: {filter_start_date_time_str}")
        self.filter_end_label.setText(f"Filter End Date and Time: {filter_end_date_time_str}")

        for row in range(self.table.rowCount()):
            date_item = self.table.item(row, 6)
            time_item = self.table.item(row, 7)
            if date_item is not None and time_item is not None:
                date_str = date_item.text()
                time_str = time_item.text()
                date_time_str = f"{date_str} {time_str}"
                date_time = QDateTime.fromString(date_time_str, "yyyy-MM-dd HH:mm:ss")

                if start_date_time <= date_time <= end_date_time:
                    self.table.setRowHidden(row, False)  # Show the row
                else:
                    self.table.setRowHidden(row, True)  # Hide the row



    def plot_data(self):
        df = pd.read_csv("C:\\Users\\Arpit\\Downloads\\map.csv")
        column = ["HGHT", "TEMP", "PRES", "RELH", "DRCT", "SPED"]
        for col in column:
            col_data = df[col]
            x = range(len(col_data))
            line = self.matplotlib_widget.plot_column(x, col_data, label=col)
            # Store the line corresponding to the legend entry
            self.legend_lines[col] = line

        self.matplotlib_widget.axis.grid(True)
        legend = self.matplotlib_widget.axis.legend()
        self.matplotlib_widget.canvas.draw()
        for legend_handle in legend.legendHandles:
            legend_handle.set_picker(True)

        # Connect the pick event of the legend to the on_pick method
        self.matplotlib_widget.canvas.mpl_connect('pick_event', self.on_pick)

    def on_pick(self, event):
        # Get the legend entry that was picked
        legend_entry = event.artist

        # Get the text of the legend entry
        text = legend_entry.get_label()

        # Get the corresponding line from the dictionary
        line = self.legend_lines[text]

        # Toggle the visibility of the line
        line.set_visible(not line.get_visible())

        # Redraw the canvas to reflect the changes
        self.matplotlib_widget.canvas.draw()


    def export_table_as_csv(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Export Table", "", "CSV (*.csv)")
        if file_path:
            try:
                visible_rows = []
                num_cols = self.table.columnCount()

                # Append column labels as the first row
                column_labels = [self.table.horizontalHeaderItem(col).text() for col in range(num_cols)]
                visible_rows.append(column_labels)

                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        visible_row_data = []
                        for col in range(num_cols):
                            item = self.table.item(row, col)
                            if item is not None:
                                visible_row_data.append(item.text())
                            else:
                                visible_row_data.append("")
                        visible_rows.append(visible_row_data)

                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerows(visible_rows)
            except Exception as e:
                print("An error occurred during file export:")
                print(traceback.format_exc())
        else:
            print("Invalid file path. Export canceled.")

    def export_table_as_pdf(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Export Table", "", "PDF (*.pdf)")
        if file_path:
            try:
                start_date = self.start_date_edit.date()
                end_date = self.end_date_edit.date()

                visible_rows = []
                num_cols = self.table.columnCount()

                for row in range(self.table.rowCount()):
                    if not self.table.isRowHidden(row):
                        visible_row_data = []
                        for col in range(num_cols):
                            item = self.table.item(row, col)
                            if item is not None:
                                visible_row_data.append(item.text())
                            else:
                                visible_row_data.append("")
                        visible_rows.append(visible_row_data)

                # Create a SimpleDocTemplate for generating the PDF
                doc = SimpleDocTemplate(file_path, pagesize=letter)

                # Table data
                column_labels = [self.table.horizontalHeaderItem(col).text() for col in range(num_cols)]  # Column labels
                data = [column_labels]  # Initialize the data with column labels

                # Add the visible rows to the data
                data.extend(visible_rows)

                # Create the table
                table = Table(data)

                # Styling the table
                table.setStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 10),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ]
                )

                elements = [table]

                # Build the PDF
                doc.build(elements)
            except Exception as e:
                print("An error occurred during file export:")
                print(traceback.format_exc())
        else:
            print("Invalid file path. Export canceled.")


    def export_graph_as_png(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Export Graph", "", "PNG (*.png)")
        if file_path:
            pixmap = self.matplotlib_widget.canvas.grab()
            pixmap.save(file_path, "PNG")

    def export_graph_as_pdf(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Export Graph", "", "PDF (*.pdf)")
        if file_path:
            fig = self.matplotlib_widget.figure
            fig.savefig(file_path, format='pdf')

class MatplotlinWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.axis = self.figure.add_subplot(111)

    def plot_column(self, x, y, label = None):
        line, = self.axis.plot(x, y, label=label)
        # Redraw the canvas
        self.canvas.draw()
        # Return the line object
        return line
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
