#!/bin/bash

# For this script, a rooted Android device is required.

# Usage Info
USAGE="
Usage: ./file_push.sh <local_directory> [-r|--restart] [-a|--adb-root]

Pushes all files from <local_directory> to your app's private directory on the device.
Requires either:
 - root access with adb root mode (via --adb-root)
 - OR root access with the app marked debuggable (default run-as method)
"

# Check for arguments
if [ -z "$1" ]; then
  echo "Missing directory argument!"
  echo "$USAGE"
  exit 1
fi

if ! test -d "$1"; then
  echo "Directory '$1' does not exist!"
  echo "$USAGE"
  exit 1
fi

# Optional flags
SHOULD_RESTART=false
USE_ADB_ROOT=false

for arg in "$@"; do
  case $arg in
    -r|--restart)
      SHOULD_RESTART=true
      ;;
    -a|--adb-root)
      USE_ADB_ROOT=true
      ;;
  esac
done

PACKAGE_NAME="org.tdynamos.earthfm"
ENTRYPOINT="org.kivy.android.PythonActivity"
APP_DIR="/data/user/0/$PACKAGE_NAME/files/app"

# Stop app if requested
if [[ "$SHOULD_RESTART" == true ]]; then
  echo "Stopping app $PACKAGE_NAME..."
  adb shell am force-stop "$PACKAGE_NAME"
fi

push_file_run_as() {
  local src="$1"
  local dest="$2"
  local base=$(basename "$src")
  local dest_dir=$(dirname "$dest")
  local term_width=$(tput cols)

  printf "\r%-*s" "$term_width" "Pushing (run-as): $src"

  adb push "$src" /data/local/tmp/ >/dev/null 2>&1

  adb shell >/dev/null 2>&1 <<EOF
su -c 'run-as $PACKAGE_NAME sh -c "
mkdir -p \"$dest_dir\"
cp \"/data/local/tmp/$base\" \"$dest\"
chmod 644 \"$dest\"
"'
EOF
}

push_file_adb_root() {
  local src="$1"
  local dest="$2"
  local base=$(basename "$src")
  local dest_dir=$(dirname "$dest")
  local term_width=$(tput cols)

  printf "\r%-*s" "$term_width" "Pushing (adb root): $src"

  # Push directly into the target location
  adb shell su -c "mkdir -p '$dest_dir'" >/dev/null 2>&1
  adb push "$src" "/sdcard/tmp_push_$base" >/dev/null 2>&1
  adb shell su -c "cp '/sdcard/tmp_push_$base' '$dest' && chmod 644 '$dest' && rm '/sdcard/tmp_push_$base'" >/dev/null 2>&1
}

# Push each file
echo "Pushing to $APP_DIR/$1"
FILES=$(ls "$1")

for file in $FILES; do
  local_path="$1/$file"
  remote_path="$APP_DIR/$1/$file"
  if test -f "$local_path"; then
    if [[ "$USE_ADB_ROOT" == true ]]; then
      push_file_adb_root "$local_path" "$remote_path"
    else
      push_file_run_as "$local_path" "$remote_path"
    fi
  fi
done

# Restart app if requested
if [[ "$SHOULD_RESTART" == true ]]; then 
  echo -e "\nRestarting app..."
  adb shell am start -n "$PACKAGE_NAME/$ENTRYPOINT" -a "$ENTRYPOINT"
fi

echo -e "\nDone."
