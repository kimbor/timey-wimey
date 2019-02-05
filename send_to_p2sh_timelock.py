
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
import bitcoin.rpc
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def main():
    # always remember to setup the network
    setup('testnet')

    #
    # This script creates a P2SH address containing a P2PK script and sends
    # some funds to it
    #
    # address we are spending from
    # from_addr = P2pkhAddress('n4bkvTyU1dVdzsrhWBqBw8fEMbHjJvtmJR')

    # # create transaction input from tx id of UTXO (contained 0.1 tBTC)
    # txin = TxInput('76464c2b9e2af4d63ef38a77964b3b77e629dddefc5cb9eb1a3645b1608b790f', 0)


    # # secret key of address that we are trying to spent
    # sk = PrivateKey('cTALNpTpRbbxTCJ2A5Vq88UxT44w1PE2cYqiB3n4hRvzyCev1Wwo')

    # create transaction output using P2SH scriptPubKey (locking script)
    # (the recipient will give us the final address  but for now we create it
    # for demonstration purposes)

    # secret key corresponding to the pubkey needed for the P2SH (P2PK) transaction
    p2pk_sk = PrivateKey('cVS929EhDuLUemssFz5N8BpuJZf6NpSdWmsENBBHUZyzMQLbYLmH')
    p2pk_pk = p2pk_sk.get_public_key().to_hex()

    redeem_script = Script([p2pk_pk, 'OP_CHECKSIG'])
    addressObj = P2shAddress.from_script(redeem_script)
    print("\nAddress:\n" + addressObj.to_address())

# end first program

# start intermission
    access = AuthServiceProxy('http://kim:kim@127.0.0.1:18332')
    transaction = access.sendtoaddress(addressObj.to_address(), 0.0001)
    print('transaction: ' + transaction)
# end intermission

# start second program
    p2pk_sk = PrivateKey('cVS929EhDuLUemssFz5N8BpuJZf6NpSdWmsENBBHUZyzMQLbYLmH')
    p2pk_pk = p2pk_sk.get_public_key().to_hex()
    redeem_script = Script([p2pk_pk, 'OP_CHECKSIG'])
    addressObj = P2shAddress.from_script(redeem_script)

    from_addr = addressObj.to_address()
    to_addr = P2pkhAddress('2MyKrYXiiyqPMiFoPUfjtxbehr7bnpTFrTk')
    
    txin = TxInput()
    txout = TxOutput( 0.08, to_addr.to_script_pub_key() )

    # no change address - the remaining 0.01 tBTC will go to miners)

    # create transaction from inputs/outputs -- default locktime is used
    tx = Transaction([txin], [txout])

    # print raw transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    # use the private key corresponding to the address that contains the
    # UTXO we are trying to spend to create the signature for the txin -
    # note that the redeem script is passed to replace the scriptSig
    sig = p2pk_sk.sign_input(tx, 0, redeem_script )
    #print(sig)

    # # set the scriptSig (unlocking script)
    # txin.script_sig = Script([sig, redeem_script.to_hex()])
    # signed_tx = tx.serialize()

    # txout = TxOutput( 0.09, redeem_script.to_p2sh_script_pub_key() )

    # # no change address - the remaining 0.01 tBTC will go to miners)

    # # create transaction from inputs/outputs -- default locktime is used
    # tx = Transaction([txin], [txout])

    # # print raw transaction
    # print("\nRaw unsigned transaction:\n" + tx.serialize())

    # # use the private key corresponding to the address that contains the
    # # UTXO we are trying to spend to create the signature for the txin
    # sig = sk.sign_input(tx, 0, from_addr.to_script_pub_key() )
    # #print(sig)

    # # get public key as hex
    # pk = sk.get_public_key()
    # pk = pk.to_hex()
    # #print (pk)

    # # set the scriptSig (unlocking script)
    # txin.script_sig = Script([sig, pk])
    # signed_tx = tx.serialize()

    # # print raw signed transaction ready to be broadcasted
    # print("\nRaw signed transaction:\n" + signed_tx)
    # print("\nTxId:", tx.get_txid())


if __name__ == "__main__":
    main()
