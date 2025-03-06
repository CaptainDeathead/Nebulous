#!/bin/bash

if [ "$EUID" -eq 0 ]; then
    echo "Please run as a normal user, not root."
    exit 1
fi

echo "Installing required packages..."
sudo apt update && sudo apt install -y xserver-xorg xinit x11-xserver-utils

echo "Creating ~/.xinitrc..."
cat <<EOF > ~/.xinitrc
#!/bin/sh
xset -dpms  # Disable power management
xset s off  # Disable screen blanking
xset s noblank
exec /usr/bin/python3 /home/pi/your_script.py
EOF
chmod +x ~/.xinitrc

echo "Modifying ~/.bash_profile to start X server on boot..."
if ! grep -q "startx" ~/.bash_profile; then
    echo -e "\nif [ -z \"\$DISPLAY\" ] && [ \"\$(tty)\" = \"/dev/tty1\" ]; then\n    startx\nfi" >> ~/.bash_profile
fi

echo "Enabling console autologin for user..." # this means no password is required, so it goes straight into console, where x server is created
sudo raspi-config nonint do_boot_behaviour B2

echo "Setup complete! Rebooting now..."
sudo reboot