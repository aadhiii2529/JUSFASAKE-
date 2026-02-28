#!/bin/bash

echo "🚀 Setting up Construction Alert System..."

# Update system
sudo apt-get update

# Install Python and Pip if not present
sudo apt-get install -y python3 python3-pip libgeos-dev libgl1-mesa-glx libglib2.0-0

# Install Python requirements
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create a systemd service (Optional but recommended for deployment)
cat <<EOF | sudo tee /etc/systemd/system/construction-alert.service
[Unit]
Description=Construction Alert System Web Dashboard
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Setup complete!"
echo "To start the system, run: python3 main.py"
echo "To install as a background service, run: sudo systemctl enable --now construction-alert"
