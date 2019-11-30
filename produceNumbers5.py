#!/usr/bin/python3
# -*- coding: ascii -*-
# Generated at 30/11/2019 15:46:18
# 



def main():
    from time import sleep
    from json import dumps
    from kafka import KafkaProducer
    p = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: dumps(x).encode('utf-8'))
    i = 1
    t='numtest'
    while i < 5:
        p.send(t, value={'n5' : i})
        i+=1
        sleep(5)


if __name__ == "__main__":
    main()
