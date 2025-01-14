import os
import re

from pynichon.utils.spell_manager import SpellManager
from pynichon.io.nif_io import NifFile

io_manager = None

class IOManager:
    _instance = None

    def __init__(self):
        self.input_paths = []
        self.output_dir = ""
        self.include_subdirs = False
        self.skip_errors = False
        self.filter_enabled = False
        self.rename_enabled = False
        self.only_modified = False
        self.filter_regex = None
        self.rename_regex = None

    def set_settings_from_window(self, window):
        self.input_paths.clear()
        self.input_paths.append(window.tb_input_dir.text())
        self.output_dir = window.tb_output_dir.text()
        self.include_subdirs = window.cb_include_subdirs.isChecked()
        self.skip_errors = window.cb_skip_errors.isChecked()
        self.filter_enabled = window.cb_filter.isChecked()
        self.rename_enabled = window.cb_rename.isChecked()
        self.only_modified = window.cb_only_modified.isChecked()
        self.filter_regex = re.compile(window.tb_filter.text())
        self.rename_regex = re.compile(window.tb_rename.text())

    def process_files(self, spell):
        for file_path in self.input_paths:
            try:
                if os.path.isfile(file_path):
                    self.process_file(file_path, spell)
                elif os.path.isdir(file_path):
                    for root, _, files in os.walk(file_path):
                        if not self.include_subdirs and root != file_path:
                            continue
                        for file in files:
                            full_path = os.path.join(root, file)
                            self.process_file(full_path, spell)
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                if self.skip_errors:
                    print("Skipping file due to error.")
                else:
                    return

    def process_file(self, file_path, spell):
        from pynichon.utils.spell_manager import get_spell_manager

        if self.filter_enabled and not self.filter_regex.search(file_path):
            return

        nif_data = NifFile.load_nif(file_path)
        get_spell_manager().run_spell(nif_data, spell)

        output_path = file_path if not self.output_dir else os.path.join(
            self.output_dir, os.path.relpath(file_path, self.input_paths[0]))
        if self.rename_enabled and self.rename_regex:
            new_name = self.rename_regex.sub('', os.path.basename(output_path))
            output_path = os.path.join(os.path.dirname(output_path), new_name)
        NifFile.save_nif(nif_data, output_path)

    def get_spell_files(self, spells_dir):
        json_files = []
        for root, _, files in os.walk(spells_dir):
            json_files.extend(
                os.path.join(root, file)
                for file in files
                if file.endswith(".json")
            )
        return json_files

    def get_output_path(self, input_path):
        output_path = input_path if not self.output_dir else os.path.join(
            self.output_dir, os.path.relpath(input_path, self.input_paths[0])
        )
        if self.rename_enabled and self.rename_regex:
            new_name = self.rename_regex.sub("", os.path.basename(output_path))
            output_path = os.path.join(os.path.dirname(output_path), new_name)
        return output_path


def get_io_manager():
    global io_manager
    if io_manager is None:
        io_manager = IOManager()
    return io_manager