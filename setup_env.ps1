# PowerShell Script to Set Up Python Virtual Environment and Install Dependencies

# Step 1: Check if Python is installed
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed. Installing Python..."
    
    # Download Python installer
    $pythonInstallerUrl = "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
    $installerPath = "$env:TEMP\python_installer.exe"

    Write-Host "Downloading Python installer..."
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath

    # Install Python silently
    Write-Host "Installing Python..."
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

    # Remove installer
    Remove-Item -Path $installerPath -Force

    # Refresh environment variables to recognize Python immediately
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    
    # Verify Python installation
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "Python installation failed. Please install Python manually."
        exit 1
    }

    Write-Host "Python installed successfully!"
}

# Step 2: Ensure pip is installed
Write-Host "Checking if pip is installed..."
$pipCheck = python -m ensurepip --default-pip
if ($pipCheck -match "was not found") {
    Write-Host "Pip is not installed. Installing pip..."
    python -m ensurepip --default-pip
}

# Step 3: Create a Virtual Environment
Write-Host "Setting up the virtual environment..."
python -m venv env

# Step 4: Activate Virtual Environment
Write-Host "Activating the virtual environment..."
Set-ExecutionPolicy Unrestricted -Scope Process -Force  # Enable script execution if needed
. .\env\Scripts\Activate

# Step 5: Upgrade pip and install virtualenv
Write-Host "Upgrading pip and installing virtualenv..."
python -m pip install --upgrade pip
python -m pip install virtualenv

# Step 6: Install Dependencies from requirements.txt
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
}
else {
    Write-Host "requirements.txt not found. Please create one with the necessary dependencies."
}

Write-Host "Python environment setup complete!"
