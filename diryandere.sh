#!/bin/bash
figlet Dir Yandere
echo "######################################			Directory Yandere : automated subdomain discovery tool 		#######################################"
echo "###################################### 				   Created by Gustavo Redol				#######################################"
echo "######################################			Usage: ./diryandere -> Awnser questions				#######################################"
#Collects target and  prepares for custom wordlist
echo "================================================================================================================================================================="
read -p "Type in the target URL: " tgt
read -p "Do you want to use a custom wordlist? 0-No 1-Yes " cwl
#in case of custom wordlist this loop will take place	
	if [ $cwl -gt 0 ]
	then
		read -p "Type path to wordlist: " trail
			for wrd in $(cat $trail)
			do
				ret=$(curl -s -H "User-Agent: Mozilla Firefox 123.0" -o /dev/null -w "%{http_code}" $tgt/$wrd/)
				if [ $ret == "200" ]
				then 
					echo "Directory found : $wrd"
				fi
			done
			
#when a custom wordlist is not needed this loop takes place
	else
		for plv in $(cat lista1.txt )
		do
			resp=$(curl -s -H "User-Agent: Mozilla Firefox 123.0" -o /dev/null -w "%{http_code}" $tgt/$plv/)
			if [ $resp == "200" ]
			then
			echo "Directory found : $tgt/$plv"
			fi
		done
	fi
