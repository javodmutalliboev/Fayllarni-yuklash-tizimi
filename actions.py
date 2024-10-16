import os.path
import threading

import mysql.connector
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import shutil


class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="javod",
            password="hHh(26Y2%C~w",
            database="file_loading_system"
        )

        self.cursor = self.conn.cursor()
        return (self.cursor, self.conn)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def insert_file_metadata(file_name, file_path):
    "Inserts the file metadata into the MySQL database."
    try:
        with Database() as (cursor, conn):
            query = "INSERT INTO file (filename, filepath, status)\
            VALUES (%s, %s, %s)"
            cursor.execute(query, (file_name, file_path, "uploaded"))
            conn.commit()
            print(f"{file_name} successfully uploaded.")

    except Exception as ex:
        print(f"Error inserting file metadata into MySQL: {ex}")


def copy_file_with_progress(src_path, dest_path, progress_callback=None):
    file_size = os.path.getsize(src_path)
    bytes_copied = 0
    with open(src_path, "rb") as f_in:
        with open(dest_path, 'wb') as f_out:
            while chunk := f_in.read(4096):
                f_out.write(chunk)
                bytes_copied += len(chunk)
                if progress_callback:
                    progress_callback(int((bytes_copied / file_size) * 100))


def upload_file(file_path, progress_callback=None):
    try:
        if file_path:
            file_name = os.path.basename(file_path)
            target_dir = "uploads"
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, file_name)

            base_name, extension = os.path.splitext(file_name)
            counter = 1
            while os.path.exists(target_path):
                file_name = f"{base_name} ({counter}){extension}"
                target_path = os.path.join(target_dir, file_name)
                counter += 1

            copy_file_with_progress(file_path, target_path, progress_callback)
            insert_file_metadata(file_name, target_path)

    except Exception as ex:
        print(f"Error during file upload: {ex}")


def load_files():
    try:
        with Database() as (cursor, conn):
            cursor.execute("SELECT * FROM file")
            files = cursor.fetchall()
            return files
    except Exception as ex:
        print(f"Error during loading files: {ex}")


upload_thread = lambda file_path, progress_callback: threading.Thread(target=upload_file,
                                                                      args=(file_path, progress_callback))


def download_file(file_path, save_path, progress_callback=None):
    try:
        copy_file_with_progress(file_path, save_path, progress_callback)
    except Exception as ex:
        print(f"Error downloading file: {ex}")


download_thread = lambda file_path, save_path, progress_callback: threading.Thread(target=download_file, args=(
    file_path, save_path, progress_callback))
