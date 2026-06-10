#!/bin/sh
set -e

mkdir -p "$HOME/bin"
curl -sL https://raw.githubusercontent.com/SimonRiemertzon/ferrybot/main/ferry.py -o "$HOME/bin/ferry"
chmod +x "$HOME/bin/ferry"
echo "ferry installed to $HOME/bin/ferry"

case ":$PATH:" in
  *":$HOME/bin:"*)
    echo "All done! Try running: ferry"
    ;;
  *)
    echo ""
    echo "Almost there! ~/bin is not in your PATH yet."
    echo "Add it by running this command:"
    echo ""
    echo '  echo '\''export PATH="$HOME/bin:$PATH"'\'' >> ~/.zshrc && source ~/.zshrc'
    echo ""
    echo "If you use bash instead of zsh, replace .zshrc with .bashrc"
    echo "Then run: ferry"
    ;;
esac
