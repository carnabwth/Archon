import subprocess
import sys
import os
import socket
import shutil  # 🆕 Added because we now check if lsof exists

def get_available_port():
    """Get an available port for the agent service."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        if os.name == 'nt':  # Windows
            # Windows-specific command
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                pid = result.stdout.strip().split()[-1]
                subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                print(f"Killed process {pid} using port {port}")
            else:
                print(f"No process found using port {port}")
        else:
            # Unix-like systems
            if shutil.which("lsof") is not None:
                subprocess.run(
                    f"lsof -ti :{port} | xargs kill -9",
                    shell=True,
                    check=True
                )
                print(f"Killed process using port {port}")
            else:
                print("lsof not found. Skipping port cleanup.")
    except subprocess.CalledProcessError:
        print(f"No process found using port {port}")
    except Exception as e:
        print(f"Error killing process on port {port}: {str(e)}")

if __name__ == "__main__":
    # Get an available port
    port = get_available_port()
    print(f"Starting agent service with port {port}")
    
    # Kill any process that might be using this port
    kill_process_on_port(port)
    
    # Get the absolute path to the graph service script
    base



if __name__ == "__main__":
    # Get an available port
    port = get_available_port()
    print(f"Starting agent service with port {port}")
    
    # Kill any process that might be using this port
    kill_process_on_port(port)
    
    # Get the absolute path to the graph service script
    base_path = os.path.abspath(os.path.dirname(__file__))
    graph_service_path = os.path.join(base_path, 'graph_service.py')
    
    # Start the process with output redirection and port argument
    process = subprocess.Popen(
        [sys.executable, graph_service_path, "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    print(f"Agent service started with PID {process.pid}")
    print(f"Service URL: http://localhost:{port}")
    
    # Print output in real-time
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        # Print any remaining output
        for output in process.stdout.readlines():
            if output:
                print(output.strip())
                
        # Print any errors
        for error in process.stderr.readlines():
            if error:
                print(f"ERROR: {error.strip()}")
                
    except KeyboardInterrupt:
        print("Stopping agent service...")
        process.terminate()
        process.wait()
        print("Agent service stopped.") 
