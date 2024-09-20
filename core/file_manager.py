import os
import shutil

class FileManager:
    def __init__(self):
        self.files = []
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def add_file(self, file_path):
        self.files.append(file_path)

    def get_all_files(self):
        return self.files.copy()

    def clear_files(self):
        self.files.clear()
        self.clear_output_dir()

    def clear_output_dir(self):
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'无法删除 {file_path}。原因: {e}')

    def get_output_dir(self):
        return self.output_dir

    def save_output_file(self, content, filename):
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    def remove_file(self, file_path):
        if file_path in self.files:
            self.files.remove(file_path)