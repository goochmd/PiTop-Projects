from Tools.tools import *
import paramiko
import asyncio

ip = input("Enter the IP address of the remote Pi-Top (default: 100.87.152.13): ") or "100.87.152.13"

async def ssh_run_remote(function_name, host=ip, username="root", password="pi-top", port=22):
    """
    SSH into a remote machine and run a persistent Python process.
    Keeps reading output until closed.
    """
    print(f"[SSH] Connecting to {host}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, port=port, username=username, password=password)
    except Exception as e:
        print(f"[SSH] Connection failed: {e}")
        return

    print(f"[SSH] Connected. Launching {function_name}() remotely...")

    command = (
        'cd /root/repo && '
        'PYTHONPATH=/root/repo nohup python3 -u -c '
        f'"from Tools.tools import {function_name}; import asyncio; asyncio.run({function_name}())" '
        '> /root/repo/ssh_log.txt 2>&1 &'
    )

    stdin, stdout, stderr = client.exec_command(command)
    print("[SSH] Remote command started in background.")
    await asyncio.sleep(2)  # let it boot
    client.close()


async def main():
    try:
        import pitop
        print("Pitop detected! Use this on the computer >:(")
        return
    except ImportError:
        print("Pitop not detected")

    choice = input("What project u wanna run? (OBJDET/LNFOL/RC/USM) ").strip().upper()

    try:
        if choice == "OBJDET":
            print("[MAIN] Starting Object Detection locally + remotely...")
            await asyncio.gather(
                run_color_isoc(),               # local computer (controller)
                ssh_run_remote("run_color_isos")  # remote Pi-Top (server)
            )

        elif choice == "RC":
            print("[MAIN] Starting Remote Control system...")
            await ssh_run_remote("run_remote_control_server")  # runs on Pi-Top
            await run_remote_control_client()                  # runs locally

        elif choice == "USM":
            print("[MAIN] Starting Ultrasonic remotely...")
            await ssh_run_remote("run_ultrasonic")

        elif choice == "LNFOL":
            print("not yet beta >:(")
        else:
            print("nuh uh")

    except Exception as e:
        print(f"[ERROR] Main loop crashed: {e}")

    finally:
        input("Press Enter to exit...")


if __name__ == "__main__":
    asyncio.run(main())
