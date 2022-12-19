import micropython
micropython.alloc_emergency_exception_buf(100)


def get_fallback(vfs_label):
    if vfs_label == "app_1":
        return "app_0"
    elif vfs_label == "app_0":
        return "vfs"


def main():
    import os
    from esp32 import NVS, Partition

    nvs = NVS("pb4")

    part_label = Partition(Partition.RUNNING).info()[4]
    print(f"boot.main: Booted MicroPython from '{part_label}'.")

    try:
        vfs_config = nvs.get_i32("vfs_config")
        vfs_label = "app_1" if vfs_config else "app_0"
    except OSError:
        vfs_label = 'vfs'
    print(f"boot.main: Booting app from '{vfs_label}'...")

    os.umount('/')

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
            os.mount(vfs_partitions[0], '/')
        except OSError as e:
            print(f"boot.main: Could not mount '{vfs_label}'! {e}")
            if vfs_fallback:
                print(f"boot.main: Falling back to '{vfs_fallback}'...")
            vfs_label = vfs_fallback
            continue

        return

    raise Exception("boot.main: No more partitions to fall back to!")


main()
