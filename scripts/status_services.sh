#!/bin/bash

echo "stopping all services"

for service in /etc/systemd/system/multi-user.target.wants/msb-*.service
do
        echo "status of $service"
        sudo systemctl status $service
        echo ""
        echo ""
done

