#!/bin/bash

#handle boot time
mysql -u terminator -p  terminator -e "drop table proxies;" --password='n5cHK9pBt1oAdcY!!'
sleep 30
/opt/terminator/bin/cusbi /R:$(/opt/terminator/bin/cusbi /Q | grep tty | cut -d',' -f1)
while true; do
	/opt/terminator/scripts/services/checker.py
	sleep 10
done;
