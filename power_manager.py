import subprocess

from log import Logger


class PowerManager:
    """Manages CPU power settings via powercfg"""

    MODE_MAP = {
        "PLUGGED_IN": "/setacvalueindex",
        "ON_BATTERY": "/setdcvalueindex",
    }

    def __init__(self):
        self.logger = Logger.get_logger()

    def set_cpu_power(self, max_p: int, mode: str) -> None:
        """Set CPU power percentage for specific mode"""
        try:
            self.logger.info(f"Setting CPU power: {max_p}% for mode {mode}")

            # Get active power scheme GUID
            output = subprocess.check_output(
                ['powercfg', '/getactivescheme'],
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=False
            )
            guid = output.split(':')[1].strip().split(' ')[0]
            self.logger.debug(f"Active power scheme: {guid}")

            # Set processor throttle maximum
            cmd1 = ['powercfg', self.MODE_MAP.get(mode), guid, 'SUB_PROCESSOR', 'PROCTHROTTLEMAX', str(max_p)]
            self.logger.debug(f"Executing command: {' '.join(cmd1)}")
            subprocess.run(cmd1, check=True, creationflags=subprocess.CREATE_NO_WINDOW, shell=False)

            # Activate the scheme
            cmd2 = ['powercfg', '/setactive', guid]
            self.logger.debug(f"Executing command: {' '.join(cmd2)}")
            subprocess.run(cmd2, check=True, creationflags=subprocess.CREATE_NO_WINDOW, shell=False)

            self.logger.info(f"CPU power successfully set to {max_p}% for mode {mode}")

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error executing powercfg command: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error setting CPU power: {e}")
            raise

    def apply_turbo_mode(self, mode: str, enabled: bool) -> None:
        """Apply turbo mode setting"""
        power_percentage = 100 if enabled else 99
        self.set_cpu_power(power_percentage, mode)