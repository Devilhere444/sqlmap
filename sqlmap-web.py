#!/usr/bin/env python

"""
SQLMap Web Interface - Modern Web-Based SQL Injection Testing Platform
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org)
See the file 'LICENSE' for copying permission
"""

import os
import sys

# Ensure the lib path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Web-only entry point for SQLMap
    """
    try:
        from lib.core.common import setPaths
        from lib.core.data import paths
        from lib.core.webui import runWebUI
        from lib.core.settings import VERSION_STRING
        from lib.core.common import dataToStdout
        
        # Set paths
        setPaths(os.path.dirname(os.path.abspath(__file__)))
        
        # Default web UI settings
        port = 8080
        host = '127.0.0.1'
        
        # Parse simple command line arguments
        if len(sys.argv) > 1:
            for i, arg in enumerate(sys.argv[1:], 1):
                if arg.startswith('--port='):
                    try:
                        port = int(arg.split('=')[1])
                    except ValueError:
                        pass
                elif arg.startswith('--host='):
                    host = arg.split('=')[1]
                elif arg == '--port' and i + 1 < len(sys.argv):
                    try:
                        port = int(sys.argv[i + 1])
                    except ValueError:
                        pass
                elif arg == '--host' and i + 1 < len(sys.argv):
                    host = sys.argv[i + 1]
                elif arg in ('--help', '-h'):
                    print(f"""
SQLMap Web Interface {VERSION_STRING}
Advanced SQL Injection Testing Platform

Usage: python sqlmap-web.py [options]

Options:
  --host HOST     Host to bind the web server (default: 127.0.0.1)
  --port PORT     Port to bind the web server (default: 8080)
  --help, -h      Show this help message

Examples:
  python sqlmap-web.py
  python sqlmap-web.py --host 0.0.0.0 --port 9000
  python sqlmap-web.py --port=8888

Web Interface Features:
🎯 Modern responsive web interface
⚡ Real-time attack progress visualization  
📊 Interactive result presentation
🎨 Animated progress indicators
📱 Mobile-compatible design
🔧 Drag-and-drop configuration
🚀 Advanced graphical features

Open your browser to http://{host}:{port} after starting.
""")
                    return
        
        # Welcome message
        dataToStdout(f"""
╔══════════════════════════════════════════════════════════════╗
║                   SQLMap Web Interface                      ║
║              Advanced SQL Injection Platform                ║
║                      {VERSION_STRING}                       ║
╚══════════════════════════════════════════════════════════════╝

🌐 Starting modern web-based interface...
🎯 Complete graphical SQL injection testing platform
⚡ Real-time progress tracking and visualization
📊 Interactive results with advanced animations

""", forceOutput=True)
        
        # Start web UI
        runWebUI(port=port, host=host)
        
    except KeyboardInterrupt:
        dataToStdout("\n[!] User interrupted web interface\n", forceOutput=True)
    except Exception as ex:
        dataToStdout(f"\n[!] Error starting web interface: {ex}\n", forceOutput=True)
        sys.exit(1)

if __name__ == "__main__":
    main()