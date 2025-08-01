# Raspberry Pi 4B Fan Control Setup

## Overview

This document describes the automatic fan control system configured for your Raspberry Pi 4B running Ubuntu Server 25. The system monitors CPU temperature and automatically controls the fan to keep your Pi cool and prevent thermal throttling.

## System Information

- **Device**: Raspberry Pi 4 Model B Rev 1.5
- **OS**: Ubuntu Server 25 (aarch64)
- **CPU**: Cortex-A72
- **Fan GPIO Pin**: 14 (standard RPi 4B fan connector)

## What's Configured

### 1. Hardware Fan Control (Boot Configuration)

**File**: `/boot/firmware/config.txt`

Added GPIO fan overlay that provides hardware-level fan control:
```
# Fan control settings
dtoverlay=gpio-fan,gpiopin=14,temp=65000
# Alternative: dtoverlay=gpio-fan,gpiopin=14,temp=60000,hyst=5000
```

- **GPIO Pin**: 14 (connects to official RPi fan)
- **Turn ON Temperature**: 65°C (65000 millicelsius)
- **Backup Available**: `/boot/firmware/config.txt.backup`

### 2. Software Fan Control Service

**Script**: `/usr/local/bin/rpi-fan-control.py`
**Service**: `rpi-fan-control.service`

Advanced Python-based fan controller with the following features:

#### Temperature Thresholds
- **Fan ON**: 65°C
- **Fan OFF**: 55°C
- **Check Interval**: 10 seconds
- **Hysteresis**: 10°C (prevents rapid on/off cycling)

#### Service Features
- Automatic startup on boot
- Automatic restart on failure
- Logging to systemd journal
- Graceful shutdown handling

### 3. Temperature Monitoring

**Script**: `/usr/local/bin/rpi-temp-monitor`

Convenience script that displays:
- Current CPU temperature (°C and °F)
- Fan control service status
- Recent fan activity logs
- GPIO pin status (when accessible)

## Usage Commands

### Check Temperature and Fan Status
```bash
rpi-temp-monitor
```

### View Fan Control Logs
```bash
# View recent logs
sudo journalctl -u rpi-fan-control.service -n 20

# Follow logs in real-time
sudo journalctl -u rpi-fan-control.service -f
```

### Service Management
```bash
# Check service status
sudo systemctl status rpi-fan-control.service

# Start/stop/restart service
sudo systemctl start rpi-fan-control.service
sudo systemctl stop rpi-fan-control.service
sudo systemctl restart rpi-fan-control.service

# Enable/disable automatic startup
sudo systemctl enable rpi-fan-control.service
sudo systemctl disable rpi-fan-control.service
```

### Manual Temperature Check
```bash
# Raw temperature in millicelsius
cat /sys/class/thermal/thermal_zone0/temp

# Convert to Celsius
echo "scale=2; $(cat /sys/class/thermal/thermal_zone0/temp) / 1000" | bc
```

## Temperature Ranges

| Temperature | Status | Action |
|-------------|---------|---------|
| < 55°C | Cool | Fan OFF |
| 55-64°C | Normal | Fan OFF (if previously ON, stays ON until ≤55°C) |
| ≥ 65°C | Warm | Fan ON |
| ≥ 80°C | Hot | Hardware throttling may occur |

## Customization

### Changing Temperature Thresholds

Edit the fan control script:
```bash
sudo nano /usr/local/bin/rpi-fan-control.py
```

Modify these values in the `RPiFanController` initialization:
```python
controller = RPiFanController(
    fan_pin=14,        # GPIO pin
    temp_on=65,        # Temperature to turn fan ON
    temp_off=55,       # Temperature to turn fan OFF
    check_interval=10  # Check every N seconds
)
```

After changes, restart the service:
```bash
sudo systemctl restart rpi-fan-control.service
```

### Boot Configuration Alternative

For different thresholds in hardware control, edit `/boot/firmware/config.txt`:
```bash
sudo nano /boot/firmware/config.txt
```

Examples:
```
# More aggressive cooling (60°C on, 55°C off)
dtoverlay=gpio-fan,gpiopin=14,temp=60000,hyst=5000

# Conservative cooling (70°C on)
dtoverlay=gpio-fan,gpiopin=14,temp=70000
```

**Important**: Reboot required for boot configuration changes.

## Files Created/Modified

### Created Files
- `/usr/local/bin/rpi-fan-control.py` - Fan control script
- `/usr/local/bin/rpi-temp-monitor` - Temperature monitoring script
- `/etc/systemd/system/rpi-fan-control.service` - Systemd service file
- `/boot/firmware/config.txt.backup` - Backup of original boot config

### Modified Files
- `/boot/firmware/config.txt` - Added fan control overlay

## Troubleshooting

### Fan Not Starting
1. Check current temperature: `rpi-temp-monitor`
2. Verify service is running: `sudo systemctl status rpi-fan-control.service`
3. Check for errors: `sudo journalctl -u rpi-fan-control.service -n 20`
4. Ensure hardware connection to GPIO pin 14

### Service Not Starting
1. Check script permissions: `ls -la /usr/local/bin/rpi-fan-control.py`
2. Test script manually: `sudo /usr/local/bin/rpi-fan-control.py`
3. Check for GPIO conflicts: `dmesg | grep -i gpio`

### Hardware Issues
1. Verify fan is connected to GPIO 14 and ground
2. Check for loose connections
3. Test with multimeter if available
4. Reboot to ensure boot configuration is loaded

## Safety Notes

- The Pi will start thermal throttling around 80°C to protect itself
- Fan activation at 65°C provides a safety margin
- Hardware overlay provides backup control even if software fails
- Both systems work independently for redundancy

## Maintenance

### Regular Checks
- Monitor temperatures periodically: `rpi-temp-monitor`
- Check service logs monthly: `sudo journalctl -u rpi-fan-control.service --since "1 month ago"`
- Clean fan and heatsink every 3-6 months

### Updates
If you modify the fan control script, remember to:
1. Test changes manually first
2. Restart the service: `sudo systemctl restart rpi-fan-control.service`
3. Monitor logs for any errors

---

**Setup Date**: August 1, 2025  
**System**: Ubuntu Server 25 on Raspberry Pi 4B  
**Status**: ✅ Active and Monitoring
