# FusionRPCBridge
This script bridges the connection between the Discord Rich Presence mod for Fusion and Discord itself. There was sadly no better way of doing it.
It uses **cherrypy** to handle the HTTP server and **pywin32** to host itself as a windows service. Versions for Linux and Mac will be released soon, though you can get it easily working just by removing the windows service initializer class from the script.

After launching the service, it spawns an HTTP server listening on localhost:33310.

# Usage
**INSTALLATION GUIDE:**
1. Download the prepackaged binary ( or install python and launch the script yourself ) from the repository here: https://github.com/naomiEve/FusionRPCBridge/releases.
2. Save it into a place where you won't remove it from.
3. Open the command prompt (cmd.exe) as an administrator.
4. Navigate to the folder where you've saved the binary file.
5. Run *bridge.exe --startup auto install* to install the service. (You can also do *--startup manual*, if you don't want the service to start automatically)
6. After installing, type "sc start FusionRPCBridge" to start the service.

**HOW TO UNINSTALL THE BRIDGE:**
1. Open the command prompt (cmd.exe) as an administrator.
2. Navigate to the folder where you've saved the binary file.
3. Run *sc stop FusionRPCBridge*.
4. After stopping the service, run *bridge.exe remove* to uninstall the service.

# Requirements (If you want to run the script using python yourself)
**cherrypy**, **pywin32**, **psutil**, **pypresence**, **requests**