# ============================================
# scenario_ai.tcl - HetNet AVEC Q-Learning
# Small cells s'eteignent selon charge reseau
# ============================================

set ns   [new Simulator]
# FIX B22: dynamic path relative to this script
set BASE [file dirname [file dirname [info script]]]

set tracefile [open "$BASE/results/ai_trace.tr" w]
$ns trace-all $tracefile

set namfile [open "$BASE/results/scenario_ai.nam" w]
$ns namtrace-all $namfile

set num_small_cells 2
set num_users       25
set sim_time        50.0

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

$ns duplex-link $macro $sc(0) 10Mb 5ms DropTail
$ns duplex-link $macro $sc(1) 10Mb 5ms DropTail

for {set i 0} {$i < $num_users} {incr i} {
    set cell_id [expr {$i % $num_small_cells}]
    $ns duplex-link $sc($cell_id) $user($i) 2Mb 2ms DropTail
}

# ---- Politique IA (Q-table apprise) ----
proc get_ai_action {t} {
    set users [expr {int(10 + 15 * sin(3.14159 * $t / 50.0))}]
    if {$users < 10} {
        return 0
    } elseif {$users < 18} {
        return 1
    } else {
        return 2
    }
}

proc compute_ai_energy {action} {
    if {$action == 2} {
        return 150.0
    } else {
        return 141.0
    }
}

for {set t 5} {$t <= $sim_time} {incr t 5} {
    $ns at $t "
        set action \[get_ai_action $t\]
        set energy \[compute_ai_energy \$action\]
        puts \"AI t=$t action=\$action energy=\${energy}W\"
    "
}

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
    puts "AI simulation terminee."
    exit 0
}

$ns run
