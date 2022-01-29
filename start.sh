#!/bin/bash
# Artikel, der genau, das Vorhaben beschreibt: https://ops.tips/blog/using-network-namespaces-and-bridge-to-isolate-servers/
# Artikel über Netzwerk-Brücke: https://wiki.archlinux.org/title/Network_bridge
CLEAR_COLOUR="\033[0m"
B_RED="\033[1;31m"
GREEN="\033[0;32m"

# Iterationen
# 0: Verzögerung 60ms
# 1: Datenrate 100kbit
# 2: Verzögerung mit Jitter 70ms 80ms
# 3: Datenverlust 50%

for j in {0..3}
do
    # Orientierung
    if [[ "${j}" == 0 ]]; then
        echo -e "${B_RED}[Verzögerung 60ms]${CLEAR_COLOUR}"
    elif [[ "${j}" == 1 ]]; then
        echo -e "${B_RED}[Datenrate 100kbit]${CLEAR_COLOUR}"
    elif [[ "${j}" == 2 ]]; then
        echo -e "${B_RED}[Verzögerung mit Jitter 70ms 80ms]${CLEAR_COLOUR}"
    elif [[ "${j}" == 3 ]]; then
        echo -e "${B_RED}[Datenverlust 50%]${CLEAR_COLOUR}"
    fi

    # Zwei Netzwerk-Namensbereiche erstellen
    ip netns add namespace1
    ip netns add namespace2

    # Erstelle Paare.
    ip link add veth1 type veth peer name br-veth1
    ip link add veth2 type veth peer name br-veth2

    # Weise veths den Namesbereichen zu.
    ip link set veth1 netns namespace1
    ip link set veth2 netns namespace2

    # IP-Adressen hinzufügen
    ip netns exec namespace1 ip addr add 10.0.0.1/24 dev veth1
    ip netns exec namespace2 ip addr add 10.0.0.2/24 dev veth2

    # Erstelle die Brücke und fahre hoch.
    ip link add name br1 type bridge
    ip link set br1 up

    # Fahre veths der Brücke hoch.
    ip link set br-veth1 up
    ip link set br-veth2 up

    # Fahre veths der Namensbereiche hoch.
    ip netns exec namespace1 ip link set dev veth1 up
    ip netns exec namespace2 ip link set dev veth2 up

    # Weise veths der Brücke zu.
    ip link set br-veth1 master br1
    ip link set br-veth2 master br1

    # Round-Trip-Time messen
    echo -e "${GREEN}[Round-Trip-Time messen]${CLEAR_COLOUR}"
    ip netns exec net1 ping -I veth1 -c3 10.0.0.2
    ip netns exec net2 ping -I veth2 -c3 10.0.0.1

    # Netzwerk-Manipulation
    if [[ "${j}" == 0 ]]; then
        ip netns exec net1 tc qdisc add dev veth1 root netem delay 60ms
    elif [[ "${j}" == 1 ]]; then
        ip netns exec net1 tc qdisc add dev veth1 root netem rate 100kbit
    elif [[ "${j}" == 2 ]]; then
        ip netns exec net1 tc qdisc add dev veth1 root netem delay 70ms 80ms
    elif [[ "${j}" == 3 ]]; then
        ip netns exec net1 tc qdisc add dev veth1 root netem loss 50%
    fi

    # Round-Trip-Time erneut messen unter Netzwerkmanipulation
    echo -e "${GREEN}[Round-Trip-Time erneut messen unter Netzwerkmanipulation]${CLEAR_COLOUR}"
    ip netns exec net1 ping -I veth1 -c3 10.0.0.2
    ip netns exec net2 ping -I veth2 -c3 10.0.0.1

    # sockperf nutzen
    echo -e "${GREEN}[sockperf-Test]${CLEAR_COLOUR}"
    tmux kill-session -t sockperf-server
    tmux new-session -s sockperf-server -d "ip netns exec net1 sockperf server --tcp"
    ip netns exec net2 sockperf ping-pong --tcp -i 10.0.0.1

    # iperf nutzen
    echo -e "${GREEN}[iperf-Test]${CLEAR_COLOUR}"
    tmux kill-session -t iperf-server
    tmux new-session -s iperf-server -d "ip netns exec net1 iperf -s"
    ip netns exec net2 iperf -c 10.0.0.1

    # In Ursprungszustand versetzen
    ## Künstliche Netzwerkmanipulation von netem entfernen
    ip netns exec net1 tc qdisc del dev veth1 root
done
