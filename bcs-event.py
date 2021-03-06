import threading
import argparse
import json
from time import sleep
from datetime import datetime

import logzero
from logzero import logger
from twisted.internet import reactor, task

from neo_node.neoNode import neoBlockchain

from database import session
from database.schema import Event , Storage
from config import config

logzero.logfile(config.logfile, maxBytes=1e6,backupCount=config.backupCount)
neo_addr_length=config.neo_addr_length

node = neoBlockchain(config.contract_sh,mainnet=config.mainnet)


@node.smart_contract.on_notify
def sc_notify(event):
    print("SmartContract Event:", event)
    print("------------------------------------------------------")

    # Make sure that the event payload list has at least one element.
    if not len(event.event_payload):
        return

    # The event payload list has at least one element. As developer of the smart contract
    # you should know what data-type is in the bytes, and how to decode it. In this example,
    # it's just a string, so we decode it with utf-8:
    event_data=Event()
    event_data.event_type = str(event.event_type)
    event_data.tx_hash = str(event.tx_hash)
    event_data.block_number = event.block_number
    event_data.method = event.event_payload[0].decode("utf-8")
    if (event_data.method == 'deploy'):
        print("Deploying Smart contract")
        pass

    elif (event_data.method == 'circulation'):
        pass

    elif (event_data.method == 'mintTokens'):
        print("mintTokens payload:",event.event_payload)
        pass

    elif (event_data.method == 'crowdsale_available'):
        pass

    elif (event_data.method == 'transfer'):
        print("Tranfer")
        try:
            event_data.param1 = node.toAddr(event.event_payload[1])
        except:
            event_data.param1 = event.event_payload[1]

        try:
            event_data.param2 = node.toAddr(event.event_payload[2])
        except:
            event_data.param2 = event.event_payload[2]

        try:
            event_data.param3 = str( int.from_bytes(event.event_payload[3],'little') )
        except:
            event_data.param3 = str(event.event_payload[3])

    event_data.execution_success = event.execution_success
    #event_data.timestamp = datetime.now()
    event_data.timestamp = datetime.utcnow()
    
    if not session.query(Event).filter(Event.tx_hash == event_data.tx_hash).count():
        print("Adding to database")
        session.add(event_data)
        session.commit()
    else :
        print("Already have a transection")

    print('Time:',str(datetime.utcnow()))
    print("------------------------------------------------------")
    logger.info("-event:{} - payload:{}".format(event.event_type,event.event_payload))

@node.smart_contract.on_storage
def sc_storage(event):
    print("SmartContract Event:", event)

    # Make sure that the event payload list has at least one element.
    if not len(event.event_payload):
        return

    if (event.execution_success or (str(event.event_type) == 'SmartContract.Storage.Delete') and (event.test_mode==False) ) :
        print("------------------------------------------------------")

        key = event.event_payload[0].replace(" ", "")
        if "b'" in key:
            try:
                key = eval(key).decode('utf-8')
            except:
                print('Invalid Key')
                print("------------------------------------------------------")
                return

        if not len(key) == neo_addr_length :
            print('key is not an address')

        storage_data = session.query(Storage).filter(Storage.key == key).first()
        if not (storage_data == None) :
            print('Updateing key {} to 0'.format(key))

            storage_data.data = '0'
            storage_data.last_changed = datetime.utcnow()
            #storage_data.last_changed = datetime.now()

            session.commit()

        print('Time:',str(datetime.utcnow()))
        print("------------------------------------------------------")

    if (event.execution_success or (str(event.event_type) == 'SmartContract.Storage.Put') and (event.test_mode==False) ) :

        print("------------------------------------------------------")
        #spilting key and data

        payload = event.event_payload[0].split()

        key = payload[0].replace(" ", "")
        data = payload[2]

        if "b'" in key:
            try:
                key = eval(key).decode('utf-8')
            except:
                print('Invalid Key')
                print("------------------------------------------------------")

                return

        if "b'" in data:
            try:
                data = int.from_bytes( eval(data),'little' )
                data = str(data)
            except:
                print('Invalid data')
                print("------------------------------------------------------")
                return

        print('Key:',key,' Data:',data)
       
        if not len(key) == neo_addr_length :
            print('key is not an address')
        
        storage_data = session.query(Storage).filter(Storage.key == key).first()
        #update key case
        if not (storage_data == None) :
            print('Updateing key')

            storage_data.data = data
            storage_data.last_changed = datetime.utcnow()
            #storage_data.last_changed = datetime.now()

            session.commit()

        #create new key
        else :
            print('Adding new key')

            storage_data = Storage()
            storage_data.key = key
            storage_data.data = data
            storage_data.last_changed = datetime.utcnow()
            #storage_data.last_changed = datetime.now()

            session.add(storage_data)
            session.commit()
        
        print('Time:',str(datetime.utcnow()))
        print("------------------------------------------------------")

    logger.info("-event:{} - payload:{}".format(event.event_type,event.event_payload))


def background():
    while(True) :
        print(node.show_status())
        sleep(20)

    
def main():
    bg = threading.Thread(target=background)
    bg.setDaemon(True)
    bg.start()
    logger.info("BCS Event Starting..")
    node.start()
    reactor.suggestThreadPoolSize(15)
    reactor.run()
    logger.info("Shutting down..")

if __name__ == '__main__':
    main()
