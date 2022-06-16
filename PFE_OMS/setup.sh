#!/bin/sh

echo "Setup the key files using your grid certificate:"
if [ ! -f ./keyout.pem ]; then
  if [ ! -f $HOME/.globus/userkey.pem ]; then
    echo "We need userkey.pem in ~/.globus for Pre/Post firing"
  else
    openssl rsa -in $HOME/.globus/userkey.pem  -out keyout.pem
  fi
fi
echo "Done with grid certificate keys"

echo "Setup the proxy, please login to lxplus.cern.ch"
echo -n "Enter your lxplus username and press [ENTER]: "
read var_name
echo "Your name is: $var_name"
ssh -fN -L 8080:cmsomsapi:8080 $var_name@lxplus.cern.ch

