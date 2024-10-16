from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QFrame, QFileDialog, \
    QTableWidget, QTableWidgetItem, QProgressBar, QMessageBox
from actions import upload_thread, load_files, download_thread
import shutil


class FileLoadingSystem(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Loading System")

        layout = QHBoxLayout()

        self.file_upload = FileUpload(self)

        self.files = Files()

        layout.addWidget(self.file_upload)

        layout.addWidget(self.files)

        self.setLayout(layout)

        self.setStyleSheet(
            """
                QWidget {
                    font-size: 22px;
                }
            """
        )


class DownloadButton(QPushButton):
    def __init__(self, parent: QTableWidget):
        super().__init__()
        self.parent = parent
        self.setText("Download")

        self.clicked.connect(self.download_file)

    def download_file(self):
        selected_row = self.parent.currentRow()
        if selected_row >= 0:
            file_path = self.parent.item(selected_row, 2).text()
            file_name = self.parent.item(selected_row, 1).text()
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(None, "Save File As", file_name, "All Files (*)",
                                                       options=options)
            if save_path:
                try:
                    dw_thread = download_thread(file_path, save_path, self.update_progress)
                    dw_thread.start()
                    dw_thread.join()
                    self.parent.parent().progress_bar.setValue(0)
                except Exception as exp:
                    print(exp)

    def update_progress(self, value):
        self.parent.parent().progress_bar.setValue(value)

class Files(QFrame):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel("Files")

        layout.addWidget(label)

        self.table = QTableWidget(parent=self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                'id',
                "filename",
                "filepath",
                "upload_time",
                "status",
                "download"
            ]
        )
        self.render_table()
        layout.addWidget(self.table)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(2)
        self.setStyleSheet("border-right: 2px solid black;")

    def render_table(self):
        try:
            self.table.setRowCount(0)
            for row_idx, (f_id, filename, filepath, upload_time, status) in enumerate(load_files()):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(f_id)))
                self.table.setItem(row_idx, 1, QTableWidgetItem(filename))
                self.table.setItem(row_idx, 2, QTableWidgetItem(filepath))
                self.table.setItem(row_idx, 3, QTableWidgetItem(upload_time.strftime("%Y-%m-%d %H:%M:%S")))
                self.table.setItem(row_idx, 4, QTableWidgetItem(status))
                self.table.setCellWidget(row_idx, 5, DownloadButton(self.table))
        except Exception as exp:
            print(f"render_table: {exp}")


class FileUpload(QFrame):
    def __init__(self, parent: FileLoadingSystem):
        self.parent = parent
        super().__init__()

        layout = QVBoxLayout()

        self.upload_button = QPushButton("File Upload")
        self.upload_button.clicked.connect(self.file_upload)
        layout.addWidget(self.upload_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(2)
        self.setStyleSheet("border-right: 2px solid black;")

    def file_upload(self):
        """Handles file selection and uploads the file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(None,
                                                   "Select file to upload",
                                                   "",
                                                   "All Files (*);;Text Files (*.txt)",
                                                   options=options)
        if file_path:
            up_thread = upload_thread(file_path, self.update_progress)
            up_thread.start()
            up_thread.join()
            self.parent.files.render_table()
            self.progress_bar.setValue(0)

    def update_progress(self, value):
        self.progress_bar.setValue(value)


def main():
    app = QApplication([])
    main_window = FileLoadingSystem()
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
