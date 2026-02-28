# This .spec config file tells Buildozer an app's requirements for being built.
#
# It largely follows the syntax of an .ini file.
# See the end of the file for more details and warnings about common mistakes.

[app]

# (str) Title of your application
title = EarthFM

# (str) Package name
package.name = earthfm

# (str) Package domain (needed for android/ios packaging)
package.domain = org.tdynamos

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,ttf

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (leave empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (leave empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
# Do not prefix with './'
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy

requirements = python3, kivy==master, materialyoucolor
    # kivy==master,
    # materialyoucolor,
    # materialshapes,
    # exceptiongroup,
    # asyncgui,
    # asynckivy,
    # android,
    # pillow,
    # pycairo,
    # scipy,
    # ffmpeg,
    # https://github.com/kivymd/KivyMD/archive/master.zip,


# (list) Additional package index urls used for dependency resolution (currently Android only)
# These indexes are searched in addition to the default PyPI index during Android builds.
#  WARNING: Third party indexes are untrusted sources and may introduce supply chain risks,
# including malicious, tampered, outdated, or incompatible packages.
extra_index_urls = https://chaquo.com/pypi-13.1/, https://anshdadwal.is-a.dev/p4a-wheels/p4a/

# (bool) Disable use of prebuilt binary packages when available (currently Android only)
# If enabled, all dependencies are built from source even if prebuilt wheels exist.
skip_prebuilt = False

# (list) Packages allowed to use available prebuilt wheels (currently Android only)
# Overrides recipe pinned versions and bypasses default version selection behavior
# when a compatible prebuilt wheel is available in the index.
# Example: if kivy==2.3.1 is requested but only `3.0.0` is available in prebuilt index,
# this option allows using the prebuilt wheel instead of building from source.
use_prebuilt_version_for = kivy, numpy, materialyoucolor

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (bool) Indicate if the application should be fullscreen or not
fullscreen = False

#android.aars = 

#android.accept_sdk_license = False

#android.activity_class_name = org.kivy.android.PythonActivity

#android.adb_args = -H host.docker.internal

#android.add_activities = com.example.ExampleActivity

#android.add_assets = 

#android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

#android.add_gradle_repositories = 

#android.add_jars = foo.jar, bar.jar, path/to/more/*.jar

#android.add_libs_arm64_v8a = libs/android-v8/*.so

#android.add_libs_armeabi = libs/android/*.so

#android.add_libs_armeabi_v7a = libs/android-v7/*.so

#android.add_libs_mips = libs/android-mips/*.so

#android.add_libs_x86 = libs/android-x86/*.so

#android.add_packaging_options = 

#android.add_resources = 

# android.add_src = java

android.api = 36

#android.ant_path = 

#android.apptheme = @android:style/Theme.NoTitleBar

android.archs = arm64-v8a, armeabi-v7a

#android.allow_backup = True

#android.backup_rules = 

#android.blacklist_src = 

#android.copy_libs = True

#android.debug_artifact = apk

#android.display_cutout = never

#android.enable_androidx = True

#android.entrypoint = org.kivy.android.PythonActivity

#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml

#android.extra_manifest_xml = ./src/android/extra_manifest.xml

#android.gradle_dependencies = 

#android.home_app = False

#android.library_references = 

#android.logcat_filters = *:S python:D

#android.logcat_pid_only = False

#android.manifest.intent_filters = 

#android.manifest.launch_mode = standard

#android.manifest.orientation = fullSensor

#android.manifest_placeholders = [:]

#android.meta_data = 

android.minapi = 24

#android.ndk = 25b

#android.ndk_api = 21

#android.ndk_path = 

android.no-byte-compile-python = True

#android.numeric_version = 1

#android.ouya.category = GAME

#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

android.permissions = android.permission.INTERNET,
                        android.permission.BLUETOOTH_CONNECT,
                        android.permission.BLUETOOTH_ADVERTISE, 
                        android.permission.BLUETOOTH_SCAN,
                        android.permission.BLUETOOTH,
# , (name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=18)

#android.presplash_color = #FFFFFF

#android.presplash_lottie = path/to/lottie/file.json

#android.release_artifact = aab

#android.res_xml = path/to/file.xml

#android.sdk = 20

#android.sdk_path = 

#android.service_class_name = org.kivy.android.PythonService

#android.skip_update = False

#android.uses_library = 

#android.wakelock = False

#android.whitelist = 

#android.whitelist_src = 

#icon.adaptive_background.filename = %(source.dir)s/data/icon_bg.png

#icon.adaptive_foreground.filename = %(source.dir)s/data/icon_fg.png

orientation = portrait

p4a.branch = develop

p4a.bootstrap = sdl3

#p4a.commit = HEAD


#p4a.fork = kivy

#p4a.hook = 

#p4a.local_recipes = 

#p4a.port = 

#p4a.setup_py = False

p4a.source_dir = /home/tdynamos/git/python-for-android/

#p4a.url = 

#services = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

#-----------------------------------------------------------------------------
#   Notes about using this file:
#
#   Buildozer uses a variant of Python's ConfigSpec to read this file.
#   For the basic syntax, including interpolations, see
#       https://docs.python.org/3/library/configparser.html#supported-ini-file-structure
#
#   Warning: Comments cannot be used "inline" - i.e.
#       [app]
#       title = My Application # This is not a comment, it is part of the title.
#
#   Warning: Indented text is treated as a multiline string - i.e.
#       [app]
#       title = My Application
#          package.name = myapp # This is all part of the title.
#
#   Buildozer's .spec files have some additional features:
#
#   Buildozer supports lists - i.e.
#       [app]
#       source.include_exts = py,png,jpg
#       #                     ^ This is a list.
#
#       [app:source.include_exts]
#       py
#       png
#       jpg
#       # ^ This is an alternative syntax for a list.
#
#   Buildozer's option names are case-sensitive, unlike most .ini files.
#
#   Buildozer supports overriding options through environment variables.
#   Name an environment variable as SECTION_OPTION to override a value in a .spec
#   file.
#
#   Buildozer support overriding options through profiles.
#   For example, you want to deploy a demo version of your application without
#   HD content. You could first change the title to add "(demo)" in the name
#   and extend the excluded directories to remove the HD content.
#
#       [app@demo]
#       title = My Application (demo)
#
#       [app:source.exclude_patterns@demo]
#       images/hd/*
#
#   Then, invoke the command line with the "demo" profile:
#
#        buildozer --profile demo android debug
#
#   Environment variable overrides have priority over profile overrides.
