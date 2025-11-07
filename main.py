from Tools.tools import *

pitop = input("pitop or naw? (y/n)")
choice = input("What project u wanna run? (OBJDET/LNFOL/RC/USM)")
if choice == "OBJDET":
    if pitop == "y":
        aio.run(run_color_isos())
    else:
        aio.run(run_color_isoc())
elif choice == "LNFOL":
    print("not yet beta >:(")
elif choice == "RC":
    if pitop == "y":
        aio.run(run_remote_control_server())
    else:
        aio.run(run_remote_control_client())
elif choice == "USM":
    aio.run(run_ultrasonic())
else:
    print("nuh uh")