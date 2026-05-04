BEGIN {
    sent = 0;
    received = 0;
}

{
    if ($1 == "+") sent++;
    if ($1 == "r") received++;
}

END {
    loss = sent - received;
    rate = (sent > 0) ? (loss / sent) * 100 : 0;

    print "Sent:", sent;
    print "Received:", received;
    print "Packet Loss:", loss;
    print "Loss Rate (%):", rate;
}
