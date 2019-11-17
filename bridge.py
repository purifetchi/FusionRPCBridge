# Imports for getting the windows service shit to work.

import servicemanager, socket, sys, win32event, win32service, win32serviceutil

import cherrypy, psutil, base64, time, requests, threading
from pypresence import Presence

class RPCBridge(object):
    def pid_timer(self):
        self.PIDTimerRunning = True
        if self.PID is not None:
            exists = self.PID in [n.pid for n in psutil.process_iter()]
            if not exists:
                self.shouldNotRunPIDTimer = True

        if not self.shouldNotRunPIDTimer:
            threading.Timer(5, self.pid_timer).start()
        else: # Reset & don't run timer
            self.shouldNotRunPIDTimer = False
            self.PIDTimerRunning = False
            self.PID = None
            self.RPC.close()
            self.RPC = None # Dispose of the RPC

    def __init__(self):
        self.discordRPCID = "644703342689255466" # The ID of the application
        self.shouldNotRunPIDTimer = False
        self.PIDTimerRunning = False
        self.RPC = None
        self.PID = None
        self.lastmap = ""

        # Get all the available assets (For icon previews)
        req = requests.get("https://discordapp.com/api/oauth2/applications/" + self.discordRPCID + "/assets")
        self.artAssets = [n["name"] for n in req.json()]

    @cherrypy.expose
    def index(self):
        return "Hello from within the windows service!"

    @cherrypy.expose
    def status(self):
        return "PID: " + str(self.PID) + "<br>PIDTimerRunning: " + str(self.PIDTimerRunning)

    @cherrypy.expose
    def recv(self, gtitleint="", gtitlenam="", modeint="", modenam="", mapint="", mapnam="", state="", count=0, maxcount=0):
        if self.PID is None:
            for proc in psutil.process_iter():
                try:
                    procname = proc.name()
                    if "Sam2017" in procname:
                        self.PID = proc.pid
                        self.RPC = Presence(self.discordRPCID)
                        self.RPC.connect()
                        self.RPC.update(state="Started.", large_image="custom_map")
                        self.start_epoch = int(time.time())
                        
                        threading.Timer(5, self.pid_timer).start()
                        break
                except:
                    pass

        if self.RPC is not None:
            level       = base64.b64decode(mapint).decode('ascii').rstrip()
            level_name  = base64.b64decode(mapnam).decode('ascii').rstrip()
            gamemode    = base64.b64decode(modenam).decode('ascii').rstrip()
            gtitle_icon = base64.b64decode(gtitleint).decode('ascii').rstrip()
            gtitle_name = base64.b64decode(gtitlenam).decode('ascii').rstrip()

            large_image = level.lower() if level.lower() in self.artAssets else "custom_map"
        
            if state == "MP":
                self.RPC.update(state=gamemode, details=level_name, small_image=gtitle_icon.lower(), large_image=large_image, small_text=gtitle_name, party_size=[int(count), int(maxcount)], start=self.start_epoch)
            else:
                self.RPC.update(state=gamemode + " (Solo)", details=level_name, small_image=gtitle_icon.lower(), large_image=large_image, small_text=gtitle_name, start=self.start_epoch)

            if self.lastmap != level:
                self.lastmap = level
                self.start_epoch = int(time.time())

            return "OK"

        else:
            return "NO RPC CONNECTION"

class RPCBridgerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FusionRPCBridge"
    _svc_display_name_ = "Fusion RPC Bridge Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        cherrypy.engine.exit()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        cherrypy.config.update({'server.socket_port': 33310})
        cherrypy.quickstart(RPCBridge())

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(RPCBridgerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(RPCBridgerService)