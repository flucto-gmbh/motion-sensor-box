import re
import subprocess
import time

# Unit properties as defined in the man pages
# see e.g. https://www.man7.org/linux/man-pages/man5/org.freedesktop.systemd1.5.html
#
# Id contains the primary name of the unit.
#
# Description contains the human readable description string for
#        the unit.
#
# LoadState contains a state value that reflects whether the
#        configuration file of this unit has been loaded. The following
#        states are currently defined: "loaded", "error", and "masked".
#        "loaded" indicates that the configuration was successfully
#        loaded.  "error" indicates that the configuration failed to load.
#        The LoadError field (see below) contains information about the
#        cause of this failure.  "masked" indicates that the unit is
#        currently masked out (i.e. symlinked to /dev/null or empty). Note
#        that the LoadState is fully orthogonal to the ActiveState (see
#        below) as units without valid loaded configuration might be
#        active (because configuration might have been reloaded at a time
#        where a unit was already active).
#
# ActiveState contains a state value that reflects whether the unit
#        is currently active or not. The following states are currently
#        defined: "active", "reloading", "inactive", "failed",
#        "activating", and "deactivating".  "active" indicates that unit
#        is active (obviously...).  "reloading" indicates that the unit is
#        active and currently reloading its configuration.  "inactive"
#        indicates that it is inactive and the previous run was successful
#        or no previous run has taken place yet.  "failed" indicates that
#        it is inactive and the previous run was not successful (more
#        information about the reason for this is available on the unit
#        type specific interfaces, for example for services in the Result
#        property, see below).  "activating" indicates that the unit has
#        previously been inactive but is currently in the process of
#        entering an active state. Conversely "deactivating" indicates
#        that the unit is currently in the process of deactivation.
#
# SubState encodes states of the same state machine that
#        ActiveState covers, but knows more fine-grained states that are
#        unit-type-specific. Where ActiveState only covers six high-level
#        states, SubState covers possibly many more low-level
#        unit-type-specific states that are mapped to the six high-level
#        states. Note that multiple low-level states might map to the same
#        high-level state, but not vice versa. Not all high-level states
#        have low-level counterparts on all unit types. At this point the
#        low-level states are not documented here, and are more likely to
#        be extended later on than the common high-level states explained
#        above.
#
# UnitFileState encodes the install state of the unit file of
#        FragmentPath. It currently knows the following states: "enabled",
#        "enabled-runtime", "linked", "linked-runtime", "masked",
#        "masked-runtime", "static", "disabled", and "invalid".  "enabled"
#        indicates that a unit file is permanently enabled.
#        "enable-runtime" indicates the unit file is only temporarily
#        enabled and will no longer be enabled after a reboot (that means,
#        it is enabled via /run/ symlinks, rather than /etc/).  "linked"
#        indicates that a unit is linked into /etc/ permanently.
#        "linked-runtime" indicates that a unit is linked into /run/
#        temporarily (until the next reboot).  "masked" indicates that the
#        unit file is masked permanently.  "masked-runtime" indicates that
#        it is masked in /run/ temporarily (until the next reboot).
#        "static" indicates that the unit is statically enabled, i.e.
#        always enabled and doesn't need to be enabled explicitly.
#        "invalid" indicates that it could not be determined whether the
#        unit file is enabled.


class SystemdStatusParser:
    # _name_desc_pattern = re.compile(r"^(msb-\w*\.service)\s-\s([\w\s]*)")
    # _loaded_enabled_pattern = re.compile(
    #     r"^Loaded:\s(loaded)\s\(/etc/systemd/system/msb-\w+\.service;\s(\w*);"
    # )
    # _active_pattern = re.compile(r"^Active:\s(\w*\s\(\w*\))")

    msb_services = []
    time_of_last_unit_update = 0
    seconds_between_unit_updates = 600

    unit_properties = [
        # Id always has to be first in this list
        # When parsing output of systemctl it is used to mark the beginning of the next unit.
        "Id",
        "Description",
        "LoadState",
        "ActiveState",
        "SubState",
        "UnitFileState",
    ]

    property_pattern = re.compile(r"^(\w+)=(.+)$", re.MULTILINE)

    def check_unit_files(self):
        if (
            time.monotonic() - self.time_of_last_unit_update
            > self.seconds_between_unit_updates
        ):
            self.update_unit_files()

    def update_unit_files(self):
        completed_process = subprocess.run(
            ["systemctl", "list-unit-files", "msb-*"],
            capture_output=True,
            encoding="utf-8",
        )
        answer = completed_process.stdout
        lines = (s.strip() for s in answer.split("\n") if s.strip().startswith("msb-"))
        self.msb_services = [l.split()[0] for l in lines]
        self.time_of_last_unit_update = time.monotonic()

    def __call__(self, *args, **kwargs):
        self.check_unit_files()

        completed_process = subprocess.run(
            [
                "systemctl",
                "show",
                *self.msb_services,
                "--property=" + ",".join(self.unit_properties),
            ],
            capture_output=True,
            encoding="utf-8",
        )
        answer = completed_process.stdout
        matches = self.property_pattern.findall(answer)
        assert len(matches) == len(self.msb_services) * len(self.unit_properties)
        status = {}
        current_id = ""
        for match in matches:
            if match[0] == "Id":
                current_id = match[1]
                status[current_id] = {}
                continue
            status[current_id][match[0]] = match[1]

        return status
