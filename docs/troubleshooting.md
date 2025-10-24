# Troubleshooting Guide

Common issues and solutions for Thinking Tools MCP Server.

## 🔌 Server Not Connecting

### Issue: IDE doesn't recognize the server

**Solution 1: Verify Paths**

```bash
# Check Python path
which python  # or absolute path of .venv/bin/python

# Check main.py path
ls -la main.py
pwd
```

**Solution 2: Use Absolute Paths**

❌ **Wrong** (relative path):
```json
{
  "command": "./main.py"
}
```

✅ **Correct** (absolute path):
```json
{
  "command": "/Users/username/Thinking_Tools_Local/main.py"
}
```

**Solution 3: Restart IDE Completely**

1. Close all IDE windows
2. Quit the application (not just close window)
3. Restart and wait for full initialization

### Issue: Server starts but disconnects immediately

**Check server logs:**

1. Enable debug logging in `.env`:
   ```
   MCP_LOG_LEVEL=DEBUG
   ```

2. Look for error messages in terminal/console

3. Common causes:
   - Missing dependencies
   - Python version mismatch
   - Path issues

## 📦 Import Errors

### Issue: `ModuleNotFoundError` or import errors

**Solution: Reinstall dependencies with uv**

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows

# Reinstall all dependencies
uv pip install -r requirements.txt --reinstall

# Verify installation
python -c "import fastmcp; print('Success!')"
```

**Alternative: Add PYTHONPATH to IDE config**

For Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "thinking-tools": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/main.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/Thinking_Tools_Local"
      }
    }
  }
}
```

For VSCode (`.vscode/settings.json`):
```json
{
  "mcp.servers": {
    "thinking-tools": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/main.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/Thinking_Tools_Local"
      }
    }
  }
}
```

## 🐍 Python Version Error

### Issue: "Python 3.12 or higher required"

**Check current version:**
```bash
python --version
```

**Solution: Install Python 3.12+**

**macOS (using Homebrew):**
```bash
brew install python@3.12
# or
brew install python@3.13
```

**macOS/Linux (using pyenv):**
```bash
# Install pyenv if needed
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12

# Set as local version
cd /path/to/Thinking_Tools_Local
pyenv local 3.12

# Recreate virtual environment
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Install Python 3.12 or higher
3. Recreate virtual environment with new Python version

## 🔒 Permission Errors (macOS/Linux)

### Issue: "Permission denied" when running files

**Solution: Add execute permissions**

```bash
chmod +x main.py
chmod +x setup_git.sh
chmod -R u+x .venv/bin/
```

### Issue: Cannot write to config directory

**Solution: Fix directory permissions**

```bash
# Fix config directory
mkdir -p ~/.config/claude
chmod 755 ~/.config/claude

# Fix config file
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
chmod 644 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## 🔧 Configuration Issues

### Issue: Tools not showing up in IDE

**Verify server is running:**

```bash
python main.py
```

Expected output:
```
INFO: Initializing Thinking Tools MCP Server v1.0.0
INFO: Registering Recursive Thinking tools...
INFO: Registering Sequential Thinking tools...
INFO: Registering Tree of Thoughts tools...
```

**Check IDE-specific configuration:**

**Claude Desktop:**
- Click 🔌 icon in bottom-left
- Verify "thinking-tools" server is listed
- Check for error messages

**VSCode/Cursor:**
- Open MCP panel
- Check server status
- Look for connection errors

### Issue: Some tools disabled

**Check environment configuration:**

Create or edit `.env` file:
```bash
# Enable/disable specific tools
ENABLE_RECURSIVE_THINKING_TOOLS=true
ENABLE_SEQUENTIAL_THINKING_TOOLS=true
ENABLE_TREE_OF_THOUGHTS_TOOLS=true

# Adjust log level
MCP_LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

## 🐛 Debugging Tips

### Enable verbose logging

**.env file:**
```
MCP_LOG_LEVEL=DEBUG
```

**Check logs location:**
- Claude Desktop: Check IDE console
- VSCode: Check Output panel → MCP
- Terminal: Direct stdout when running `python main.py`

### Test server independently

```bash
# Run server directly
python main.py

# Test with example input (if available)
python -c "from tools.reasoning.recursive_thinking_tool import RecursiveThinkingTool; print('OK')"
```

### Verify dependencies

```bash
# List installed packages
uv pip list

# Check for fastmcp
uv pip show fastmcp

# Reinstall if needed
uv pip install fastmcp --force-reinstall
```

## 🔄 uv-Specific Issues

### Issue: `uv` command not found

**Solution: Install uv**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Verify installation
uv --version
```

### Issue: uv fails to install packages

**Solution: Use pip as fallback**

```bash
# Activate venv
source .venv/bin/activate

# Use pip instead
pip install -r requirements.txt
```

## 🆘 Still Having Issues?

### Collect diagnostic information

```bash
# System info
uname -a  # macOS/Linux
# or: systeminfo  # Windows

# Python info
python --version
which python

# Package info
pip list

# Server test
python main.py
```

### Get help

1. **GitHub Issues**: [Report an issue](https://github.com/HHC225/Thinking_Tools_Local/issues)
   - Include diagnostic information
   - Describe steps to reproduce
   - Share error messages

2. **Check existing issues**: Someone may have solved it already

3. **Review documentation**:
   - [QUICKSTART.md](../QUICKSTART.md)
   - [README.md](../README.md)
   - Tool-specific docs in `docs/`

## 📋 Diagnostic Checklist

Before asking for help, verify:

- [ ] Python 3.12+ installed (`python --version`)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`uv pip install -r requirements.txt`)
- [ ] Server runs without errors (`python main.py`)
- [ ] Absolute paths used in IDE config
- [ ] IDE completely restarted
- [ ] Configuration file syntax is valid JSON
- [ ] Permissions correct on all files
- [ ] PYTHONPATH set if needed
- [ ] Logs reviewed for error messages

## 🔍 Common Error Messages

### "cannot import name 'FastMCP'"

**Cause**: fastmcp not installed or wrong version

**Solution**:
```bash
uv pip install fastmcp --upgrade
```

### "Address already in use"

**Cause**: Server already running

**Solution**:
```bash
# Find and kill existing process
ps aux | grep main.py
kill <process_id>
```

### "No module named 'tools'"

**Cause**: PYTHONPATH issue

**Solution**: Add PYTHONPATH to IDE config (see Import Errors section)

### "JSON decode error" in IDE config

**Cause**: Invalid JSON syntax

**Solution**: Validate JSON at [jsonlint.com](https://jsonlint.com/)

Common mistakes:
- Missing commas
- Trailing commas
- Unescaped backslashes in Windows paths
- Missing quotes around strings
