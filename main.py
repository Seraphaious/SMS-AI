# File: main.py

# Required Imports
import threading
import logging
import pinecone
from gsmmodem.modem import GsmModem
from functools import partial

from sms.handle_sms import delete_all_sms, handle_sms, monitor_sms_storage_and_delete
from config import *

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

    print("Initializing modem...")
    modem = GsmModem(PORT, BAUD_RATE)
    modem.smsTextMode = False
    modem.connect()
    delete_all_sms(modem)

    modem.waitForNetworkCoverage(10)
    modem.smsReceivedCallback = partial(handle_sms, modem=modem)

    stop_event = threading.Event()
    storage_monitor_thread = threading.Thread(target=monitor_sms_storage_and_delete, args=(stop_event,modem))
    storage_monitor_thread.start()

    print("Waiting for SMS messages...")
    try:
        modem.rxThread.join()  # Removed the timeout argument
    except KeyboardInterrupt:
        print("\nExiting...")
        stop_event.set()
        storage_monitor_thread.join()
    finally:
        modem.close()
