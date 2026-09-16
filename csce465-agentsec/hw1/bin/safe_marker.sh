#! /bin/bash

path="$HOME/csce465-agentsec/hw1/markers/marker.txt"
# only accept 1 pos var"
if [ "$#" -ne 1 ]; then
	echo "ERR: Too many arguments"
	exit 1
fi 

# check if the arg is course-marker
if [ "$1" != "course-marker" ]; then
	echo "ERR: This is an unacceptable argument"
	exit 1
fi

echo "Received course-marker argument: $1"

# Make the file path
mkdir -p "$(dirname "$path")"
printf 'course-marker created at %s\n' "$(date -u +%FT%TZ)" > "$path"


