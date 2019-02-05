import sys
if sys.version_info.major < 3:
    sys.stderr.write('Please use Python 3.x to run this.\n')
    sys.exit(1)

import hashlib
import bitcoin.rpc

from bitcoin import SelectParams
from bitcoin.core import b2x, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret

SelectParams('testnet')  # CHANGE THIS TO regtest

# parameterize these
privKeySender = 'cVS929EhDuLUemssFz5N8BpuJZf6NpSdWmsENBBHUZyzMQLbYLmH'
addressReceiver = '2Myk6MB7DTEzuPC17v1voy5U8snwSULALyr'

secret = CBitcoinSecret(privKeySender)
redeem_script = CScript([secret.pub, OP_CHECKSIG])
#redeem_script = CScript([OP_DUP, OP_HASH160, secret.pub, OP_EQUALVERIFY, OP_CHECKSIG])

print("public key: " + str(secret.pub))
print('redeem script: ' + b2x(redeem_script))

txin_scriptPubKey = redeem_script.to_p2sh_scriptPubKey()
txin_p2sh_address = CBitcoinAddress.from_scriptPubKey(txin_scriptPubKey)
print('Pay to:', str(txin_p2sh_address))

# start intermission
proxy = bitcoin.rpc.Proxy()
transaction = proxy.sendtoaddress(str(txin_p2sh_address), 0.001*COIN)
print('transaction: ' + str(transaction))
# end intermission

print ('Unspent transactions:')
for transaction in proxy.call("listtransactions"):
    if (transaction['address'] == str(txin_p2sh_address)):
        print('transaction: ' + transaction['txid'])
        # lx() takes *little-endian* hex and converts it to bytes; in Bitcoin
        # transaction hashes are shown little-endian rather than the usual big-endian.
        txid = lx(transaction['txid'])
print ('End unspent')


vout = 0

# Create the txin structure, which includes the outpoint. The scriptSig defaults to being empty.
txin = CMutableTxIn(COutPoint(txid, vout))
#txin = CMutableTxIn(COutPoint(txid, vout), nSequence=0xc800007f)

# Create the txout. This time we create the scriptPubKey from a Bitcoin address.
txout = CMutableTxOut(0.0001*COIN, CBitcoinAddress(addressReceiver).to_scriptPubKey())

# Create the unsigned transaction.
tx = CMutableTransaction([txin], [txout])
print('tx: ' + str(tx))

# Calculate the signature hash for that transaction. Note how the script we use
# is the redeemScript, not the scriptPubKey. That's because when the CHECKSIG
# operation happens EvalScript() will be evaluating the redeemScript, so the
# corresponding SignatureHash() function will use that same script when it
# replaces the scriptSig in the transaction being hashed with the script being
# executed.
sighash = SignatureHash(redeem_script, tx, 0, SIGHASH_ALL)

# Now sign it. We have to append the type of signature we want to the end, in
# this case the usual SIGHASH_ALL.
sig = secret.sign(sighash) + bytes([SIGHASH_ALL])

# Set the scriptSig of our transaction input appropriately.
txin.scriptSig = CScript([sig, redeem_script])

# Verify the signature worked. This calls EvalScript() and actually executes
# the opcodes in the scripts to see if everything worked out. If it doesn't an
# exception will be raised.
VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))

# Done! Print the transaction to standard output with the bytes-to-hex
# function.
print('transaction: ' + b2x(tx.serialize()))

#actually execute the transaction
#delete this later
proxy.sendrawtransaction(tx)



