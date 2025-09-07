import json
import os
from pathlib import Path

from log import Logger


class StateManager:
    """Manages application state persistence"""

    def __init__(self, state_file: str = None):
        if state_file is None:
            self.state_file = self._get_default_state_file()
        else:
            self.state_file = Path(state_file)

        self.logger = Logger.get_logger()
        self._state = {
            "PLUGGED_IN": False,  # False = Off, True = On
            "ON_BATTERY": False
        }

        # Log the state file location
        self.logger.info(f"State file will be stored at: {self.state_file}")

    def _get_default_state_file(self) -> Path:
        """Get the default path for state file"""
        if os.name == 'nt':  # Windows
            # Use %APPDATA%\TurboBoostManager\
            app_data = os.environ.get('APPDATA')
            if app_data:
                config_dir = Path(app_data) / 'TurboBoostManager'
            else:
                # Fallback if APPDATA is not available
                config_dir = Path.home() / 'AppData' / 'Roaming' / 'TurboBoostManager'
        else:
            # Fallback for non-Windows systems
            config_dir = Path.cwd()

        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        return config_dir / 'turbo_boost_state.json'

    @property
    def state(self) -> dict[str, bool]:
        return self._state.copy()

    def load_state(self) -> None:
        """Load state from file"""
        self.logger.info("Loading application state...")
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                    self._state.update(loaded_state)
                    self.logger.info(f"State loaded successfully: {self._state}")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.logger.warning(f"Error loading state: {e}. Using default values.")
        else:
            self.logger.info("State file not found. Using default values.")

    def save_state(self) -> None:
        """Save state to file"""
        try:
            # Ensure parent directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2)
            self.logger.info(f"State saved: {self._state}")
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")

    def update_state(self, mode: str, value: bool) -> None:
        """Update state for specific mode"""
        if mode in self._state:
            self._state[mode] = value
            self.save_state()
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def get_mode_state(self, mode: str) -> bool:
        """Get state for specific mode"""
        return self._state.get(mode, False)