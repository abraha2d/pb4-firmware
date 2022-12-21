/*
* This file is part of VL53L1 Platform 
* 
* Copyright (c) 2016, STMicroelectronics - All Rights Reserved 
* 
* License terms: BSD 3-clause "New" or "Revised" License. 
* 
* Redistribution and use in source and binary forms, with or without 
* modification, are permitted provided that the following conditions are met: 
* 
* 1. Redistributions of source code must retain the above copyright notice, this 
* list of conditions and the following disclaimer. 
* 
* 2. Redistributions in binary form must reproduce the above copyright notice, 
* this list of conditions and the following disclaimer in the documentation 
* and/or other materials provided with the distribution. 
* 
* 3. Neither the name of the copyright holder nor the names of its contributors 
* may be used to endorse or promote products derived from this software 
* without specific prior written permission. 
* 
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
* 
*/

#include "vl53l1_platform.h"
#include <string.h>
#include <time.h>
#include <math.h>

#include "py/dynruntime.h"

int8_t VL53L1_ReadMulti(uint16_t dev, uint16_t index, uint8_t *pdata, uint32_t count) {
    mp_obj_t upy_platform_obj = mp_import_name(MP_QSTR_upy_platform, mp_const_true, MP_OBJ_NEW_SMALL_INT(0));
    mp_obj_t i2c_obj = mp_import_from(upy_platform_obj, MP_QSTR_i2c);
    if (i2c_obj) {
        mp_obj_t readfrom_mem_fn = mp_load_attr(i2c_obj, MP_QSTR_readfrom_mem);
        if (readfrom_mem_fn) {
            mp_obj_t args[5] = {
                    MP_OBJ_NEW_SMALL_INT(dev),
                    MP_OBJ_NEW_SMALL_INT(index),
                    MP_OBJ_NEW_SMALL_INT(count),
                    MP_OBJ_NEW_QSTR(MP_QSTR_addrsize),
                    MP_OBJ_NEW_SMALL_INT(16),
            };
            mp_obj_t obj = mp_call_function_n_kw(readfrom_mem_fn, 3, 1, &args[0]);
            mp_buffer_info_t bufinfo;
            mp_get_buffer_raise(obj, &bufinfo, MP_BUFFER_READ);
            for (uint32_t i = 0; i < count; ++i) {
                pdata[i] = ((uint8_t*) bufinfo.buf)[i];
            }
        }
    }
    return 0; // to be implemented
}

int8_t VL53L1_WrByte(uint16_t dev, uint16_t index, uint8_t data) {
    mp_obj_t upy_platform_obj = mp_import_name(MP_QSTR_upy_platform, mp_const_true, MP_OBJ_NEW_SMALL_INT(0));
    mp_obj_t i2c_obj = mp_import_from(upy_platform_obj, MP_QSTR_i2c);
    if (i2c_obj) {
        mp_obj_t writeto_mem_fn = mp_load_attr(i2c_obj, MP_QSTR_writeto_mem);
        if (writeto_mem_fn) {
            mp_obj_t args[5] = {
                    MP_OBJ_NEW_SMALL_INT(dev),
                    MP_OBJ_NEW_SMALL_INT(index),
                    mp_obj_new_bytes(&data, 1),
                    MP_OBJ_NEW_QSTR(MP_QSTR_addrsize),
                    MP_OBJ_NEW_SMALL_INT(16),
            };
            mp_call_function_n_kw(writeto_mem_fn, 3, 1, &args[0]);
        }
    }
    return 0; // to be implemented
}

int8_t VL53L1_WrWord(uint16_t dev, uint16_t index, uint16_t data) {
    uint8_t data_hi = data >> 8, data_lo = data & 0xFF, data_hilo[2] = {data_hi, data_lo};
    mp_obj_t upy_platform_obj = mp_import_name(MP_QSTR_upy_platform, mp_const_true, MP_OBJ_NEW_SMALL_INT(0));
    mp_obj_t i2c_obj = mp_import_from(upy_platform_obj, MP_QSTR_i2c);
    if (i2c_obj) {
        mp_obj_t writeto_mem_fn = mp_load_attr(i2c_obj, MP_QSTR_writeto_mem);
        if (writeto_mem_fn) {
            mp_obj_t args[5] = {
                    MP_OBJ_NEW_SMALL_INT(dev),
                    MP_OBJ_NEW_SMALL_INT(index),
                    mp_obj_new_bytes(&data_hilo[0], 2),
                    MP_OBJ_NEW_QSTR(MP_QSTR_addrsize),
                    MP_OBJ_NEW_SMALL_INT(16),
            };
            mp_call_function_n_kw(writeto_mem_fn, 3, 1, &args[0]);
        }
    }
    return 0; // to be implemented
}

int8_t VL53L1_RdByte(uint16_t dev, uint16_t index, uint8_t *data) {
    mp_obj_t upy_platform_obj = mp_import_name(MP_QSTR_upy_platform, mp_const_true, MP_OBJ_NEW_SMALL_INT(0));
    mp_obj_t i2c_obj = mp_import_from(upy_platform_obj, MP_QSTR_i2c);
    if (i2c_obj) {
        mp_obj_t readfrom_mem_fn = mp_load_attr(i2c_obj, MP_QSTR_readfrom_mem);
        if (readfrom_mem_fn) {
            mp_obj_t args[5] = {
                    MP_OBJ_NEW_SMALL_INT(dev),
                    MP_OBJ_NEW_SMALL_INT(index),
                    MP_OBJ_NEW_SMALL_INT(1),
                    MP_OBJ_NEW_QSTR(MP_QSTR_addrsize),
                    MP_OBJ_NEW_SMALL_INT(16),
            };
            mp_obj_t obj = mp_call_function_n_kw(readfrom_mem_fn, 3, 1, &args[0]);
            mp_buffer_info_t bufinfo;
            mp_get_buffer_raise(obj, &bufinfo, MP_BUFFER_READ);
            *data = ((uint8_t*) bufinfo.buf)[0];
        }
    }
    return 0; // to be implemented
}

int8_t VL53L1_RdWord(uint16_t dev, uint16_t index, uint16_t *data) {
    mp_obj_t upy_platform_obj = mp_import_name(MP_QSTR_upy_platform, mp_const_true, MP_OBJ_NEW_SMALL_INT(0));
    mp_obj_t i2c_obj = mp_import_from(upy_platform_obj, MP_QSTR_i2c);
    if (i2c_obj) {
        mp_obj_t readfrom_mem_fn = mp_load_attr(i2c_obj, MP_QSTR_readfrom_mem);
        if (readfrom_mem_fn) {
            mp_obj_t args[5] = {
                    MP_OBJ_NEW_SMALL_INT(dev),
                    MP_OBJ_NEW_SMALL_INT(index),
                    MP_OBJ_NEW_SMALL_INT(2),
                    MP_OBJ_NEW_QSTR(MP_QSTR_addrsize),
                    MP_OBJ_NEW_SMALL_INT(16),
            };
            mp_obj_t obj = mp_call_function_n_kw(readfrom_mem_fn, 3, 1, &args[0]);
            mp_buffer_info_t bufinfo;
            mp_get_buffer_raise(obj, &bufinfo, MP_BUFFER_READ);
            *data = (((uint8_t*) bufinfo.buf)[0] << 8) + ((uint8_t*) bufinfo.buf)[1];
        }
    }
    return 0; // to be implemented
}
