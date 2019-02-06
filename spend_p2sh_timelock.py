
#
# This script spends funds from a timelock script address.
#

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Please use Python 3.x to run this.\n')
    sys.exit(1)
if len(sys.argv) <= 2:
    sys.stderr.write('Usage: python3 spend_p2sh_timelock.py [private key] [receiver address]\n')
    sys.exit(1)    

import bitcoin.rpc
import binascii

from bitcoin import SelectParams
from bitcoin.core import b2x, b2lx, lx, COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160
from bitcoin.core.script import CScript, CScriptOp, OP_DUP, OP_HASH160, SignatureHash, OP_EQUALVERIFY, OP_CHECKSIG, SIGHASH_ALL, OP_DROP, OP_NOP3
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret

OP_CHECKSEQUENCEVERIFY = OP_NOP3    #unlike other op-codes, python-bitcoinlib doesn't define OP_CHECKSEQUENCEVERIFY, so I define it myself here

SelectParams('testnet')

# parameterize these
privKeySender = str(sys.argv[1])
addressReceiver = str(sys.argv[2])

secret = CBitcoinSecret(privKeySender)

# per instructor message in the COMP541-01-S-2019 Moodle classroom forum, use '0xc800' (200 blocks) for relative timelock amount
# 0xc800 is calculated as little-endian hex of 200, plus '00' tacked on the end because it's necessary to add sign for values which are less than half a byte, otherwise interpreted as negative
redeem_script = CScript([0xc800, OP_CHECKSEQUENCEVERIFY, OP_DROP, OP_DUP, OP_HASH160, Hash160(secret.pub), OP_EQUALVERIFY, OP_CHECKSIG])

txin_scriptPubKey = redeem_script.to_p2sh_scriptPubKey()
txin_p2sh_address = CBitcoinAddress.from_scriptPubKey(txin_scriptPubKey)
print('Pay to:', str(txin_p2sh_address))

proxy = bitcoin.rpc.Proxy()

# the below functionality is to be run from cmd line in between send_to_p2sh_timelock.py and this program
# uncomment to run programmatically for testing purposes
# transactionid = proxy.sendtoaddress(str(txin_p2sh_address), 0.0001*COIN)
# print('transaction id: ' + b2lx(transactionid))

# find the set of UTXO transactions that have been sent to the script address
txins = []  # inputs to the spending transaction we will create
            # We populate this array using unspent transaction outputs that have been sent to the script address
totalUnspentAmount = 0  # total of amounts sent to the script address which are still unspent
VOUT = 0    # always use the incoming transaction's first output
for transaction in proxy.call("listtransactions"):  # query the local node to find the list of recent transactions. 
                                                    # listtransactions defaults to retrieve the 10 most recent transactions
    # now that we have the 10 most recent transactions, we test to see if they go with the script address and are spendable
    if (transaction['address'] == str(txin_p2sh_address)):  # if current transaction is to send coins to the script address
        # create a CMutableTxIn object so that we can test whether it's spendable
        txid = lx(transaction['txid'])  # lx() takes *little-endian* hex and converts it to bytes
        #txin = CMutableTxIn(COutPoint(txid, VOUT))
        txin = CMutableTxIn(COutPoint(txid, VOUT), nSequence=0xc800007f)    # per instructor msg in the forums, use '0xc800007f' for 200 blocks
        try:
            # test to see if this transaction is spendable
            # throws an IndexError error if it's not
            proxy.gettxout(txin.prevout)    
        except IndexError:
            # if transaction is not spendable, ignore it
            continue
        else:
            # if transaction is spendable, add it to our array
            txins.append(txin)
            # and update the total amount available to us to spent
            # transaction amounts sent to script address are negative because they are debits against sender account
            # multiply by -1 to make them positive
            # then add to total
            totalUnspentAmount += (transaction['amount'] * -1)
            #print('Including UTXO transaction ' + transaction['txid'] + ' for ' + str(transaction['amount'] * -1))

# calculate the mining fee
#FEE_PER_BYTE = 0.00025*COIN/1000    #todo: use estimatesmartfee function instead
#mining_fee = len(txins.serialize()) * FEE_PER_BYTE
mining_fee = 0.00000350     # todo: calculate this instead of hard-coding it
assert(totalUnspentAmount > mining_fee), 'Not enough funds available to spend'
output_amt = float(totalUnspentAmount) - mining_fee

# Create the txout. This time we create the scriptPubKey from a Bitcoin address.
txout = CMutableTxOut(output_amt*COIN, CBitcoinAddress(addressReceiver).to_scriptPubKey())

# Create the unsigned transaction.
tx = CMutableTransaction(txins, [txout])  # maybe need to add parameter 'nLockTime=200'? It seems to work without this parameter, but slide 74 says it's needed
#print("raw unsigned transaction: " + b2x(tx.serialize()))

for index, txin in enumerate(txins):
    # Calculate the signature hash for that transaction. Note how the script we use
    # is the redeemScript, not the scriptPubKey. That's because when the CHECKSIG
    # operation happens EvalScript() will be evaluating the redeemScript, so the
    # corresponding SignatureHash() function will use that same script when it
    # replaces the scriptSig in the transaction being hashed with the script being
    # executed.
    sighash = SignatureHash(redeem_script, tx, index, SIGHASH_ALL)

    # Now sign it. We have to append the type of signature we want to the end, in
    # this case the usual SIGHASH_ALL.
    sig = secret.sign(sighash) + bytes([SIGHASH_ALL])

    # Set the scriptSig of our transaction input appropriately.
    txin.scriptSig = CScript([sig, redeem_script])
    # Verify the signature worked. This calls EvalScript() and actually executes
    # the opcodes in the scripts to see if everything worked out. If it doesn't an
    # exception will be raised.
    # this is commented out so that locktime requirement error is not hidden when this script is run before locktime requirement is satisfied
    # VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, index, (SCRIPT_VERIFY_P2SH,))

# Done setting up the transaction. Display it.
# print('transaction: ' + b2x(tx.serialize()))

# actually execute the transaction
transactionid = proxy.sendrawtransaction(tx)
# decode and print the resulting transaction id. Using bytes to little-endian hex function.
print('transaction id: ' + b2lx(transactionid))
