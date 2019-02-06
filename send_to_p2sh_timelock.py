
#
# This script creates a P2SH address containing a timelock script.
# All funds sent to the address will be locked for a period of time.
#

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Please use Python 3.x to run this.\n')
    sys.exit(1)

from bitcoin import SelectParams
from bitcoin.core import Hash160
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, OP_DROP, OP_NOP3
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret

OP_CHECKSEQUENCEVERIFY = OP_NOP3    #unlike other op-codes, python-bitcoinlib doesn't define OP_CHECKSEQUENCEVERIFY, so I define it myself here

SelectParams('testnet')  # CHANGE THIS TO regtest

# todo: parameterize these
# address we are spending from
privKeySender = 'cVS929EhDuLUemssFz5N8BpuJZf6NpSdWmsENBBHUZyzMQLbYLmH'

secret = CBitcoinSecret(privKeySender)
#redeem_script = CScript([secret.pub, OP_CHECKSIG])
redeem_script = CScript([0xc800, OP_CHECKSEQUENCEVERIFY, OP_DROP, OP_DUP, OP_HASH160, Hash160(secret.pub), OP_EQUALVERIFY, OP_CHECKSIG])

txin_scriptPubKey = redeem_script.to_p2sh_scriptPubKey()
txin_p2sh_address = CBitcoinAddress.from_scriptPubKey(txin_scriptPubKey)
print('Pay to:', str(txin_p2sh_address))
