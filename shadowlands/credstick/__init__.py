import hid, threading, time
from hexbytes import HexBytes
from eth_account.internal.transactions import Transaction, UnsignedTransaction
from eth_utils import decode_hex, encode_hex
from eth_utils.crypto import keccak
from eth_account.datastructures import AttributeDict
import rlp
from time import sleep


from shadowlands.tui.debug import debug
import pdb


# TODO
# fork eth-account and eth-keys repos from the Web3.py project and 
# submit a PR to make this all a subsystem of web3

class NoCredstickFoundError(Exception):
    pass

class DeriveCredstickAddressError(Exception):
    pass

class OpenCredstickError(Exception):
    pass

class CloseCredstickError(Exception):
    pass

class SignTxError(Exception):
    pass

class StillHaveCredstick(Exception):
    pass

#import pdb; pdb.set_trace()

class Credstick(object):
    interface = None
    eth_node = None
    manufacturer = None
    product = None
    address = None
    detect_thread = None
    detect_thread_shutdown = False

    @classmethod
    def addressStr(cls):
        return cls.address

    @classmethod
    def heartbeat(cls):
        return

    @classmethod
    def detect(cls):
        for hidDevice in hid.enumerate(0, 0):
            if hidDevice['vendor_id'] == 0x2c97:
                if ('interface_number' in hidDevice and hidDevice['interface_number'] == 0) or ('usage_page' in hidDevice and hidDevice['usage_page'] == 0xffa0):
                    if hidDevice['path'] is not None:
                        from shadowlands.credstick.ledger_ethdriver import LedgerEthDriver
                        LedgerEthDriver.manufacturer = hidDevice['manufacturer_string']
                        LedgerEthDriver.product = hidDevice['product_string']
                        return LedgerEthDriver
            elif hidDevice['vendor_id'] == 0x534c:
                if ('interface_number' in hidDevice and hidDevice['interface_number'] == -1) or ('usage_page' in hidDevice and hidDevice['usage_page'] in [0xf1d0, 0xff00]):
                    if hidDevice['path'] is not None:
                        from shadowlands.credstick.trezor_ethdriver import TrezorEthDriver
                        TrezorEthDriver.manufacturerStr = hidDevice['manufacturer_string']
                        TrezorEthDriver.productStr = hidDevice['product_string']
                        sleep(1)
                        return TrezorEthDriver
            elif hidDevice['vendor_id'] == 0x1209:
                if ('interface_number' in hidDevice and hidDevice['interface_number'] == -1) or ('usage_page' in hidDevice and hidDevice['usage_page'] in [0xf1d0, 0xff00]):
                    if hidDevice['path'] is not None:
                        from shadowlands.credstick.trezor_ethdriver import TrezorEthDriver
                        TrezorEthDriver.manufacturerStr = hidDevice['manufacturer_string']
                        TrezorEthDriver.productStr = 'Trezor Model T'
                        ##hidDevice['product_string']
                        sleep(1)
                        return TrezorEthDriver
 
        raise NoCredstickFoundError("Could not identify any supported credstick")

    @classmethod
    def start_detect_thread(cls):
        cls.detect_thread = threading.Thread(target=cls.credstick_finder)
        cls.detect_thread.start()

    @classmethod 
    def stop_detect_thread(cls):
        cls.detect_thread_shutdown = True 
        cls.detect_thread.join()

    @classmethod
    def credstick_finder(cls):

        while not cls.detect_thread_shutdown:
            try: 
                credstick = cls.detect()

                if credstick == credstick.interface._credstick:
                    # We still have our credstick.
                    # Go to sleep for a bit.
                    raise StillHaveCredstick

                # We found a new credstick.  Let's wipe all
                # possible associations with an old one.
                credstick.interface._credstick = None
                credstick.eth_node._credstick = None
                credstick.address = None
                credstick.manufacturer = None
                credstick.product = None
                   
                credstick.open()
                credstick.derive()

                timeout = 30 

                while credstick.address is None and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                if credstick.address is None:
                    raise DeriveCredstickAddressError

                #debug(); pdb.set_trace()

                cls.eth_node.credstick = credstick
                cls.interface.credstick = credstick
                cls.interface.credstick_situation_changed = True
            except NoCredstickFoundError:
                # did we have one a moment ago?
                if cls.interface._credstick is None:
                    time.sleep(0.25)
                    continue

                # We lost our credstick!
                # wipe everything off the previous one.
                old_credstick = cls.interface._credstick 
                old_credstick.interface._credstick = None
                old_credstick.eth_node._credstick = None
                old_credstick.address = None
                old_credstick.manufacturer = None
                old_credstick.product = None
 
                cls.interface._credstick = None
                cls.eth_node._credstick = None
                cls.interface.credstick_situation_changed = True
            except(OpenCredstickError, DeriveCredstickAddressError, StillHaveCredstick):
                time.sleep(0.25)

    @classmethod
    def prepare_tx(cls, transaction_dict):
        try:
            del(transaction_dict['chainId'])
        except:
            # Fine, if it isn't there it isn't there. jeez.
            pass

        # if to and data fields are hex strings, turn them into byte arrays
        if (transaction_dict['to']).__class__ == str:
            transaction_dict['to'] = decode_hex(transaction_dict['to'])

        if (transaction_dict['data']).__class__ == str:
            transaction_dict['data'] = decode_hex(transaction_dict['data'])

        return transaction_dict

    @classmethod
    def signed_tx(cls, transaction_dict, v, r, s):
        tx = UnsignedTransaction.from_dict(transaction_dict)

        trx = Transaction(tx.nonce, tx.gasPrice, tx.gas, tx.to, tx.value, tx.data, v, r, s)
        #debug(); pdb.set_trace()
        enctx = rlp.encode(trx)
        transaction_hash = keccak(enctx)

        attr_dict =  AttributeDict({
            'rawTransaction': HexBytes(enctx),
            'hash': HexBytes(transaction_hash),
            'r': r,
            's': s,
            'v': v,
        })
        
        return attr_dict


    @classmethod
    def open(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def close(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def heartbeat(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def derive(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def signTx(cls, transaction_dict, r=None, s=None, v=None):

 
        raise NotImplementedError(optional_error_message)

    @classmethod
    def open(cls):
        raise NotImplementedError(optional_error_message)


