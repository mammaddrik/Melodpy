#!/bin/bash

RED="\033[1;31m"
BLUE="\033[1;34m"
GREEN='\033[1;32m'
RESET="\033[1;37m"

function ctrl_c(){
    echo -e "\n\n${RED}Finishing up...${RESET}\n"
    exit 2
}

os="$( awk -F '=' '/^ID=/ {print $2}' /etc/os-release 2>&- )"
kernel_version="$( uname -r )"
hardware_architecture="$( uname -m )"
kernel="$( uname )"
username="$( whoami )"
loc="$( pwd )"
path=`pwd`

func_title(){
    echo " ==============================================================================="
    echo "                             Melodpy (Setup Script)                             "
    echo " ==============================================================================="
    echo "                                                                                "
    echo "                                os = ${os}                                      "
    echo "                            kernel = ${kernel}                                  "
    echo "                    kernel version = ${kernel_version}                          "
    echo "                      architecture = ${hardware_architecture}                   "
    echo "                          trueuser = ${username}                                "
    echo "                          location = ${loc}                                     "
    echo "                                                                                "
}

clear
func_title

mkdir -p /usr/share/Melodpy
cp setup.sh /usr/share/Melodpy
cp melodpy.py /usr/share/Melodpy
cp -r detect/ lib/ src/ /usr/share/Melodpy

echo "#!/bin/sh" >> /usr/bin/Melodpy
echo "cd /usr/share/Melodpy" >> /usr/bin/Melodpy
echo "exec python melodpy.py \"\$@\"" >> /usr/bin/Melodpy
cp $path/logo/Melodpy.desktop /usr/share/applications/Melodpy.desktop
cp $path/logo/Melodpy.png /usr/share/icons/Melodpy.png
cp melodpy.py /usr/local/sbin/melodpy.py
cp -r detect/ lib/ src/ /usr/local/sbin
chmod +x /usr/local/sbin/melodpy.py
chmod +x melodpy.py

echo -e "[${GREEN}✔${RESET}]Done"
echo -e "${GREEN} ╔───────────────────────────╗${RESET}"
echo -e "${GREEN} | ${BLUE}Run in Terminal (Melodpy) ${GREEN}|${RESET}"
echo -e "${GREEN} ╚───────────────────────────╝${RESET}"
exit

trap ctrl_c INT