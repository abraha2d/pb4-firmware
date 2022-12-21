// Include the header file to get access to the MicroPython API
#include "py/dynruntime.h"

#include "VL53L1X_api.h"

STATIC mp_obj_t get_sw_version() {
    VL53L1X_Version_t version;
    VL53L1X_GetSWVersion(&version);
    mp_obj_t items[4] = {
            mp_obj_new_int(version.major),
            mp_obj_new_int(version.minor),
            mp_obj_new_int(version.build),
            mp_obj_new_int(version.revision),
    };
    mp_obj_t version_obj = mp_obj_new_tuple(4, items);
    return version_obj;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(get_sw_version_obj, get_sw_version);

STATIC mp_obj_t set_i2c_address(mp_obj_t dev_obj, mp_obj_t new_address_obj) {
    int dev = mp_obj_get_int(dev_obj);
    int new_address = mp_obj_get_int(new_address_obj);
    VL53L1X_SetI2CAddress(dev, new_address);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_i2c_address_obj, set_i2c_address);

STATIC mp_obj_t sensor_init(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "sensor_init dev=%d\n", dev);
    VL53L1X_SensorInit(dev);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(sensor_init_obj, sensor_init);

STATIC mp_obj_t clear_interrupt(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "clear_interrupt dev=%d\n", dev);
    VL53L1X_ClearInterrupt(dev);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(clear_interrupt_obj, clear_interrupt);

STATIC mp_obj_t start_ranging(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "start_ranging dev=%d\n", dev);
    VL53L1X_StartRanging(dev);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(start_ranging_obj, start_ranging);

STATIC mp_obj_t stop_ranging(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "stop_ranging dev=%d\n", dev);
    VL53L1X_StopRanging(dev);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(stop_ranging_obj, stop_ranging);

STATIC mp_obj_t check_for_data_ready(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "check_for_data_ready dev=%d\n", dev);
    uint8_t is_data_ready;
    VL53L1X_CheckForDataReady(dev, &is_data_ready);
    mp_printf(&mp_plat_print, "check_for_data_ready dev=%d return=%u\n", dev, is_data_ready);
    return mp_obj_new_int(is_data_ready);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(check_for_data_ready_obj, check_for_data_ready);

STATIC mp_obj_t boot_state(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "boot_state dev=%d\n", dev);
    uint8_t state;
    VL53L1X_BootState(dev, &state);
    mp_printf(&mp_plat_print, "boot_state dev=%d return=%u\n", dev, state);
    return mp_obj_new_int(state);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(boot_state_obj, boot_state);

STATIC mp_obj_t get_sensor_id(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "get_sensor_id dev=%d\n", dev);
    uint16_t sensor_id;
    VL53L1X_GetSensorId(dev, &sensor_id);
    mp_printf(&mp_plat_print, "get_sensor_id dev=%d return=%u\n", dev, sensor_id);
    return mp_obj_new_int(sensor_id);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(get_sensor_id_obj, get_sensor_id);

STATIC mp_obj_t get_distance(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "get_distance dev=%d\n", dev);
    uint16_t distance;
    VL53L1X_GetDistance(dev, &distance);
    mp_printf(&mp_plat_print, "get_distance dev=%d return=%u\n", dev, distance);
    return mp_obj_new_int(distance);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(get_distance_obj, get_distance);

STATIC mp_obj_t get_range_status(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "get_range_status dev=%d\n", dev);
    uint8_t range_status;
    VL53L1X_GetRangeStatus(dev, &range_status);
    mp_printf(&mp_plat_print, "get_range_status dev=%d return=%u\n", dev, range_status);
    return mp_obj_new_int(range_status);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(get_range_status_obj, get_range_status);

STATIC mp_obj_t get_result(mp_obj_t dev_obj) {
    int dev = mp_obj_get_int(dev_obj);
    mp_printf(&mp_plat_print, "get_result dev=%d\n", dev);
    VL53L1X_Result_t result;
    VL53L1X_GetResult(dev, &result);
    mp_printf(&mp_plat_print, "get_result dev=%d return={\n", dev);
    mp_printf(&mp_plat_print, "  Status:       %u,\n", result.Status);
    mp_printf(&mp_plat_print, "  Distance:     %u,\n", result.Distance);
    mp_printf(&mp_plat_print, "  Ambient:      %u,\n", result.Ambient);
    mp_printf(&mp_plat_print, "  SigPerSPAD:   %u,\n", result.SigPerSPAD);
    mp_printf(&mp_plat_print, "  NumSPADs:     %u,\n", result.NumSPADs);
    mp_printf(&mp_plat_print, "};\n");
    mp_obj_t result_obj = mp_obj_new_dict(5);
    mp_obj_dict_store(result_obj, MP_OBJ_NEW_QSTR(MP_QSTR_status), mp_obj_new_int(result.Status));
    mp_obj_dict_store(result_obj, MP_OBJ_NEW_QSTR(MP_QSTR_distance), mp_obj_new_int(result.Distance));
    mp_obj_dict_store(result_obj, MP_OBJ_NEW_QSTR(MP_QSTR_ambient), mp_obj_new_int(result.Ambient));
    mp_obj_dict_store(result_obj, MP_OBJ_NEW_QSTR(MP_QSTR_sig_per_spad), mp_obj_new_int(result.SigPerSPAD));
    mp_obj_dict_store(result_obj, MP_OBJ_NEW_QSTR(MP_QSTR_num_spads), mp_obj_new_int(result.NumSPADs));
    return result_obj;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(get_result_obj, get_result);

// This is the entry point and is called when the module is imported
mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args) {
    // This must be first, it sets up the globals dict and other things
    MP_DYNRUNTIME_INIT_ENTRY

    // Make the function available in the module's namespace
    mp_store_global(MP_QSTR_get_sw_version, MP_OBJ_FROM_PTR(&get_sw_version_obj));
    mp_store_global(MP_QSTR_set_i2c_address, MP_OBJ_FROM_PTR(&set_i2c_address_obj));
    mp_store_global(MP_QSTR_sensor_init, MP_OBJ_FROM_PTR(&sensor_init_obj));
    mp_store_global(MP_QSTR_clear_interrupt, MP_OBJ_FROM_PTR(&clear_interrupt_obj));
    mp_store_global(MP_QSTR_start_ranging, MP_OBJ_FROM_PTR(&start_ranging_obj));
    mp_store_global(MP_QSTR_stop_ranging, MP_OBJ_FROM_PTR(&stop_ranging_obj));
    mp_store_global(MP_QSTR_check_for_data_ready, MP_OBJ_FROM_PTR(&check_for_data_ready_obj));
    mp_store_global(MP_QSTR_boot_state, MP_OBJ_FROM_PTR(&boot_state_obj));
    mp_store_global(MP_QSTR_get_sensor_id, MP_OBJ_FROM_PTR(&get_sensor_id_obj));
    mp_store_global(MP_QSTR_get_distance, MP_OBJ_FROM_PTR(&get_distance_obj));
    mp_store_global(MP_QSTR_get_range_status, MP_OBJ_FROM_PTR(&get_range_status_obj));
    mp_store_global(MP_QSTR_get_result, MP_OBJ_FROM_PTR(&get_result_obj));

    // This must be last, it restores the globals dict
    MP_DYNRUNTIME_INIT_EXIT
}
