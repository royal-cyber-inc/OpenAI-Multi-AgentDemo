## OpenAI Multi-Agent Demo

This demo demonstrates **OpenAI Multi-Agent capabilities** with **guardrails, handoffs, and tool integrations**.

------

### **Prerequisites**

Before running the demo, ensure you have:

- **Python 3.10+** installed
- **pip** (Python package manager)
- **A valid OpenAI API key**

------

### **Windows Setup**

### **1. Install Python & Virtual Environment**

1. Open **PowerShell** as Administrator.

2. Run the setup script to install Python (if missing) and set up the virtual environment:

   ```powershell
   .\setup_env.ps1
   ```

------

### 2. **Set OpenAI API Key**

1. **Option 1: Use a `.env` file (Recommended)**

   - Create a file named `.env` in the project directory.

   - Add the following line:

     ```powershell
     OPENAI_API_KEY=your_openai_api_key_here
     ```

   - The script will automatically load this API key.

2. **Option 2: Set Environment Variable Permanently**

   ```powershell
   [System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_openai_api_key_here", "User")
   ```

   **Restart PowerShell** to apply changes.

3. **Option 3: Temporary Session Variable**

   ```powershell
   $env:OPENAI_API_KEY="your_openai_api_key_here"
   ```

------

### 3. **Run the Demo**

```
powershell


CopyEdit
python main.py
```

The multi-agent system is now running!

------

## **Linux/macOS Setup**

### **1. Install Python & Virtual Environment**

1. Open 

   Terminal

    and run the setup script:

   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

------

### **2. Set OpenAI API Key**

1. **Option 1: Use a `.env` file (Recommended)**

   ```bash
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

2. **Option 2: Temporary Session Variable**

   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

------

### **3. Run the Demo**

```bash
python main.py
```

The multi-agent system is now running!

------

## **Troubleshooting**

### **Python Version is Incorrect**

Run:

```powershell
python --version
```

If it’s **lower than 3.10**, reinstall Python.

------

### **OpenAI API Key Not Found**

1. Verify 

   ```
   echo $env:OPENAI_API_KEY  # Windows
   echo $OPENAI_API_KEY      # Linux/macOS
   ```

2. Restart terminal and try again.



------

## **Features in This Demo**

- Multi-Agent System
-  Guardrails to Filter Requests**
- Handoff Mechanism
-  Tool Integrations (Weather API, Web Search)