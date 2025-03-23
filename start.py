#!/usr/bin/env python3
"""
Bunkr Scraper - Main Application Launcher

This script starts both the backend API server and the frontend development server.
"""

import os
import subprocess
import threading
import time
import signal
import sys

def start_backend():
    """Start the FastAPI backend server"""
    os.chdir("backend")
    # Activate virtual environment
    if os.name == 'nt':  # Windows
        activate_cmd = os.path.join("venv", "Scripts", "activate")
    else:  # Unix/Linux
        activate_cmd = f"source {os.path.join('venv', 'bin', 'activate')}"
    
    # Start the backend server
    cmd = f"{activate_cmd} && uvicorn api:app --host 0.0.0.0 --port 8000 --reload"
    
    if os.name == 'nt':  # Windows
        process = subprocess.Popen(cmd, shell=True)
    else:  # Unix/Linux
        process = subprocess.Popen(cmd, shell=True, executable="/bin/bash")
    
    return process

def start_frontend():
    """Start the React frontend development server"""
    os.chdir("frontend")
    
    # Start the frontend server
    if os.name == 'nt':  # Windows
        process = subprocess.Popen("npm start", shell=True)
    else:  # Unix/Linux
        process = subprocess.Popen("npm start", shell=True, executable="/bin/bash")
    
    return process

def main():
    """Main function to start both servers"""
    print("Starting Bunkr Scraper Application...")
    
    # Store current directory
    root_dir = os.getcwd()
    
    # Start backend server
    print("Starting backend server...")
    backend_process = start_backend()
    
    # Return to root directory
    os.chdir(root_dir)
    
    # Wait a bit for backend to start
    time.sleep(2)
    
    # Start frontend server
    print("Starting frontend server...")
    frontend_process = start_frontend()
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\nBunkr Scraper Application is running!")
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:3000")
    print("\nPress Ctrl+C to stop the servers.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
