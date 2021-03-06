#!/bin/bash

test_info()
{
    cat <<EOF
Check that CTDB operated correctly if there are 0 event scripts

This test only does anything with local daemons.  On a real cluster it
has no way of updating configuration.
EOF
}

. "${TEST_SCRIPTS_DIR}/integration.bash"

set -e

if [ -z "$TEST_LOCAL_DAEMONS" ] ; then
	echo "SKIPPING this test - only runs against local daemons"
	exit 0
fi

ctdb_test_init --no-event_scripts

cluster_is_healthy

echo "Good, that seems to work!"
