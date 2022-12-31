import micropython

micropython.alloc_emergency_exception_buf(100)


def main():
    import os
    from sys import print_exception
    from esp32 import NVS, Partition

    nvs = NVS("pb4")

    p = Partition(Partition.RUNNING).info()[4]
    u = os.uname()

    print(f"boot.main: Booted MicroPython from '{p}'.")
    print(f"boot.main: {u.version}; {u.machine}")

    try:
        vfs_config = nvs.get_i32("vfs_config")
        vfs_label = "app_1" if vfs_config else "app_0"
    except OSError as e:
        if e.errno != -4354:  # ESP_ERR_NVS_NOT_FOUND
            raise
        print(f"boot.main: VFS config not found.")
        vfs_label = "vfs"
    print(f"boot.main: Booting app from '{vfs_label}'...")

    os.umount("/")

    def get_fallback(vfs_label):
        if vfs_label == "app_1":
            return "app_0"
        elif vfs_label == "app_0":
            return "vfs"

    while vfs_label:
        vfs_fallback = get_fallback(vfs_label)
        vfs_partitions = Partition.find(Partition.TYPE_DATA, label=vfs_label)

        if len(vfs_partitions) == 0:
            print(f"boot.main: Could not find '{vfs_label}'!")
            if vfs_fallback:
                print(f"boot.main: Falling back to '{vfs_fallback}'...")
            vfs_label = vfs_fallback
            continue

        try:
            os.mount(vfs_partitions[0], "/")
        except OSError as e:  # TODO: Cast a smaller net
            print_exception(e)
            print(f"boot.main: Could not mount '{vfs_label}'!")
            if vfs_fallback:
                print(f"boot.main: Falling back to '{vfs_fallback}'...")
            vfs_label = vfs_fallback
            continue

        try:
            from version import NAME, VERSION

            print(f"boot.main: Loaded {NAME} v{VERSION}.")
        except ImportError as e:
            print(f"boot.main: {e}")
            print("boot.main: Loaded unidentified app.")

        return

    raise Exception("boot.main: No more partitions to fall back to!")


main()
