import platform
import sys

from log import Logger
from power_manager import PowerManager
from state_manager import StateManager
from tray_manager import TrayManager


class TurboBoostManager:
    """Main application controller"""

    def __init__(self):
        self.logger = Logger.get_logger()
        self.state_manager = StateManager()
        self.power_manager = PowerManager()
        self.tray_manager = TrayManager(self.state_manager, self.power_manager)

    def _check_windows_platform(self) -> bool:
        """Check if running on Windows platform"""
        current_platform = platform.system().lower()
        self.logger.debug(f"Detected platform: {current_platform}")

        if current_platform != 'windows':
            self.logger.error(f"Unsupported platform: {current_platform}")
            print("=" * 60)
            print("ERROR: This application only works on Windows")
            print("=" * 60)
            print(f"Detected platform: {platform.system()}")
            print("This application requires Windows to manage CPU power settings")
            print("using the 'powercfg' utility which is Windows-specific.")
            print("=" * 60)
            return False

        return True

    def initialize(self) -> None:
        """Initialize application state"""
        self.logger.info("Initializing Turbo Boost Manager...")

        # Load saved state
        self.state_manager.load_state()

        # Apply saved settings
        self.logger.info("Applying saved settings...")
        state = self.state_manager.state

        if state["PLUGGED_IN"]:
            self.power_manager.apply_turbo_mode("PLUGGED_IN", True)
        else:
            self.power_manager.apply_turbo_mode("PLUGGED_IN", False)

        if state["ON_BATTERY"]:
            self.power_manager.apply_turbo_mode("ON_BATTERY", True)
        else:
            self.power_manager.apply_turbo_mode("ON_BATTERY", False)

    def run(self) -> None:
        """Run the application"""
        self.logger.info("=" * 50)
        self.logger.info("Starting Turbo Boost Manager")
        self.logger.info("=" * 50)

        # Check if running on Windows
        if not self._check_windows_platform():
            self.logger.critical("Application terminated due to unsupported platform")
            sys.exit(1)

        try:
            self.initialize()

            self.logger.info("Creating system tray...")
            icon = self.tray_manager.create_tray_icon()

            self.logger.info("Turbo Boost Manager started successfully")
            icon.run()

        except Exception as e:
            self.logger.critical(f"Critical error during application startup: {e}")
            raise
        finally:
            self.logger.info("Turbo Boost Manager terminated")


if __name__ == "__main__":
    try:
        app = TurboBoostManager()
        app.run()
    except SystemExit:
        # Handle graceful exit for unsupported platforms
        pass
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
