# parse_ee.awk - Extraction métriques énergie depuis trace NS2
BEGIN {
    sent=0; received=0; dropped=0;
    print "=== ANALYSE TRACE NS2 ==="
}
{
    event = $1
    if (event == "+") sent++
    if (event == "r") received++
    if (event == "d") dropped++
}
END {
    pdr = (sent > 0) ? (received/sent*100) : 0
    print "Paquets envoyes  : " sent
    print "Paquets recus    : " received
    print "Paquets perdus   : " dropped
    printf "PDR              : %.2f%%\n", pdr
}
