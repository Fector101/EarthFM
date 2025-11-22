#!/usr/bin/env bash
set -e

cp /home/tdynamos/git/python-for-android/pythonforandroid/bootstraps/common/build/jni/application/src/start.c \
   /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/jni/application/src/start.c

rm -f /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/obj/local/arm64-v8a/objs-debug/main/start.o
/home/tdynamos/.buildozer/android/platform/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/bin/clang -MMD -MP -MF /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/obj/local/arm64-v8a/objs-debug/main/start.o.d -target aarch64-none-linux-android24 -fdata-sections -ffunction-sections -fstack-protector-strong -funwind-tables -no-canonical-prefixes --sysroot /home/tdynamos/.buildozer/android/platform/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/sysroot -g -Wno-invalid-command-line-argument -Wno-unused-command-line-argument -D_FORTIFY_SOURCE=2 -fpic -O0 -UNDEBUG -fno-limit-debug-info -I/home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/jni/application/src/../../SDL/include -I/home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/jni/SDL/include -I/home/tdynamos/.buildozer/android/platform/android-ndk-r28c/sources/android/cpufeatures -I/home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/jni/application/src -DANDROID -I/home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/other_builds/python3/arm64-v8a__ndk_target_24/python3/Include -Wformat -Werror=format-security -c /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/jni/application/src/start.c -o /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/obj/local/arm64-v8a/objs-debug/main/start.o
/home/tdynamos/.buildozer/android/platform/android-ndk-r28c/toolchains/llvm/prebuilt/linux-x86_64/bin/clang -Wl,-soname,libmain.so -shared /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/obj/local/arm64-v8a/objs-debug/main/start.o -latomic /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/obj/local/arm64-v8a/libSDL3.so -target aarch64-none-linux-android24 -no-canonical-prefixes -Wl,--build-id=sha1 -Wl,--no-rosegment -L/home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/other_builds/python3/arm64-v8a__ndk_target_24/python3/android-build -Wl,--no-undefined -Wl,--fatal-warnings -Wl,--no-undefined-version -lGLESv1_CM -lGLESv2 -llog -lpython3.14 -ldl -lc -lm -o /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/obj/local/arm64-v8a/libmain.so
install -p /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/obj/local/arm64-v8a/libmain.so /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/libs/arm64-v8a/libmain.so

adb push /home/tdynamos/EarthFM/.buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl3/libs/arm64-v8a/libmain.so /data/local/tmp/libmain.so

adb shell '
APP=$(dirname "$(pm path org.tdynamos.earthfm | sed s/package://)")
cp /data/local/tmp/libmain.so "$APP/lib/arm64/libmain.so"
chmod 755 "$APP/lib/arm64/libmain.so"
'
adb shell am force-stop org.tdynamos.earthfm

adb shell am start -n org.tdynamos.earthfm/org.kivy.android.PythonActivity -a com.kivy.android.PythonActivity

sleep 1

adb shell pidof org.tdynamos.earthfm | xargs -I {} adb logcat --pid={}
