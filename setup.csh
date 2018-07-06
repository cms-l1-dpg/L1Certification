#!/bin/tcsh

if ( ! -f ./keyout.pem ) then
  if ( ! -f $HOME/.globus/userkey.pem ) then
    echo "We need userkey.pem in ~/.globus for Pre/Post firing"
  else
    openssl rsa -in $HOME/.globus/userkey.pem  -out keyout.pem
  endif
endif

ssh -fN -L 8080:cmsomsapi:8080 lxplus.cern.ch

