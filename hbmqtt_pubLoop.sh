a=1
while(( 1 ))
do
    echo $a
    hbmqtt_pub --url "mqtt://192.168.49.199:12883" -t "ttest" -m "{'iter':"$a"}" &
    a=$[$a+1]

    sleep .1
done