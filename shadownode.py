import sys, time
from web3.exceptions import UnhandledRequest
from web3.auto import w3

localNode = True
block = ""
nodeVersion = ""
syncing = {}
blocksBehind = None
ethBalance = None
ethAddress = None


def connect():
    global w3, localNode

    connected = w3.isConnected()
    if connected and w3.version.node.startswith('Parity'):
        enode = w3.parity.enode
    elif connected and w3.version.node.startswith('Geth'):
        enode = w3.admin.nodeInfo['enode']
    else:
        localNode = False
        print("Could not find parity or geth locally")
        del sys.modules['web3.auto']
        os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
        from web3.auto.infura import w3

    if not w3.isConnected():
        print("Sorry chummer, couldn't connect to an Ethereum node.")
        exit()


def heartbeat():
    global nodeVersion, block, blocksBehind, syncing, ethBalance
    while True:
        #       assert w3.isConnected()
        nodeVersion = w3.version.node
        block = str(w3.eth.blockNumber)
        syncing = w3.eth.syncing

        if syncing:
            blocksBehind = syncing['highestBlock'] - syncing['currentBlock']

        if ethAddress:
            ethBalance = w3.eth.getBalance(ethAddress)

        if localNode:
            time.sleep(.5)
        else:
            time.sleep(10)


