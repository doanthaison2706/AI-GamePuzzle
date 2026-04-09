import json
import os

class SettingsManager:
    # Singleton instance
    _instance = None

    # Defaults if config file doesn't exist
    DEFAULT_SETTINGS = {
        "music_volume": 80,
        "move_volume": 70,
        "brightness": 100,
    }

    CONFIG_FILE = "configs/settings.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.settings = dict(self.DEFAULT_SETTINGS)
        self.load()

    def get(self, key):
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))

    def update(self, new_settings):
        """Update multiple settings and save to file."""
        for k, v in new_settings.items():
            if k in self.DEFAULT_SETTINGS:
                self.settings[k] = v

        self.save()

    def load(self):
        """Load settings from JSON file."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if k in self.DEFAULT_SETTINGS:
                            self.settings[k] = v
            except Exception as e:
                print(f"Error loading settings: {e}. Using defaults.")

    def save(self):
        """Save current settings to JSON file."""
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
