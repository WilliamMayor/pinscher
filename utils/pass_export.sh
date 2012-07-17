#!/bin/bash

DB="$1"
KEYFILE="$2"

echo $(openssl enc -d -aes-256-cbc -in "$DB" -pass file:"$KEYFILE")
