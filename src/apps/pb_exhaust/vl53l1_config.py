DEFAULT_CONFIG = [
    0x00,  # 0x2d : VL53L1_PAD_I2C_HV__CONFIG                               : set bit 2 and 5 to 1 for fast plus mode (1MHz I2C), else don't touch
    0x00,  # 0x2e : VL53L1_PAD_I2C_HV__EXTSUP_CONFIG                        : bit 0 if I2C pulled up at 1.8V, else set bit 0 to 1 (pull up at AVDD)
    0x00,  # 0x2f : VL53L1_GPIO_HV_PAD__CTRL                                : bit 0 if GPIO pulled up at 1.8V, else set bit 0 to 1 (pull up at AVDD)
    0x01,  # 0x30 : VL53L1_GPIO_HV_MUX__CTRL                                : set bit 4 to 0 for active high interrupt and 1 for active low (bits 3:0 must be 0x1), use SetInterruptPolarity()
    0x02,  # 0x31 : VL53L1_GPIO__TIO_HV_STATUS                              : bit 1 = interrupt depending on the polarity, use CheckForDataReady()
    0x00,  # 0x32 : VL53L1_GPIO__FIO_HV_STATUS                              : not user-modifiable
    0x02,  # 0x33 : VL53L1_ANA_CONFIG__SPAD_SEL_PSWIDTH                     : not user-modifiable
    0x08,  # 0x34 : VL53L1_ANA_CONFIG__VCSEL_PULSE_WIDTH_OFFSET             : not user-modifiable
    0x00,  # 0x35 : VL53L1_ANA_CONFIG__FAST_OSC__CONFIG_CTRL                : not user-modifiable
    0x08,  # 0x36 : VL53L1_SIGMA_ESTIMATOR__EFFECTIVE_PULSE_WIDTH_NS        : not user-modifiable
    0x10,  # 0x37 : VL53L1_SIGMA_ESTIMATOR__EFFECTIVE_AMBIENT_WIDTH_NS      : not user-modifiable
    0x01,  # 0x38 : VL53L1_SIGMA_ESTIMATOR__SIGMA_REF_MM                    : not user-modifiable
    0x01,  # 0x39 : VL53L1_ALGO__CROSSTALK_COMPENSATION_VALID_HEIGHT_MM     : not user-modifiable
    0x00,  # 0x3a : VL53L1_SPARE_HOST_CONFIG__STATIC_CONFIG_SPARE_0         : not user-modifiable
    0x00,  # 0x3b : VL53L1_SPARE_HOST_CONFIG__STATIC_CONFIG_SPARE_1         : not user-modifiable
    0x00,  # 0x3c : VL53L1_ALGO__RANGE_IGNORE_THRESHOLD_MCPS_HI             : not user-modifiable
    0x00,  # 0x3d : VL53L1_ALGO__RANGE_IGNORE_THRESHOLD_MCPS_LO             : not user-modifiable
    0xFF,  # 0x3e : VL53L1_ALGO__RANGE_IGNORE_VALID_HEIGHT_MM               : not user-modifiable
    0x00,  # 0x3f : VL53L1_ALGO__RANGE_MIN_CLIP                             : not user-modifiable
    0x0F,  # 0x40 : VL53L1_ALGO__CONSISTENCY_CHECK__TOLERANCE               : not user-modifiable
    0x00,  # 0x41 : VL53L1_SPARE_HOST_CONFIG__STATIC_CONFIG_SPARE_2         : not user-modifiable
    0x00,  # 0x42 : VL53L1_SD_CONFIG__RESET_STAGES_MSB                      : not user-modifiable
    0x00,  # 0x43 : VL53L1_SD_CONFIG__RESET_STAGES_LSB                      : not user-modifiable
    0x00,  # 0x44 : VL53L1_GPH_CONFIG__STREAM_COUNT_UPDATE_VALUE            : not user-modifiable
    0x00,  # 0x45 : VL53L1_GLOBAL_CONFIG__STREAM_DIVIDER                    : not user-modifiable
    0x20,  # 0x46 : VL53L1_SYSTEM__INTERRUPT_CONFIG_GPIO                    : interrupt configuration 0->level low detection, 1-> level high, 2-> Out of window, 3->In window, 0x20-> New sample ready , TBC
    0x0B,  # 0x47 : VL53L1_CAL_CONFIG__VCSEL_START                          : not user-modifiable
    0x00,  # 0x48 : VL53L1_CAL_CONFIG__REPEAT_RATE_HI                       : not user-modifiable
    0x00,  # 0x49 : VL53L1_CAL_CONFIG__REPEAT_RATE_LO                       : not user-modifiable
    0x02,  # 0x4a : VL53L1_GLOBAL_CONFIG__VCSEL_WIDTH                       : not user-modifiable
    0x0A,  # 0x4b : VL53L1_PHASECAL_CONFIG__TIMEOUT_MACROP                  : not user-modifiable
    0x21,  # 0x4c : VL53L1_PHASECAL_CONFIG__TARGET                          : not user-modifiable
    0x00,  # 0x4d : VL53L1_PHASECAL_CONFIG__OVERRIDE                        : not user-modifiable
    0x00,  # 0x4e :                                                         : not user-modifiable
    0x05,  # 0x4f : VL53L1_DSS_CONFIG__ROI_MODE_CONTROL                     : not user-modifiable
    0x00,  # 0x50 : VL53L1_SYSTEM__THRESH_RATE_HIGH_HI                      : not user-modifiable
    0x00,  # 0x51 : VL53L1_SYSTEM__THRESH_RATE_HIGH_LO                      : not user-modifiable
    0x00,  # 0x52 : VL53L1_SYSTEM__THRESH_RATE_LOW_HI                       : not user-modifiable
    0x00,  # 0x53 : VL53L1_SYSTEM__THRESH_RATE_LOW_LO                       : not user-modifiable
    0xC8,  # 0x54 : VL53L1_DSS_CONFIG__MANUAL_EFFECTIVE_SPADS_SELECT_HI     : not user-modifiable
    0x00,  # 0x55 : VL53L1_DSS_CONFIG__MANUAL_EFFECTIVE_SPADS_SELECT_LO     : not user-modifiable
    0x00,  # 0x56 : VL53L1_DSS_CONFIG__MANUAL_BLOCK_SELECT                  : not user-modifiable
    0x38,  # 0x57 : VL53L1_DSS_CONFIG__APERTURE_ATTENUATION                 : not user-modifiable
    0xFF,  # 0x58 : VL53L1_DSS_CONFIG__MAX_SPADS_LIMIT                      : not user-modifiable
    0x01,  # 0x59 : VL53L1_DSS_CONFIG__MIN_SPADS_LIMIT                      : not user-modifiable
    0x00,  # 0x5a : VL53L1_MM_CONFIG__TIMEOUT_MACROP_A_HI                   : not user-modifiable
    0x08,  # 0x5b : VL53L1_MM_CONFIG__TIMEOUT_MACROP_A_LO                   : not user-modifiable
    0x00,  # 0x5c : VL53L1_MM_CONFIG__TIMEOUT_MACROP_B_HI                   : not user-modifiable
    0x00,  # 0x5d : VL53L1_MM_CONFIG__TIMEOUT_MACROP_B_LO                   : not user-modifiable
    0x01,  # 0x5e : VL53L1_RANGE_CONFIG__TIMEOUT_MACROP_A_HI                : not user-modifiable
    0xCC,  # 0x5f : VL53L1_RANGE_CONFIG__TIMEOUT_MACROP_A_LO                : not user-modifiable
    0x0F,  # 0x60 : VL53L1_RANGE_CONFIG__VCSEL_PERIOD_A                     : not user-modifiable
    0x01,  # 0x61 : VL53L1_RANGE_CONFIG__TIMEOUT_MACROP_B_HI                : not user-modifiable
    0xF1,  # 0x62 : VL53L1_RANGE_CONFIG__TIMEOUT_MACROP_B_LO                : not user-modifiable
    0x0D,  # 0x63 : VL53L1_RANGE_CONFIG__VCSEL_PERIOD_B                     : not user-modifiable
    0x01,  # 0x64 : VL53L1_RANGE_CONFIG__SIGMA_THRESH_HI                    : Sigma threshold MSB (mm in 14.2 format for MSB+LSB), use SetSigmaThreshold(), default value 90 mm
    0x68,  # 0x65 : VL53L1_RANGE_CONFIG__SIGMA_THRESH_LO                    : Sigma threshold LSB
    0x00,  # 0x66 : VL53L1_RANGE_CONFIG__MIN_COUNT_RATE_RTN_LIMIT_MCPS_HI   : Min count Rate MSB (MCPS in 9.7 format for MSB+LSB), use SetSignalThreshold()
    0x80,  # 0x67 : VL53L1_RANGE_CONFIG__MIN_COUNT_RATE_RTN_LIMIT_MCPS_LO   : Min count Rate LSB
    0x08,  # 0x68 : VL53L1_RANGE_CONFIG__VALID_PHASE_LOW                    : not user-modifiable
    0xB8,  # 0x69 : VL53L1_RANGE_CONFIG__VALID_PHASE_HIGH                   : not user-modifiable
    0x00,  # 0x6a :                                                         : not user-modifiable
    0x00,  # 0x6b :                                                         : not user-modifiable
    0x00,  # 0x6c : VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD_3                : Intermeasurement period MSB, 32 bits register, use SetIntermeasurementInMs()
    0x00,  # 0x6d : VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD_2                : Intermeasurement period
    0x0F,  # 0x6e : VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD_1                : Intermeasurement period
    0x89,  # 0x6f : VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD_0                : Intermeasurement period LSB
    0x00,  # 0x70 : VL53L1_SYSTEM__FRACTIONAL_ENABLE                        : not user-modifiable
    0x00,  # 0x71 : VL53L1_SYSTEM__GROUPED_PARAMETER_HOLD_0                 : not user-modifiable
    0x00,  # 0x72 : VL53L1_SYSTEM__THRESH_HIGH_HI                           : distance threshold high MSB (in mm, MSB+LSB), use SetD:tanceThreshold()
    0x00,  # 0x73 : VL53L1_SYSTEM__THRESH_HIGH_LO                           : distance threshold high LSB
    0x00,  # 0x74 : VL53L1_SYSTEM__THRESH_LOW_HI                            : distance threshold low MSB ( in mm, MSB+LSB), use SetD:tanceThreshold()
    0x00,  # 0x75 : VL53L1_SYSTEM__THRESH_LOW_LO                            : distance threshold low LSB
    0x00,  # 0x76 : VL53L1_SYSTEM__ENABLE_XTALK_PER_QUADRANT                : not user-modifiable
    0x01,  # 0x77 : VL53L1_SYSTEM__SEED_CONFIG                              : not user-modifiable
    0x0F,  # 0x78 : VL53L1_SD_CONFIG__WOI_SD0                               : not user-modifiable
    0x0D,  # 0x79 : VL53L1_SD_CONFIG__WOI_SD1                               : not user-modifiable
    0x0E,  # 0x7a : VL53L1_SD_CONFIG__INITIAL_PHASE_SD0                     : not user-modifiable
    0x0E,  # 0x7b : VL53L1_SD_CONFIG__INITIAL_PHASE_SD1                     : not user-modifiable
    0x00,  # 0x7c : VL53L1_SYSTEM__GROUPED_PARAMETER_HOLD_1                 : not user-modifiable
    0x00,  # 0x7d : VL53L1_SD_CONFIG__FIRST_ORDER_SELECT                    : not user-modifiable
    0x02,  # 0x7e : VL53L1_SD_CONFIG__QUANTIFIER                            : not user-modifiable
    0xC7,  # 0x7f : VL53L1_ROI_CONFIG__USER_ROI_CENTRE_SPAD                 : ROI center, use SetROI()
    0xFF,  # 0x80 : VL53L1_ROI_CONFIG__USER_ROI_REQUESTED_GLOBAL_XY_SIZE    : XY ROI (X=Width, Y=Height), use SetROI()
    0x9B,  # 0x81 : VL53L1_SYSTEM__SEQUENCE_CONFIG                          : not user-modifiable
    0x00,  # 0x82 : VL53L1_SYSTEM__GROUPED_PARAMETER_HOLD                   : not user-modifiable
    0x00,  # 0x83 : VL53L1_POWER_MANAGEMENT__GO1_POWER_FORCE                : not user-modifiable
    0x00,  # 0x84 : VL53L1_SYSTEM__STREAM_COUNT_CTRL                        : not user-modifiable
    0x01,  # 0x85 : VL53L1_FIRMWARE__ENABLE                                 : not user-modifiable
    0x00,  # 0x86 : VL53L1_SYSTEM__INTERRUPT_CLEAR                          : clear interrupt, use ClearInterrupt()
    0x00,  # 0x87 : VL53L1_SYSTEM__MODE_START                               : start ranging, use StartRanging() or StopRanging(), If you want an automatic start after VL53L1X_init() call, put 0x40 in location 0x87
]
