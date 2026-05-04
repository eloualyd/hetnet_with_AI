# ============================================
# scenario_baseline.tcl - HetNet SANS IA
# Baseline : toutes les stations toujours ON
# ============================================

set ns   [new Simulator]
# FIX B21: dynamic path relative to this script
set BASE [file dirname [file dirname [info script]]]

set tracefile [open "$BASE/results/baseline_trace.tr" w]
$ns trace-all $tracefile

set namfile [open "$BASE/results/scenario_baseline.nam" w]
$ns namtrace-all $namfile

# ---- Parametres reseau ----
set num_small_cells 2
set num_users       25
set sim_time        50.0

# ---- Noeuds : 1 Macro + 2 Small Cells + 25 Users ----
set macro [$ns node]
set sc(0) [$ns node]
set sc(1) [$ns node]

for {set i 0} {$i < $num_users} {incr i} {
    set user($i) [$ns node]
}

$macro color red
$sc(0) color blue
$sc(1) color blue
for {set i 0} {$i < $num_users} {incr i} {
    $user($i) color green
}
$ns color 1 red

# ---- Liens Macro -> Small Cells ----
$ns duplex-link $macro $sc(0) 10Mb 5ms DropTail
$ns duplex-link $macro $sc(1) 10Mb 5ms DropTail

# ---- Liens Small Cells -> Users ----
for {set i 0} {$i < $num_users} {incr i} {
    set cell_id [expr {$i % $num_small_cells}]
    $ns duplex-link $sc($cell_id) $user($i) 2Mb 2ms DropTail
}

# ---- Energie : baseline = stations toujours ON ----
set energy_macro 130.0
set energy_small  10.0
set total_energy  [expr {$energy_macro + $num_small_cells * $energy_small}]
puts "BASELINE energy_total: $total_energy W (constant)"

# ---- Trafic UDP ----
for {set i 0} {$i < $num_users} {incr i} {
    set udp($i)  [new Agent/UDP]
    set null($i) [new Agent/Null]
    $ns attach-agent $user($i) $udp($i)
    $ns attach-agent $macro    $null($i)
    $ns connect $udp($i) $null($i)
    $udp($i) set fid_ 1

    set cbr($i) [new Application/Traffic/CBR]
    $cbr($i) set packetSize_ 512
    $cbr($i) set rate_       64Kb
    $cbr($i) attach-agent $udp($i)

    $ns at 1.0 "$cbr($i) start"
    $ns at [expr {$sim_time - 1}] "$cbr($i) stop"
}

$ns at $sim_time "finish"

proc finish {} {
    global ns tracefile namfile
    $ns flush-trace
    close $tracefile
    close $namfile
    puts "BASELINE simulation terminee."
    exit 0
}

$ns run
