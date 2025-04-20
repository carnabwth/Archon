import subprocess
import platform
import sys

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        if platform.system() == "Windows":
            # Windows-specific command
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                # Get the PID from the last column
                pid = result.stdout.strip().split()[-1]
                subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                print(f"Killed process {pid} using port {port}")
            else:
                print(f"No process found using port {port}")
        else:
            # Unix-like systems
            subprocess.run(
                f"lsof -ti :{port} | xargs kill -9",
                shell=True,
                check=True
            )
            print(f"Killed process using port {port}")
    except subprocess.CalledProcessError:
        # No process found using the port
        print(f"No process found using port {port}")
    except Exception as e:
        print(f"Error killing process on port {port}: {str(e)}")

if __name__ == "__main__":
    port = 8100
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    print(f"Attempting to kill process on port {port}...")
    kill_process_on_port(port)
    print("Done.") 