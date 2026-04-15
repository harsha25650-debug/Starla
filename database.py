import json
import os
from typing import Any

class Database:
    def __init__(self, file="database.json"):
        self.file = file
        self.data = {}
        self.load()

    # 📥 LOAD DATA
    def load(self):
        if not os.path.exists(self.file):
            self.data = {}
            self.save()
        else:
            with open(self.file, "r") as f:
                try:
                    self.data = json.load(f)
                except:
                    self.data = {}

    # 💾 SAVE DATA
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=4)

    # 📦 GET DATA
    def get(self, path: str, default=None):
        keys = path.split(".")
        data = self.data

        for key in keys:
            if key not in data:
                return default
            data = data[key]

        return data

    # 📝 SET DATA
    def set(self, path: str, value: Any):
        keys = path.split(".")
        data = self.data

        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]

        data[keys[-1]] = value
        self.save()

    # ➕ ADD TO LIST
    def add(self, path: str, value: Any):
        current = self.get(path, [])
        if not isinstance(current, list):
            current = []

        current.append(value)
        self.set(path, current)

    # ➖ REMOVE FROM LIST
    def remove(self, path: str, value: Any):
        current = self.get(path, [])
        if isinstance(current, list) and value in current:
            current.remove(value)
            self.set(path, current)

    # 🔢 INCREMENT VALUE
    def increment(self, path: str, amount: int = 1):
        value = self.get(path, 0)
        if not isinstance(value, int):
            value = 0

        value += amount
        self.set(path, value)

    # ❌ DELETE KEY
    def delete(self, path: str):
        keys = path.split(".")
        data = self.data

        for key in keys[:-1]:
            if key not in data:
                return
            data = data[key]

        if keys[-1] in data:
            del data[keys[-1]]
            self.save()
