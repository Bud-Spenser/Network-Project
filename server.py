import socket
import time
import statistics

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(("", 50000))
    
    print("Server running...")

    PACKET_COUNT= 0
    sequence_list = []
    dt = time.time()
    t_end = dt + 60

    #####################STATS VARIABLES#########################

    #set up a latency List to calculate the mean of the latencys during an interval
    latency_list = []
    ### interval in which the stats are printed in seconds
    stats_interval = 5
    #variables for lost and interval packet measurement
    old_packet_count = 0
    old_packet_lost = 0

    ##################### Looking for packages - main loop ##########################

    while True:

        #ends with end of time
        if time.time() > t_end:
            print(len(sequence_list))
            exit(0)
        # message is a tuple
        daten, addr = s.recvfrom(1024)
        
        # received message is the sequence number formatted as a byte string
        counter = int.from_bytes(daten, byteorder="big")

        #add the sequence number to a sequence list
        sequence_list.append(counter)
        # add received packet to packet counter
        PACKET_COUNT += 1


        ############################ STATS ################################

        ####### start measuring time for the stats ###########
        if PACKET_COUNT == 1:
            start_time = time.time()
        #### latency can only be calculated if at least two frames are sent ####
        if PACKET_COUNT > 1 :
            latency_list.append(time.time() - time_last_frame)

        ##### Variable for latency calculation
        time_last_frame = time.time()

        #### print every definded interval the stats
        if time.time() > (start_time + stats_interval):
            
            interval_packets = PACKET_COUNT - old_packet_count
            old_packet_count = PACKET_COUNT

            ###Throughput in kb/s
            throughput = round((1024 * 0.001 * interval_packets / (time.time()-start_time)),2)

            #### only take the mean of the packets send within the interval

            latency = statistics.mean(latency_list[-interval_packets:])
            ###lost frames... letzte Zahl aus sequencelist[], vergleich mit Packet_Count
            interval_lost = sequence_list[-1] - PACKET_COUNT - old_packet_lost
            old_packet_lost = sequence_list[-1] - PACKET_COUNT
            
            #### lost packages during stats_interval in percent
            lost_percent = round(interval_lost/interval_packets*100,2)
            
            interval = time.time()-start_time
            #new start time for the real interval
            start_time = time.time()
            
            print("Latenz zwischen den Frames: {}s\nDatenrate: {} kb/s\nVerlorene Frames: {}% ".format(latency, throughput,lost_percent))
            
            

    
################ to do : check sequence list for missing packages
######## timeout server ...
####Problem : innerhalb der While Schleife muss ein Paket ankommen, damit die stats geprinted werden..
        