#!/bin/bash

echo "retrieving service status"

for service_path in /etc/systemd/system/multi-user.target.wants/msb-*.service
do
	service=$(basename $service_path)
        echo "status of $service"
        sudo systemctl status $service
        echo ""
        echo ""
done

