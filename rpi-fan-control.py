#!/usr/bin/env python3
import time
import os
import signal
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RPiFanController:
    def __init__(self, fan_pin=14, temp_on=65, temp_off=55, check_interval=10):
        self.fan_pin = fan_pin
        self.temp_on = temp_on  # Temperature to turn fan ON (Celsius)
        self.temp_off = temp_off  # Temperature to turn fan OFF (Celsius)
        self.check_interval = check_interval  # Check interval in seconds
        self.fan_running = False
        self.running = True
        
        # Setup GPIO
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.fan_pin, GPIO.OUT)
            GPIO.output(self.fan_pin, GPIO.LOW)  # Start with fan off
            logger.info(f"Fan controller initialized on GPIO pin {self.fan_pin}")
        except ImportError:
            logger.error("RPi.GPIO not available, using mock mode")
            self.GPIO = None
    
    def get_cpu_temp(self):
        """Get CPU temperature in Celsius"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_millicelsius = int(f.read().strip())
                return temp_millicelsius / 1000.0
        except:
            logger.error("Could not read CPU temperature")
            return 50.0  # Default safe temperature
    
    def set_fan(self, state):
        """Set fan state (True = ON, False = OFF)"""
        if self.GPIO:
            self.GPIO.output(self.fan_pin, self.GPIO.HIGH if state else self.GPIO.LOW)
        
        if state != self.fan_running:
            self.fan_running = state
            status = "ON" if state else "OFF"
            logger.info(f"Fan turned {status}")
    
    def cleanup(self, signum=None, frame=None):
        """Cleanup GPIO and exit"""
        logger.info("Shutting down fan controller...")
        self.running = False
        if self.GPIO:
            self.GPIO.cleanup()
        sys.exit(0)
    
    def run(self):
        """Main control loop"""
        signal.signal(signal.SIGTERM, self.cleanup)
        signal.signal(signal.SIGINT, self.cleanup)
        
        logger.info(f"Starting fan controller - ON: {self.temp_on}°C, OFF: {self.temp_off}°C")
        
        while self.running:
            try:
                current_temp = self.get_cpu_temp()
                
                if current_temp >= self.temp_on and not self.fan_running:
                    self.set_fan(True)
                elif current_temp <= self.temp_off and self.fan_running:
                    self.set_fan(False)
                
                logger.debug(f"CPU: {current_temp:.1f}°C, Fan: {'ON' if self.fan_running else 'OFF'}")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(self.check_interval)
        
        self.cleanup()

if __name__ == "__main__":
    controller = RPiFanController()
    controller.run()
