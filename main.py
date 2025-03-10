#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from subprocess import run
from typing import Optional, Dict

class NotebookConverter:
    def __init__(self) -> None:
        self.main()

    @property
    def ambient(self) -> bool:
        try:
            import google.colab
            return True
        except ImportError:
            return False

    def input_file(self) -> Optional[Dict[str, bytes]]:
        valid_files: Dict[str, bytes] = {}

        if self.ambient:
            from google.colab import drive, files
            drive.mount("/content/drive")
            uploaded = files.upload()
            valid_files = {f: uploaded[f] for f in uploaded if f.endswith(('.py', '.ipynb'))}

        elif os.name == 'nt':
            from tkinter import Tk
            from tkinter.filedialog import askopenfilenames
            print("Select the files (.py or .ipynb):")
            root = Tk()
            root.withdraw()
            file_paths = askopenfilenames(title="Select files",
                                          filetypes=[("Python files", "*.py"),
                                                     ("Jupyter Notebooks", "*.ipynb")])

        else:
            file_paths = input("Enter the full path of the files (comma-separated): ").split(',')

        for file_path in file_paths:
            file_path = file_path.strip()
            if Path(file_path).suffix in {".py", ".ipynb"}:
                with open(file_path, 'rb') as f:
                    valid_files[Path(file_path).name] = f.read()

        return valid_files if valid_files else None

    def process_file(self, filename: str, file_content: bytes) -> None:
        local_path = f'/content/{filename}' if self.ambient else f'./{filename}'

        with open(local_path, 'wb') as f:
            f.write(file_content)

        print(f"\nProcessing file: {filename} ({len(file_content)} bytes)")
        self.convert_file(local_path)

    def convert_file(self, file_path: str) -> None:
        if file_path.endswith('.py'):
            self.convert_py_to_ipynb(file_path)
        elif file_path.endswith('.ipynb'):
            self.convert_ipynb_to_py(file_path)

    def convert_py_to_ipynb(self, py_file: str) -> None:
        ipynb_file = py_file.replace('.py', '.ipynb')
        print(f"Converting {py_file} to {ipynb_file}...")
        run(['p2j', py_file], check=True)
        self.export_file(ipynb_file)

    def convert_ipynb_to_py(self, ipynb_file: str) -> None:
        py_file = ipynb_file.replace('.ipynb', '.py')
        print(f"Converting {ipynb_file} to {py_file}...")
        run(['ipynb-py-convert', ipynb_file, py_file], check=True)
        self.export_file(py_file)

    def export_file(self, file_path: str) -> None:
        if self.ambient:
            from google.colab import files
            files.download(file_path)
            print(f"File {file_path} ready for download.")
        else:
            print(f"File saved at: {file_path}")

        if input("Do you want to convert another file? (y/n): ").strip().lower() != 'y':
            print("Exiting...")
            sys.exit()

    def main(self) -> None:
        uploaded_files = self.input_file()
        if uploaded_files:
            for filename, content in uploaded_files.items():
                self.process_file(filename, content)
        else:
            print("No valid files uploaded.")


if __name__ == "__main__":
    NotebookConverter()
