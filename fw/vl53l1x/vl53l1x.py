def test(dev):
    while not boot_state(0x29):
        print("1", end="", flush=True)
    print()

    sensor_init(0x29)
    start_ranging(0x29)

    while True:
        while not check_for_data_ready(0x29):
            print("2", end="", flush=True)
        print()

        print(get_range_status(0x29))
        print(get_distance(0x29))

        clear_interrupt(0x29)
