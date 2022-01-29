#!/bin/bash
# Artikel, der genau das Vorhaben beschreibt: https://ops.tips/blog/using-network-namespaces-and-bridge-to-isolate-servers/
# Artikel über Netzwerk-Brücke: https://wiki.archlinux.org/title/Network_bridge
CLEAR_COLOUR="\033[0m"
B_RED="\033[1;31m"
GREEN="\033[0;32m"

# Orientierung
echo -e "${B_RED}[Verzögerung 120ms; Datenrate 500MB; Datenverlust 1%]${CLEAR_COLOUR}"

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
ip netns exec namespace2 ip addr add 10.0.0.3/24 dev veth2

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

# Weise Brücke IP-Adresse hinzu.
ip addr add 10.0.0.2/24 brd + dev br1

# Round-Trip-Time messen
echo -e "${GREEN}[Round-Trip-Time messen]${CLEAR_COLOUR}"
ip netns exec namespace1 ping -I veth1 -c3 10.0.0.3
ip netns exec namespace2 ping -I veth2 -c3 10.0.0.1

# Netzwerk-Manipulation
ip netns exec namespace1 tc qdisc add dev veth1 root netem delay 120ms
ip netns exec namespace1 tc qdisc add dev veth1 root netem rate 500mbit
ip netns exec namespace1 tc qdisc add dev veth1 root netem loss 1%

ip netns exec namespace2 tc qdisc add dev veth1 root netem delay 120ms
ip netns exec namespace2 tc qdisc add dev veth1 root netem rate 500mbit
ip netns exec namespace2 tc qdisc add dev veth1 root netem loss 1%

# Round-Trip-Time erneut messen unter Netzwerkmanipulation
echo -e "${GREEN}[Round-Trip-Time erneut messen unter Netzwerkmanipulation]${CLEAR_COLOUR}"
ip netns exec namespace1 ping -I veth1 -c3 10.0.0.3
ip netns exec namespace2 ping -I veth2 -c3 10.0.0.1

# sockperf nutzen
echo -e "${GREEN}[sockperf-Test]${CLEAR_COLOUR}"
tmux kill-session -t sockperf-server
tmux new-session -s sockperf-server -d "ip netns exec namespace1 sockperf server --tcp"
ip netns exec namespace2 sockperf ping-pong --tcp -i 10.0.0.1

# iperf nutzen
echo -e "${GREEN}[iperf-Test]${CLEAR_COLOUR}"
tmux kill-session -t iperf-server
tmux new-session -s iperf-server -d "ip netns exec namespace1 iperf -s"
ip netns exec namespace2 iperf -c 10.0.0.1

# In Ursprungszustand versetzen
## Künstliche Netzwerkmanipulation von netem entfernen
ip netns exec namespace1 tc qdisc del dev veth1 root
ip netns exec namespace2 tc qdisc del dev veth1 root
