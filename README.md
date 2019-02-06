# timey-wimey
Python script to create and spend a time-locked bitcoin script address.

Assignment for COMP-541 February 2019.

Requirements:

Using the programming language of your choice implement two programs/scripts. The first one will create an address where all funds sent to it should be locked for N time after its creation; other than the time locking the redeem script should be equivalent to P2PKH. The second program will allow someone to spent funds from this address.
Both programs should:
- use testnet 
- assume a local Bitcoin testnet node is running
The first program should:
- accept a public (or optionally a private) key for the P2PKH part of the redeem script
- accept a future time period expressed either in block height or in UNIX Epoch time
- display the P2SH address
The second program should:
- accept a future time period and a private key (to recreate the redeem script as above and also use to unlock the P2PKH part)
- accept a P2SH address to get the funds from
- accept a P2PKH address to sent the funds to
- calculate the appropriate fees
- sent all funds of the local wallet from the P2SH address to the P2PKH address provided
- display the transaction id
Notes:
- there is some repetition between the 2 programs; this is fine
- you will submit a single compressed file (ZIP or TGZ) that contains the source code and the executables, if any (e.g. for static languages). It should include a text file with detailed instructions on how to run your programs.
- If an executable is submitted it should be compiled for x86_64 on linux. Unfortunately, I cannot check executables on Windows or Mac so make sure you use an interpreted language if you work on any of these.
- the source code is your main submission and it should contain everything you want to share with me. It should include detailed comments and everything else you think I should be aware of.
- you are expected to manually construct the Bitcoin locking/unlocking script for the timelock transactions. If the programming libraries you are using have functionality to automatically create timelock transactions do not use them (it will be penalized).
- do not use CHECKLOCKTIMEVERIFY
