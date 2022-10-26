from concurrent.futures import thread
import threading
from tkinter import *
from tkinter import messagebox
import pyprofibus

profibus_on = False

stop = False
t1 : thread
    
def run():
    global comm, stop
    watchdog=None
    master = None
    try:
        config = pyprofibus.PbConf.fromFile("C:\profibus\pyprofibus-master\pyprofibus-master\examples/example_dummy_inputonly.conf")
        master = config.makeDPM()
        outData = {}        
        for slaveConf in config.slaveConfs:
            slaveDesc = slaveConf.makeDpSlaveDesc()			
            dp1PrmMask = bytearray((pyprofibus.dp.DpTelegram_SetPrm_Req.DPV1PRM0_FAILSAFE,
						pyprofibus.dp.DpTelegram_SetPrm_Req.DPV1PRM1_REDCFG,
						0x00))
            dp1PrmSet  = bytearray((pyprofibus.dp.DpTelegram_SetPrm_Req.DPV1PRM0_FAILSAFE,
						pyprofibus.dp.DpTelegram_SetPrm_Req.DPV1PRM1_REDCFG,
						0x00))
            slaveDesc.setUserPrmData(slaveConf.gsd.getUserPrmData(dp1PrmMask=dp1PrmMask,
									      dp1PrmSet=dp1PrmSet))
            master.addSlave(slaveDesc)
			# Set initial output data.
            outData[slaveDesc.name] = bytearray((0x40, 0x24))
            slaveDesc.setSyncMode(True)
            slaveDesc.__repr__()
            slaveDesc.setGroupMask(1)
            slaveDesc.setWatchdog(300)
		# Initialize the DPM
        master.initialize()
        # Run the slave state machine.
        while True:
            if stop:
                break
			# Write the output data.
            for slaveDesc in master.getSlaveList():
                slaveDesc.setMasterOutData(outData[slaveDesc.name])	
            # Run slave state machines.
            handledSlaveDesc = master.run()
			# Get the in-data (receive)
            if handledSlaveDesc:
                inData = handledSlaveDesc.getMasterInData()
				#print(handledSlaveDesc.isConnected())
				#print (slaveDesc)
				#print(slaveDesc.name)
				# This slave will not send any data. It's input-only (see config).
                assert inData is None
			# Feed the system watchdog, if it is available.
            #print(handledSlaveDesc.isConnecting())
            #print(handledSlaveDesc.isConnected())
            #if watchdog is not None:
            #    watchdog()
			# Slow down main loop. Just for debugging.
            #time.sleep(0.01)
            #print(slaveDesc.__repr__())
        
        #await asyncio.sleep(1)
       
    except pyprofibus.ProfibusError as e:
        messagebox.showinfo(message='Stopped Profibus communication' + str(e))
        return 1
    finally:
        if master:
            master.destroy()
    return 0    

def stop_profibus():
    global stop, t1, profibus_on
    if not profibus_on:
        return
    profibus_on = False
    stop = True
    t1.join()
    
def start_profibus():
    global stop, t1, profibus_on
    if profibus_on:
        return
    profibus_on = True
    stop = False
    t1 = threading.Thread(target = run)
    t1.start()
    
def main():
    global t1,stop
    root = Tk()
    def close():
        global stop, t1   
        stop = True
        t1.join()
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    root.title('Profibus DP controller')    
    Button(master=root, text='Start Profibus',fg='black', bg='blue', command = lambda: start_profibus()).pack()
    Button(master=root, text='Stop Profibus', fg='black', bg='red', command = lambda: stop_profibus() ).pack()
    Text(master=root,height=12,width=40).pack() 
    root.protocol("WM_DELETE_WINDOW", close) 
    root.mainloop()
   
if __name__ == '__main__':    
    main()
