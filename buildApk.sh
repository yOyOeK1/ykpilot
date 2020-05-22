app="ykpilot"
echo "building "$app
rm -rf /tmp/$app
mkdir /tmp/$app
cp -rv ./ /tmp/$app/
cd /tmp
rm -r /tmp/$app/playground
for i in `find /tmp/$app/ | grep pyo`; do rm $i; done
rm /tmp/$app/backup.sh
rm /tmp/$app/buildApk.sh
rm /tmp/$app/*.ini
rm /tmp/$app/*.db
rm /tmp/$app/wRadar_*.gif
rm /tmp/$app/*.*~
rm -rf /tmp/$app/.git
rm -r /tmp/$app/__pycache__
rm /tmp/$app/ykpilot.config
rm -r /tmp/$app/.settings
rm -r /tmp/$app/.project
rm -r /tmp/$app/.pydevproject

echo "clean done -------------------"


echo "-----------------------------"
echo "call"
ver=`date +%y%m%d`
p4a_build.sh $ver $app /tmp/$app /home/yoyo/Apps/ykpilot/ico_sailboat_256_256.png
adb install  "/home/yoyo/.local/share/python-for-android/dists/API26_r21_3__armeabi-v7a/bin/$app-0."$ver"-debug.apk"