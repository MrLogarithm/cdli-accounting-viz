#!/bin/bash
# server script for jekyll docker image

unset BUNDLE_PATH
unset BUNDLE_BIN

exec "$@"
