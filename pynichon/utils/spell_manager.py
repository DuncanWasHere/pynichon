import importlib
import json
import os
from pathlib import Path


spell_manager = None

class SpellManager:
    _instance = None

    def __init__(self):
        self.spells_dir = "pynichon\spells"
        self.spells = {}
        self.load_spells()

    def load_spells(self):
        from pynichon.io.io_manager import get_io_manager

        for json_path in get_io_manager().get_spell_files(self.spells_dir):
            try:
                with open(json_path, "r") as f:
                    config = json.load(f)
                    spell_name = config["Info"]["Name"]
                    self.spells[spell_name] = Spell(json_path)
            except (KeyError, json.JSONDecodeError):
                print(f"Failed to load spell from {json_path}")

    def run_spell(self, nif_data, spell):
        if spell not in self.spells:
            raise ValueError(f"Spell {spell} not found.")
        self.spells[spell].execute(nif_data)


def get_spell_manager():
    global spell_manager
    if spell_manager is None:
        spell_manager = SpellManager()
    return spell_manager


class Spell:
    def __init__(self, json_path):
        self.json_path = json_path
        self.stem = Path(json_path).stem
        self.py_path = json_path.replace(".json", ".py")
        self.category = str(Path(json_path).parent.name).capitalize()

    def execute(self, nif_data):
        if not os.path.exists(self.py_path):
            raise FileNotFoundError(f"Python file not found for spell: {self.stem}")

        spec = importlib.util.spec_from_file_location("spell_module", self.py_path)
        spell_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(spell_module)

        if hasattr(spell_module, self.stem):
            getattr(spell_module, self.stem)(nif_data)
        else:
            raise AttributeError(f"No function {self.stem} in module {self.py_path}")