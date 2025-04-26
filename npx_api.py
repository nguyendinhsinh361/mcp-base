from fastapi import FastAPI, HTTPException, BackgroundTasks, Body, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import subprocess
import shlex
import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Union, Any
import json
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("npx-api")

# Initialize FastAPI app
app = FastAPI(
    title="NPX Runner API",
    description="API for running NPX commands in the host environment",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with appropriate origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for active processes
active_processes: Dict[str, subprocess.Popen] = {}

class NPXCommandRequest(BaseModel):
    """Request model for running an NPX command"""
    command: str = Field(..., description="The NPX command to run")
    args: str = Field("", description="Arguments for the NPX command as a single string")
    env_vars: Dict[str, str] = Field(default_factory=dict, description="Environment variables to set")
    working_dir: Optional[str] = Field(None, description="Working directory for the command")
    stream_output: bool = Field(False, description="Whether to stream output")

class ProcessInfo(BaseModel):
    """Response model for process information"""
    process_id: str
    command: str
    args: str
    status: str
    start_time: str
    pid: int

async def run_command(command: str, args: str, env_vars: Dict[str, str], 
                      working_dir: Optional[str], process_id: str):
    """Run an NPX command and store the process"""
    try:
        # Prepare environment
        env = os.environ.copy()
        env.update(env_vars)
        
        # Prepare full command as a string
        full_command_str = f"npx -y {command} {args}"
        
        logger.info(f"Starting process {process_id}: {full_command_str}")
        
        # Start the process using shell=True to handle the string command
        process = subprocess.Popen(
            full_command_str,
            cwd=working_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=True
        )
        logger.info(process)
        
        # Store the process
        active_processes[process_id] = process
        
        return process
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        if process_id in active_processes:
            del active_processes[process_id]
        raise

async def stream_process_output(process: subprocess.Popen):
    """Stream output from a process"""
    async def output_generator():
        while True:
            # Check if process has finished
            if process.poll() is not None:
                # Process has terminated, yield remaining output
                stdout_line = process.stdout.readline()
                if stdout_line:
                    yield f"data: {json.dumps({'type': 'stdout', 'data': stdout_line.strip()})}\n\n"
                
                stderr_line = process.stderr.readline()
                if stderr_line:
                    yield f"data: {json.dumps({'type': 'stderr', 'data': stderr_line.strip()})}\n\n"
                
                # Yield exit code
                yield f"data: {json.dumps({'type': 'exit', 'code': process.returncode})}\n\n"
                break
            
            # Read stdout
            stdout_line = process.stdout.readline()
            if stdout_line:
                yield f"data: {json.dumps({'type': 'stdout', 'data': stdout_line.strip()})}\n\n"
            
            # Read stderr
            stderr_line = process.stderr.readline()
            if stderr_line:
                yield f"data: {json.dumps({'type': 'stderr', 'data': stderr_line.strip()})}\n\n"
            
            # Sleep briefly to avoid high CPU usage
            await asyncio.sleep(0.1)
    
    return StreamingResponse(
        output_generator(),
        media_type="text/event-stream"
    )

@app.post("/api/npx", status_code=status.HTTP_201_CREATED, response_model=ProcessInfo)
async def run_npx_command(
    request: NPXCommandRequest,
    background_tasks: BackgroundTasks
):
    """Run an NPX command and return the process ID"""
    # Generate a unique ID for this process
    process_id = str(uuid.uuid4())
    
    try:
        # Run the command
        process = await run_command(
            request.command,
            request.args,
            request.env_vars,
            request.working_dir,
            process_id
        )
        
        # Return process info
        return ProcessInfo(
            process_id=process_id,
            command=request.command,
            args=request.args,
            status="running",
            start_time=datetime.now().isoformat(),
            pid=process.pid
        )
    except Exception as e:
        logger.error(f"Failed to run NPX command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run NPX command: {str(e)}"
        )

@app.get("/api/npx/{process_id}/stream", response_class=StreamingResponse)
async def stream_process(process_id: str):
    """Stream output from a running process"""
    if process_id not in active_processes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with ID {process_id} not found"
        )
    
    process = active_processes[process_id]
    return await stream_process_output(process)

@app.get("/api/npx", response_model=List[ProcessInfo])
async def list_processes():
    """List all active processes"""
    result = []
    for pid, proc in active_processes.items():
        # Clean up dead processes
        if proc.poll() is not None and proc.returncode != 0:
            logger.info(f"Removing terminated process {pid} with return code {proc.returncode}")
            # Keep it for now so we can report its status
        
        result.append(
            ProcessInfo(
                process_id=pid,
                command="npx",  # We don't store the original command
                args="",        # We don't store the original args
                status="running" if proc.poll() is None else f"terminated (code: {proc.returncode})",
                start_time=datetime.now().isoformat(),  # We don't track the real start time
                pid=proc.pid
            )
        )
    
    return result

@app.delete("/api/npx/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_process(process_id: str):
    """Terminate a running process"""
    if process_id not in active_processes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with ID {process_id} not found"
        )
    
    process = active_processes[process_id]
    
    # Check if process is still running
    if process.poll() is None:
        try:
            # Try to terminate gracefully first
            process.terminate()
            
            # Wait briefly for process to terminate
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                process.kill()
                process.wait(timeout=5)
        except Exception as e:
            logger.error(f"Error terminating process {process_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error terminating process: {str(e)}"
            )
    
    # Remove from active processes
    del active_processes[process_id]
    
    return None

@app.get("/api/npx/{process_id}", response_model=Dict[str, Any])
async def get_process_info(process_id: str):
    """Get detailed information about a process"""
    if process_id not in active_processes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with ID {process_id} not found"
        )
    
    process = active_processes[process_id]
    
    # Check process status
    return_code = process.poll()
    status = "running" if return_code is None else f"terminated (code: {return_code})"
    
    # Get process output if it has terminated
    stdout, stderr = "", ""
    if return_code is not None:
        try:
            stdout_data, stderr_data = process.communicate(timeout=1)
            stdout = stdout_data if stdout_data else ""
            stderr = stderr_data if stderr_data else ""
        except subprocess.TimeoutExpired:
            # Process is still producing output
            pass
    
    # Return process info
    return {
        "process_id": process_id,
        "status": status,
        "return_code": return_code,
        "pid": process.pid,
        "stdout": stdout,
        "stderr": stderr
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)