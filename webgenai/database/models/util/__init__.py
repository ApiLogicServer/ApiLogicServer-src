import psutil

def kill_processes_by_port(port: int) -> None:
    """
    Kill processes using the specified port
    """
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port == port:
                    psutil.Process(proc.info['pid']).terminate()
                    print(f"Terminated process with PID {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass