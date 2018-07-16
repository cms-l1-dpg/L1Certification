#!/bin/tcsh

echo "Setup the key files using your grid certificate:"
if ( ! -f ./keyout.pem ) then
  if ( ! -f $HOME/.globus/userkey.pem ) then
    echo "We need userkey.pem in ~/.globus for Pre/Post firing"
  else
    openssl rsa -in $HOME/.globus/userkey.pem  -out keyout.pem
  endif
endif
echo "Done with grid certificate keys"

echo "Setup the proxy, please login to lxplus.cern.ch"
ssh -fN -L 8080:cmsomsapi:8080 lxplus.cern.ch

