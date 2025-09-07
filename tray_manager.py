import sys
from pathlib import Path
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem, Icon

from log import Logger
from power_manager import PowerManager
from state_manager import StateManager


class TrayManager:
    """Manages system tray icon and menu"""

    def __init__(self, state_manager: StateManager, power_manager: PowerManager):
        self.state_manager = state_manager
        self.power_manager = power_manager
        self.logger = Logger.get_logger()
        self.icon = None

    def get_resource_path(self, relative_path: str) -> Path:
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            # Running in normal Python environment
            base_path = Path(__file__).parent

        return Path(base_path) / relative_path

    def create_image(self) -> Image.Image:
        """Load tray icon image from PNG file or create fallback"""
        icon_path = self.get_resource_path('img/icon.png')

        # Try to load PNG icon
        if icon_path.exists():
            try:
                image = Image.open(icon_path)

                # Convert to RGB if needed (remove alpha channel for compatibility)
                if image.mode in ('RGBA', 'LA'):
                    # Create white background for transparency
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                    else:
                        background.paste(image)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')

                # Resize if needed (system tray icons typically 16x16 or 32x32, but PIL handles scaling)
                if image.size != (64, 64):
                    image = image.resize((64, 64), Image.Resampling.LANCZOS)

                self.logger.info(f"Successfully loaded icon from {icon_path}")
                return image

            except Exception as e:
                self.logger.warning(f"Failed to load icon from {icon_path}: {e}. Using fallback icon.")
        else:
            self.logger.info(f"Icon file not found at {icon_path}. Using fallback icon.")

        # Fallback to generated icon
        return self._create_fallback_icon()

    def _create_fallback_icon(self) -> Image.Image:
        """Create simple fallback icon"""
        image = Image.new('RGB', (64, 64), 'black')
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill='lime')
        self.logger.info("Using fallback generated icon")
        return image

    def create_menu(self) -> Menu:
        """Create context menu with current state"""
        state = self.state_manager.state
        return Menu(
            MenuItem('Plugged in', Menu(
                MenuItem('On', self._set_plugged_in_on, checked=lambda item: state["PLUGGED_IN"]),
                MenuItem('Off', self._set_plugged_in_off, checked=lambda item: not state["PLUGGED_IN"]),
            )),
            MenuItem('On battery', Menu(
                MenuItem('On', self._set_on_battery_on, checked=lambda item: state["ON_BATTERY"]),
                MenuItem('Off', self._set_on_battery_off, checked=lambda item: not state["ON_BATTERY"]),
            )),
            MenuItem('Exit', self._quit_app)
        )

    def _set_on_battery_on(self, icon, item):
        """Enable turbo mode for battery operation"""
        self.logger.info("User selected: On Battery -> On")
        self.power_manager.apply_turbo_mode("ON_BATTERY", True)
        self.state_manager.update_state("ON_BATTERY", True)
        self._update_menu()
        self.logger.info("Turbo mode enabled for battery operation")

    def _set_on_battery_off(self, icon, item):
        """Disable turbo mode for battery operation"""
        self.logger.info("User selected: On Battery -> Off")
        self.power_manager.apply_turbo_mode("ON_BATTERY", False)
        self.state_manager.update_state("ON_BATTERY", False)
        self._update_menu()
        self.logger.info("Turbo mode disabled for battery operation")

    def _set_plugged_in_on(self, icon, item):
        """Enable turbo mode for AC operation"""
        self.logger.info("User selected: Plugged In -> On")
        self.power_manager.apply_turbo_mode("PLUGGED_IN", True)
        self.state_manager.update_state("PLUGGED_IN", True)
        self._update_menu()
        self.logger.info("Turbo mode enabled for AC operation")

    def _set_plugged_in_off(self, icon, item):
        """Disable turbo mode for AC operation"""
        self.logger.info("User selected: Plugged In -> Off")
        self.power_manager.apply_turbo_mode("PLUGGED_IN", False)
        self.state_manager.update_state("PLUGGED_IN", False)
        self._update_menu()
        self.logger.info("Turbo mode disabled for AC operation")

    def _quit_app(self, icon, item):
        """Quit application"""
        self.logger.info("Application shutdown requested by user")
        icon.stop()

    def _update_menu(self):
        """Update tray menu"""
        if self.icon:
            self.icon.menu = self.create_menu()

    def create_tray_icon(self) -> Icon:
        """Create and configure tray icon"""
        self.icon = Icon(
            "PowerCfg",
            self.create_image(),
            "Turbo Boost Manager",
            self.create_menu()
        )
        return self.icon
