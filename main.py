from Tools.tools import *
import paramiko
import asyncio

async def ssh_run_remote(function_name, host="100.87.152.13", username="root", password="pi-top", port=22):
    """
    SSH into a remote machine, run a Python async function,
    and keep streaming output until the function ends or is interrupted.
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
        'git stash && git pull'
        'PYTHONPATH=/root/repo python3 -u -c '
        f'"from Tools.tools import {function_name}; '
        'import asyncio; '
        f'asyncio.run({function_name}())"'
    )

    transport = client.get_transport()
    if not transport:
        print("[SSH] No transport available!")
        return

    channel = transport.open_session()
    channel.exec_command(command)
    print("[SSH] Remote function started. Streaming output...\n")

    try:
        while True:
            if channel.recv_ready():
                out = channel.recv(4096).decode(errors="ignore")
                if out.strip():
                    print("[REMOTE]", out.strip())

            if channel.recv_stderr_ready():
                err = channel.recv_stderr(4096).decode(errors="ignore")
                if err.strip():
                    print("[REMOTE ERR]", err.strip())

            if channel.exit_status_ready():
                print("[SSH] Remote process exited.")
                break

            await asyncio.sleep(0.2)

    except KeyboardInterrupt:
        print("[SSH] Interrupted by user. Closing connection...")

    finally:
        channel.close()
        client.close()
        print("[SSH] Session closed.")


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
                run_color_isoc(),
                ssh_run_remote("run_color_isos")
            )

        elif choice == "RC":
            print("[MAIN] Starting Remote Control system...")
            await asyncio.gather(
                run_remote_control_client(),
                ssh_run_remote("run_remote_control_server")
            )

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
