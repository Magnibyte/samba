#!/bin/sh

. "${TEST_SCRIPTS_DIR}/unit.sh"

define_test "Memory check, bad situation, custom memory critical"

setup

setup_script_options <<EOF
CTDB_MONITOR_MEMORY_USAGE=":85"
EOF

set_mem_usage 90 0
required_result 1 <<EOF
ERROR: System memory utilization 90% >= threshold 85%
$FAKE_PROC_MEMINFO
$(ps foobar)
EOF

simple_test
