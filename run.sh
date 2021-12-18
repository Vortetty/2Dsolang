#!/usr/bin/bash

if ! command -v kitty &> /dev/null
then
    echo "The Kitty terminal was not found, this program is only tested within Kitty on non-windows platforms."
    read -r -p "Would you like to install it now?\n [Y/n] >>> " response
    if [[ "$response" =~ ^([nN][oO]|[nN])$ ]]
    then
        read -r -p "Would you like to try to launch in this terminal? (may not work properly if terminal is too small)\n [y/N] >>> " response1
        if [[ "$response1" =~ ^([yY][eE][sS]|[yY])$ ]]
        then
            python3 ./main.py -n "$@"
            exit 0
        else
            exit 0
        fi
    else
        echo "Kitty installed"
        curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin
        echo "Font installed"
        mkdir ~/.local/share/fonts
        cp ./fonts/* ~/.local/share/fonts/
    fi
else
    echo "Kitty is already installed, not installing"
fi

if fc-list | grep -q -i "Consolas for Powerline:style=regular"; then
    echo "Consolas for Powerline already installed, not installing"
else
    echo "Installing Consolas for Powerline"
    mkdir ~/.local/share/fonts
    cp ./fonts/* ~/.local/share/fonts/
    echo "done"
fi


SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

kitty \
    -o allow_remote_control=yes \
    -o initial_window_width=1281 \
    -o initial_window_height=625 \
    -o font_family="Consolas for Powerline" \
    -o bold_font="auto" \
    -o italic_font="auto" \
    -o bold_italic_font="auto" \
    -o font_size=11 \
    -o tab_bar_style=hidden \
    -d="$DIR" \
    python3 ./main.py "$@" &