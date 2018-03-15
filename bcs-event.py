import threading
import argparse
import json
from time import sleep
from datetime import datetime

import logzero
from logzero import logger
from twisted.internet import reactor, task

from neoNode import neoBlockchain

logzero.logfile("/var/log/neo/neo-contract-event.log", maxBytes=1e6, backupCount=3)
contract_sh = '546c5872a992b2754ef327154f4c119baabff65f'
#contract_sh = 'e81c837d37763afbf894d319c868a09f219f2be9'    #testnet contract

node = neoBlockchain(contract_sh,mainnet=True)


@node.smart_contract.on_notify
def sc_notify(event):
    print("SmartContract Runtime.Notify event:", event)

    # Make sure that the event payload list has at least one element.
    if not len(event.event_payload):
        return

    # The event payload list has at least one element. As developer of the smart contract
    # you should know what data-type is in the bytes, and how to decode it. In this example,
    # it's just a string, so we decode it with utf-8:
    print("notify txid:", event.tx_hash)
    print("notify block:", event.tx_hash)
    print("notify payload:", event.event_payload)
    print(str(datetime.now()))
    print("------------------------------------------------------")
    logger.info("-notify - payload:{}".format(event.event_payload))

@node.smart_contract.on_storage
def sc_storage(event):
    print("SmartContract Runtime.Notify event:", event)

    # Make sure that the event payload list has at least one element.
    if not len(event.event_payload):
        return

    # The event payload list has at least one element. As developer of the smart contract
    # you should know what data-type is in the bytes, and how to decode it. In this example,
    # it's just a string, so we decode it with utf-8:
    print("notify txid:", event.tx_hash)
    print("notify block:", event.tx_hash)
    print("notify payload:", event.event_payload)
    print(str(datetime.now()))
    print("------------------------------------------------------")
    logger.info("-storage - payload:{}".format(event.event_payload))


def background():
    while(True) :
        print(node.show_status())
        sleep(20)

    
def main():
    bg = threading.Thread(target=background)
    bg.setDaemon(True)
    bg.start()
    
    node.start()
    reactor.suggestThreadPoolSize(15)
    reactor.run()

if __name__ == '__main__':
    main()
