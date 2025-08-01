#!/bin/bash

echo "Testing GPIO pins for fan control..."
echo "Current temperature: $(echo "scale=1; $(cat /sys/class/thermal/thermal_zone0/temp)/1000" | bc)°C"
echo ""

# Common fan GPIO pins on the 40-pin header
pins=(14 15 18 23 24 25 8 7 12 16 20 21)

for pin in "${pins[@]}"; do
    echo "Testing GPIO $pin..."
    
    # Export the pin if not already exported
    if [ ! -d "/sys/class/gpio/gpio$pin" ]; then
        echo $pin | sudo tee /sys/class/gpio/export > /dev/null 2>&1
        sleep 0.1
    fi
    
    # Set as output
    echo "out" | sudo tee /sys/class/gpio/gpio$pin/direction > /dev/null 2>&1
    
    # Turn on
    echo "1" | sudo tee /sys/class/gpio/gpio$pin/value > /dev/null 2>&1
    echo "  GPIO$pin set to HIGH - Listen for fan (3 seconds)..."
    sleep 3
    
    # Turn off
    echo "0" | sudo tee /sys/class/gpio/gpio$pin/value > /dev/null 2>&1
    echo "  GPIO$pin set to LOW"
    
    # Ask user
    echo -n "Did the fan turn on/off? (y/n): "
    read response
    
    case $response in
        [Yy]* ) 
            echo "*** Fan found on GPIO $pin! ***"
            echo $pin > /tmp/fan_gpio_pin
            # Cleanup before exit
            echo $pin | sudo tee /sys/class/gpio/unexport > /dev/null 2>&1
            exit 0
            ;;
        [Nn]* ) 
            echo "  Not GPIO $pin"
            ;;
    esac
    
    # Cleanup
    echo $pin | sudo tee /sys/class/gpio/unexport > /dev/null 2>&1
    echo ""
done

echo "Fan GPIO pin not found. Please check your wiring."
