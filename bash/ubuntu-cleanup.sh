#!/bin/bash

# Ubuntu System Cleanup Script
# This script should be run with sudo privileges

# Function to print section headers
print_header() {
    echo "======================================"
    echo "$1"
    echo "======================================"
}

# Check if script is run with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo privileges"
    exit 1
fi

# Clean apt cache
clean_apt_cache() {
    print_header "Cleaning APT Cache"
    apt-get clean
    apt-get autoclean
    echo "APT cache cleaned"
}

# Remove unused packages
remove_unused_packages() {
    print_header "Removing Unused Packages"
    apt-get autoremove -y
    echo "Unused packages removed"
}

# Clear systemd journal logs
clear_journal_logs() {
    print_header "Clearing Systemd Journal Logs"
    journalctl --vacuum-time=7d
    echo "Journal logs older than 7 days cleared"
}

# Clean thumbnail cache
clean_thumbnail_cache() {
    print_header "Cleaning Thumbnail Cache"
    rm -rf /home/*/.cache/thumbnails/*
    rm -rf /root/.cache/thumbnails/*
    echo "Thumbnail cache cleaned"
}

# Clean temp files
clean_temp_files() {
    print_header "Cleaning Temporary Files"
    rm -rf /tmp/*
    rm -rf /var/tmp/*
    echo "Temporary files cleaned"
}

# Clean old kernels (keeping the current and one previous version)
clean_old_kernels() {
    print_header "Cleaning Old Kernels"
    dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r | sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d' | xargs apt-get -y purge
    echo "Old kernels cleaned"
}

# Clean bash history
clean_bash_history() {
    print_header "Cleaning Bash History"
    history -c
    > ~/.bash_history
    echo "Bash history cleaned"
}

# Main execution
print_header "Starting System Cleanup"
echo "Current disk usage:"
df -h

# Execute all cleanup functions
clean_apt_cache
remove_unused_packages
clear_journal_logs
clean_thumbnail_cache
clean_temp_files
clean_old_kernels
clean_bash_history

# Show disk usage after cleanup
print_header "Cleanup Complete"
echo "Updated disk usage:"
df -h

echo "System cleanup completed successfully!"
