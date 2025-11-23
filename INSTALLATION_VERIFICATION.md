# Installation Verification Guide

This document provides instructions for verifying that the TrifectaOmni system is properly installed and ready to run.

## Automated Verification

The easiest way to verify your installation is to run the automated verification script:

```bash
python verify_installation.py
```

This script will check:
- ✓ Python version (3.10+)
- ✓ Required packages
- ✓ Module imports
- ✓ Directory structure
- ✓ Configuration files
- ✓ Example scripts
- ✓ Basic system functionality

### Expected Output

If everything is set up correctly, you should see:

```
✓ All checks passed!
The TrifectaOmni system is properly installed and ready to run.
```

## Manual Verification

You can also verify manually:

### 1. Check Python Version

```bash
python --version
```

Should show Python 3.10 or higher.

### 2. Check Dependencies

```bash
pip list | grep -E "numpy|pandas|scikit-learn|onnxruntime|web3"
```

All packages should be installed.

### 3. Test Import

```bash
python -c "from omni_trifecta.decision.master_governor import MasterGovernorX100; print('Import successful!')"
```

Should print "Import successful!" without errors.

### 4. Run Shadow Mode

```bash
python examples/shadow_mode_example.py
```

Should execute successfully showing trading simulation results.

## Troubleshooting

### Python Version Too Old

If your Python version is less than 3.10:

```bash
# Ubuntu/Debian
sudo apt install python3.10 python3-pip

# macOS
brew install python@3.10

# Windows
# Download from python.org
```

### Missing Packages

If packages are missing:

```bash
pip install -r requirements.txt
```

### Import Errors

If you get import errors:

1. Make sure you're in the project root directory
2. Check that all files were cloned properly:
   ```bash
   git status
   ```
3. Re-install dependencies:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

## Verification Checklist

Use this checklist to ensure everything is ready:

- [ ] Python 3.10+ installed
- [ ] All dependencies installed (pip install -r requirements.txt)
- [ ] Repository cloned completely
- [ ] verify_installation.py runs successfully
- [ ] Shadow mode example runs successfully
- [ ] Documentation reviewed (README.md, SETUP.md, QUICKSTART.md)

## Next Steps

Once verification is complete:

1. **Test the system**: Run `python examples/shadow_mode_example.py`
2. **Read the documentation**: Check SETUP.md for detailed usage
3. **Configure for live trading** (optional): Copy .env.example to .env and configure

## Support

If you encounter issues:

1. Check [STATUS.md](STATUS.md) for known issues
2. Review [SETUP.md](SETUP.md) for setup instructions
3. Run `python verify_installation.py` for diagnostic information
4. Open an issue on GitHub with the verification output

---

**Remember**: Shadow mode works without any configuration! You can test the system immediately after cloning.
