from Tools.tools import *
import paramiko

def ssh_run_remote(function_name, host="100.87.152.13", username="root", password="pi-top", port=22):
    """
    SSH into a remote machine and run a Python function from Tools/tools.py
    """
    print(f"Connecting to {host}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, port=port, username=username, password=password)
        print("Connected. Running function remotely...")

        command = f'python3 -c "from repo.Tools.tools import {function_name}; import asyncio; asyncio.run({function_name}())"'
        stdin, stdout, stderr = client.exec_command(command)

        for line in stdout:
            print("REMOTE:", line.strip())
        if stderr != [] or stderr is not None:
            for line in stderr:
                print("REMOTE ERR:", line.strip())

    except Exception as e:
        print("SSH error:", e)
    finally:
        client.close()

try:
    import pitop
    pitop = "y"
    print("Pitop detected! Use this on the computer >:(")
    exit()
except ImportError:
    pitop = "n"
    print("Pitop not detected")
choice = input("What project u wanna run? (OBJDET/LNFOL/RC/USM)")
if choice == "OBJDET":
    aio.run(run_color_isoc())
    ssh_run_remote("run_color_isos")
elif choice == "LNFOL":
    print("not yet beta >:(")
elif choice == "RC":
    aio.run(run_remote_control_client())
    ssh_run_remote("run_remote_control_server")
elif choice == "USM":
    ssh_run_remote("run_ultrasonic")
else:
    print("nuh uh")