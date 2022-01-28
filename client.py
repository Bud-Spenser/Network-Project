import socket
import time

# Set up socket
s: socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# IP of the receiver
ip = input("IP-Adresse: ")

#### set send rate per second
#sendRateBytesPerSecond = 1024 * 1000

### set runtime in s
#run_time = 2
#time.time() returns actual time in seconds
#t_end = time.time() + run_time 

### calculate total nr of packets
#total_packets = (sendRateBytesPerSecond/1024) * run_time

#### use a counter for sequencing
counter = 0

#while time.time() < t_end:
#### send 120 MB , then stop for 0.48 secs - repeat 30 times
for o in range(30):
    for i in range(120000):

        now = time.time()

        ### create data of 1024 bytes with the counter as Input
        data = counter.to_bytes(1024, byteorder="big")
        #send the data to receiver
        s.sendto(data, (ip, 50000))
        counter += 1

    time.sleep(0.48)

#### Ausbreitungsverzögerung = 35786 km /300000 km/s = 0.12 s
#### 0.24 s bis zum anderen Empfänger auf der Erden
#### Datenrate = 500 Mb/s
#### Delay = 0.24 s
#### datarate / delay produkt =  120 Mb 

# Ich kann 120 MB auf den Kanal legen, um den Kanal effizient zu nutzen, dann kommen die ersten Pakete an (Überprüfung, ob Pakete vollständig sind, NACK's schicken..)
# nach 0.48 s sind erst alle Daten vollständig eingetroffen
# danach sendet nach Möglichkeit der Empfänger einen Bloom Filter zurück mit nicht empfangegen Frames, um den Kanal nicht zu belasten
