"""
Main entry point for MCP Project.
Runs all available servers concurrently.
"""
import os
import sys
import time
import signal
import asyncio
import multiprocessing
from typing import List, Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core import settings, logger
from app.servers import MathServer, WeatherServer

# Configure logging
log = logger.getChild("main")

# Global flag to track if servers should be running
running = True

def run_math_server():
    """Run the Math MCP Server"""
    try:
        log.info("Starting Math Server...")
        server = MathServer()
        server.run(transport="sse")
    except Exception as e:
        log.error(f"Error in Math Server: {e}")

def run_weather_server():
    """Run the Weather MCP Server"""
    try:
        log.info("Starting Weather Server...")
        server = WeatherServer()
        server.run(transport="sse")
    except Exception as e:
        log.error(f"Error in Weather Server: {e}")

def run_github_server():
    """Run the Github MCP Server"""
    try:
        log.info("Starting Github Server...")
        # server = GitHubProxyServer()
        # server.run(transport="sse")
    except Exception as e:
        log.error(f"Error in Github Server: {e}")

def sigint_handler(signum, frame):
    """Handle CTRL+C signal to gracefully shut down"""
    global running
    log.info("Received shutdown signal, stopping servers...")
    running = False

def display_startup_message(processes, github_ready=False):
    """Display a startup message with server information"""
    print("\n" + "=" * 60)
    print("MCP SERVERS RUNNING".center(60))
    print("=" * 60)
    print(f"Weather Server: http://{settings.ip_host}:{settings.weather_port}")
    print(f"Math Server:    http://{settings.ip_host}:{settings.math_port}")
    print(f"Github Server: http://{settings.ip_host}:{settings.github_port}")
    
    print("-" * 60)
    print("Running Processes:")
    for i, p in enumerate(processes, 1):
        print(f"  {i}. {p.name} (PID: {p.pid})")
    
    print("-" * 60)
    print("Press Ctrl+C to stop all servers")
    print("=" * 60)

def run_all_servers():
    """Run all available MCP servers concurrently"""
    global running
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)
    
    # Check environment
    if not settings.validate():
        log.error("Environment validation failed. Please check your .env file.")
        return 1
    
    # Start all servers in separate processes
    processes = []
    
    # Start Math Server
    math_process = multiprocessing.Process(target=run_math_server, name="Math Server")
    math_process.daemon = True
    math_process.start()
    processes.append(math_process)
    
    # Start Weather Server
    weather_process = multiprocessing.Process(target=run_weather_server, name="Weather Server")
    weather_process.daemon = True
    weather_process.start()
    processes.append(weather_process)
    
    # github_process = multiprocessing.Process(target=run_github_server, name="Github Server")
    # github_process.daemon = True
    # github_process.start()
    # processes.append(github_process)
    
    # Wait a moment for servers to start
    time.sleep(2)
    
    # Check if processes are alive
    alive_processes = [p for p in processes if p.is_alive()]
    if len(alive_processes) < len(processes):
        log.error("Some servers failed to start. Check logs for details.")
        for p in processes:
            if not p.is_alive():
                log.error(f"{p.name} failed to start.")
    
    # Display startup message
    display_startup_message(alive_processes)
    
    # Keep the main process running until interrupted
    try:
        while running and any(p.is_alive() for p in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received, shutting down...")
    finally:
        # Clean up
        log.info("Stopping all server processes...")
        for p in processes:
            if p.is_alive():
                log.info(f"Terminating {p.name} (PID: {p.pid})...")
                p.terminate()
        
        # Wait for processes to terminate
        for p in processes:
            p.join(timeout=5)
        
        # Check if any process is still alive
        for p in processes:
            if p.is_alive():
                log.warning(f"{p.name} (PID: {p.pid}) did not terminate gracefully, killing...")
                p.kill()
        
        log.info("All servers stopped.")
    
    return 0

if __name__ == "__main__":
    sys.exit(run_all_servers())