#!/bin/bash

# Bash Script to Set Up Python Virtual Environment and Install Dependencies

# Step 1: Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Installing Python..."
    
    # Update package lists
    sudo apt update -y

    # Install Python (Debian/Ubuntu)
    sudo apt install -y python3 python3-venv python3-pip

    # Verify Python installation
    if ! command -v python3 &> /dev/null; then
        echo "Python installation failed. Please install Python manually."
        exit 1
    fi

    echo "Python installed successfully!"
else
    echo "Python is already installed."
fi

# Step 2: Ensure pip is installed
echo "Checking if pip is installed..."
if ! command -v pip3 &> /dev/null; then
    echo "Pip is not installed. Installing pip..."
    sudo apt install -y python3-pip
fi

# Step 3: Create a Virtual Environment
echo "Setting up the virtual environment..."
python3 -m venv env

# Step 4: Activate Virtual Environment
echo "Activating the virtual environment..."
source env/bin/activate

# Step 5: Upgrade pip and install virtualenv
echo "Upgrading pip and installing virtualenv..."
pip install --upgrade pip
pip install virtualenv

# Step 6: Install Dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please create one with the necessary dependencies."
fi

echo "Python environment setup complete!"
