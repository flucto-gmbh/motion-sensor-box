#!/usr/bin/env python3

import os
import sys
import subprocess

# thanks to https://stackoverflow.com/a/39499692
if os.geteuid() == 0:
    # print("We're root!")
    pass
else:
    # print("We're not root.")
    subprocess.call(["sudo", "python3", *sys.argv])
    sys.exit()  # do not continue after this as we already did the work in the subprocess

# check that all necessary files are where we expect them
base_path = os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")
)
print(base_path)
cfg_path = os.path.join(base_path, "cfg/")
hostname_path = os.path.join(cfg_path, "hostname")
hosts_path = os.path.join(cfg_path, "hosts")
rtunnel_path = os.path.join(cfg_path, "rtunnel.service")
wpa_config_path = os.path.join(cfg_path, "wpa_supplicant.conf")

for file_path in [hostname_path, hosts_path, rtunnel_path, wpa_config_path]:
    if not os.path.isfile(hostname_path):
        raise RuntimeError(f"Could not find file where I expect it: {file_path}")

print("Found all 4 local files.")

sd_card_path = input("Enter path to SD card: ")

rootfs_path = os.path.join(sd_card_path, "rootfs")
boot_path = os.path.join(sd_card_path, "boot")

if not os.path.exists(rootfs_path):
    raise RuntimeError(
        f"Could not find rootfs path where I expect it: {rootfs_path}. Did you mount it?"
    )
if not os.path.exists(boot_path):
    raise RuntimeError(
        f"Could not find boot path where I expect it: {boot_path}. Did you mount it?"
    )


# load files and insert msb_id as required
msb_id = int(input("Enter MSB ID: "))
if not 0 < msb_id <= 9999:
    raise ValueError("MSB ID has to be in 0-535.")

print("The files to create will be printed in the following:")
with open(hosts_path, "rt") as hosts_file:
    hosts_str = hosts_file.read()

hosts_str = hosts_str.replace("MSB-XXXX-A", f"MSB-{msb_id:04d}-A")

print("hosts:")
print(hosts_str)

with open(hostname_path, "rt") as hostname_file:
    hostname_str = hostname_file.read()

hostname_str = hostname_str.replace("MSB-XXXX-A", f"MSB-{msb_id:04d}-A")

print("hostname:")
print(hostname_str)

with open(rtunnel_path, "rt") as rtunnel_file:
    rtunnel_str = rtunnel_file.read()

rtunnel_str = rtunnel_str.replace("[REMOTE PORT]", f"{65000 + msb_id}")

print("rtunnel.service:")
print(rtunnel_str)

with open(wpa_config_path, "rt") as wpa_config_file:
    wpa_config_str = wpa_config_file.read()

print("wpa_supplicant.conf:")
print(wpa_config_str)


# create path for sd card files
sd_hosts_path = os.path.join(rootfs_path, "etc", os.path.basename(hosts_path))
sd_hostname_path = os.path.join(rootfs_path, "etc", os.path.basename(hostname_path))
sd_rtunnel_path = os.path.join(
    rootfs_path, "etc/systemd/system", os.path.basename(rtunnel_path)
)

sd_wpa_config_path = os.path.join(boot_path, os.path.basename(wpa_config_path))
sd_ssh_path = os.path.join(boot_path, "ssh")

# get user confirmation before proceeding.
print("The following files will be created:")
print(sd_hosts_path)
print(sd_hostname_path)
print(sd_rtunnel_path)
print(sd_wpa_config_path)
print(sd_ssh_path)
proceed = input("Proceed? [y/N] : ") or "N"
if not proceed.lower() == "y":
    print("Aborting.")
    sys.exit()

with open(sd_hosts_path, "wt") as sd_hosts_file:
    sd_hosts_file.write(hosts_str)

with open(sd_hostname_path, "wt") as sd_hostname_file:
    sd_hostname_file.write(hostname_str)

with open(sd_rtunnel_path, "wt") as sd_rtunnel_file:
    sd_rtunnel_file.write(rtunnel_str)

with open(sd_wpa_config_path, "wt") as sd_wpa_config_file:
    sd_wpa_config_file.write(wpa_config_str)

with open(sd_ssh_path, "wt") as sd_ssh_file:
    sd_ssh_file.write("")

print("Finished")
