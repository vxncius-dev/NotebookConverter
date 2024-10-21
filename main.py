#!/usr/bin/env python3
from os import system, name
from typing import Optional, Dict, Any
from pathlib import Path
from subprocess import run, CalledProcessError
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from time import sleep


class NotebookConverter:
    def __init__(self: 'NotebookConverter') -> None:
        self.ambient: bool = self.check_ambient()
        self.ensure_dependencies()
        self.main()

    def check_ambient(self: 'NotebookConverter') -> bool:
        try:
            import google.colab
            colab_ambient = True
        except ImportError:
            colab_ambient = False

        local = "Google Colab" if colab_ambient else "Local"
        print(f"Running on {local}\n")
        return colab_ambient

    def ensure_dependencies(self: 'NotebookConverter') -> None:
        try:
            import p2j
            import ipynb_py_convert
        except ImportError as e:
            print(f"Error importing dependencies: {e}. Installing...")
            try:
                run(["pip", "install", "p2j"], check=True)
                run(["pip", "install", "ipynb-py-convert"], check=True)
                system('cls' if name == 'nt' else 'clear')
            except CalledProcessError as install_error:
                print(f"Error installing packages: {install_error}")

    def input_file(self: 'NotebookConverter') -> Optional[Dict[str, bytes]]:
        valid_files: Dict[str, bytes] = {}

        if self.ambient:
            from google.colab import drive, files
            drive.mount("/content/drive")
            uploaded = files.upload()

            for filename in uploaded.keys():
                if filename.endswith(('.py', '.ipynb')):
                    valid_files[filename] = uploaded[filename]

        else:
            print("Select the files (.py or .ipynb) you wish to upload:")
            root = Tk()
            root.withdraw()
            file_paths = askopenfilenames(title="Select files",
                                           filetypes=[("Python files", "*.py"),
                                                      ("Jupyter Notebooks", "*.ipynb")])

            for file_path in file_paths:
                filename = Path(file_path).name
                if filename.endswith(('.py', '.ipynb')):
                    with open(file_path, 'rb') as f:
                        valid_files[filename] = f.read()

        return valid_files if valid_files else None

    def process_file(self: 'NotebookConverter', filename: str, file_content: bytes) -> None:
        file_size = len(file_content)
        print(f"\nProcessing file: {filename}")
        print(f"File size: {file_size} bytes")

        local_path = f'/content/{filename}' if self.ambient else f'./{filename}'

        with open(local_path, 'wb') as f:
            f.write(file_content)

        if filename.endswith('.py'):
            self.convert_py_to_ipynb(local_path)
        elif filename.endswith('.ipynb'):
            self.convert_ipynb_to_py(local_path)

    def convert_py_to_ipynb(self: 'NotebookConverter', py_file: str) -> None:
        ipynb_file = py_file.replace('.py', '.ipynb')
        print(f"\nConverting {py_file} to {ipynb_file}...")
        run(['p2j', py_file])
        print(f"File converted: {ipynb_file}\n")
        self.export_file(ipynb_file)

    def convert_ipynb_to_py(self: 'NotebookConverter', ipynb_file: str) -> None:
        py_file = ipynb_file.replace('.ipynb', '.py')
        print(f"\nConverting {ipynb_file} to {py_file}...")
        run(['ipynb-py-convert', ipynb_file, py_file])
        print(f"File converted: {py_file}\n")
        self.export_file(py_file)

    def export_file(self: 'NotebookConverter', file_path: str) -> None:
        if self.ambient:
            from google.colab import files
            files.download(file_path)
            print(f"File {file_path} ready for download.")
        else:
            print(f"File saved at: {file_path}")

        another = input("Do you want to convert another file? (s/n): ").strip().lower()
        if another != 's':
            print("Exiting the program.")
            sleep(2)
            exit()
        else:
            self.main()

    def main(self: 'NotebookConverter') -> None:
        uploaded_files = self.input_file()
        if uploaded_files:
            for filename, content in uploaded_files.items():
                self.process_file(filename, content)
        else:
            print("No valid files uploaded.")


if __name__ == "__main__":
    NotebookConverter()
