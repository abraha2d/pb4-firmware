VL53L1_I2C_SLAVE__DEVICE_ADDRESS = 0x0001
VL53L1_VHV_CONFIG__TIMEOUT_MACROP_LOOP_BOUND = 0x0008
ALGO__CROSSTALK_COMPENSATION_PLANE_OFFSET_KCPS = 0x0016
ALGO__CROSSTALK_COMPENSATION_X_PLANE_GRADIENT_KCPS = 0x0018
ALGO__CROSSTALK_COMPENSATION_Y_PLANE_GRADIENT_KCPS = 0x001A
ALGO__PART_TO_PART_RANGE_OFFSET_MM = 0x001E
MM_CONFIG__INNER_OFFSET_MM = 0x0020
MM_CONFIG__OUTER_OFFSET_MM = 0x0022
GPIO_HV_MUX__CTRL = 0x0030
GPIO__TIO_HV_STATUS = 0x0031
SYSTEM__INTERRUPT_CONFIG_GPIO = 0x0046
PHASECAL_CONFIG__TIMEOUT_MACROP = 0x0004B
RANGE_CONFIG__TIMEOUT_MACROP_A_HI = 0x005E
RANGE_CONFIG__VCSEL_PERIOD_A = 0x0060
RANGE_CONFIG__TIMEOUT_MACROP_B_HI = 0x0061
RANGE_CONFIG__VCSEL_PERIOD_B = 0x0063
RANGE_CONFIG__SIGMA_THRESH = 0x0064
RANGE_CONFIG__MIN_COUNT_RATE_RTN_LIMIT_MCPS = 0x0066
RANGE_CONFIG__VALID_PHASE_HIGH = 0x0069
VL53L1_SYSTEM__INTERMEASUREMENT_PERIOD = 0x006C
SYSTEM__THRESH_HIGH = 0x0062
SYSTEM__THRESH_LOW = 0x0074
SD_CONFIG__WOI_SD0 = 0x0078
SD_CONFIG__INITIAL_PHASE_SD0 = 0x007A
ROI_CONFIG__USER_ROI_CENTRE_SPAD = 0x007F
ROI_CONFIG__USER_ROI_REQUESTED_GLOBAL_XY_SIZE = 0x0080
SYSTEM__INTERRUPT_CLEAR = 0x0086
SYSTEM__MODE_START = 0x0087
VL53L1_RESULT__RANGE_STATUS = 0x0089
VL53L1_RESULT__DSS_ACTUAL_EFFECTIVE_SPADS_SD0 = 0x008C
RESULT__AMBIENT_COUNT_RATE_MCPS_SD = 0x0090
VL53L1_RESULT__FINAL_CROSSTALK_CORRECTED_RANGE_MM_SD0 = 0x0096
VL53L1_RESULT__PEAK_SIGNAL_COUNT_RATE_CROSSTALK_CORRECTED_MCPS_SD0 = 0x0098
VL53L1_RESULT__OSC_CALIBRATE_VAL = 0x00DE
VL53L1_FIRMWARE__SYSTEM_STATUS = 0x00E5
VL53L1_IDENTIFICATION__MODEL_ID = 0x010F
VL53L1_ROI_CONFIG__MODE_ROI_CENTRE_SPAD = 0x013E

DEFAULT_CONFIGURATION = [
    0x00,  # 0x2d : set bit 2 and 5 to 1 for fast plus mode (1MHz I2C), else don't touch
    0x00,  # 0x2e : bit 0 if I2C pulled up at 1.8V, else set bit 0 to 1 (pull up at AVDD)
    0x00,  # 0x2f : bit 0 if GPIO pulled up at 1.8V, else set bit 0 to 1 (pull up at AVDD)
    0x01,  # 0x30 :0 must be 0x1), use SetInterruptPolarity()
    0x02,  # 0x31 : bit 1 = interrupt depending on the polarity, use CheckForDataReady()
    0x00,  # 0x32 : not user-modifiable
    0x02,  # 0x33 : not user-modifiable
    0x08,  # 0x34 : not user-modifiable
    0x00,  # 0x35 : not user-modifiable
    0x08,  # 0x36 : not user-modifiable
    0x10,  # 0x37 : not user-modifiable
    0x01,  # 0x38 : not user-modifiable
    0x01,  # 0x39 : not user-modifiable
    0x00,  # 0x3a : not user-modifiable
    0x00,  # 0x3b : not user-modifiable
    0x00,  # 0x3c : not user-modifiable
    0x00,  # 0x3d : not user-modifiable
    0xFF,  # 0x3e : not user-modifiable
    0x00,  # 0x3f : not user-modifiable
    0x0F,  # 0x40 : not user-modifiable
    0x00,  # 0x41 : not user-modifiable
    0x00,  # 0x42 : not user-modifiable
    0x00,  # 0x43 : not user-modifiable
    0x00,  # 0x44 : not user-modifiable
    0x00,  # 0x45 : not user-modifiable
    0x20,  # 0x46 : interrupt configuration 0->level low detection, 1-> level high, 2-> Out of window, 3->In window, 0x20-> New sample ready , TBC
    0x0B,  # 0x47 : not user-modifiable
    0x00,  # 0x48 : not user-modifiable
    0x00,  # 0x49 : not user-modifiable
    0x02,  # 0x4a : not user-modifiable
    0x0A,  # 0x4b : not user-modifiable
    0x21,  # 0x4c : not user-modifiable
    0x00,  # 0x4d : not user-modifiable
    0x00,  # 0x4e : not user-modifiable
    0x05,  # 0x4f : not user-modifiable
    0x00,  # 0x50 : not user-modifiable
    0x00,  # 0x51 : not user-modifiable
    0x00,  # 0x52 : not user-modifiable
    0x00,  # 0x53 : not user-modifiable
    0xC8,  # 0x54 : not user-modifiable
    0x00,  # 0x55 : not user-modifiable
    0x00,  # 0x56 : not user-modifiable
    0x38,  # 0x57 : not user-modifiable
    0xFF,  # 0x58 : not user-modifiable
    0x01,  # 0x59 : not user-modifiable
    0x00,  # 0x5a : not user-modifiable
    0x08,  # 0x5b : not user-modifiable
    0x00,  # 0x5c : not user-modifiable
    0x00,  # 0x5d : not user-modifiable
    0x01,  # 0x5e : not user-modifiable
    0xCC,  # 0x5f : not user-modifiable
    0x0F,  # 0x60 : not user-modifiable
    0x01,  # 0x61 : not user-modifiable
    0xF1,  # 0x62 : not user-modifiable
    0x0D,  # 0x63 : not user-modifiable
    0x01,  # 0x64 : Sigma threshold MSB (mm in 14.2 format for MSB+LSB), use SetSigmaThreshold(), default value 90 mm
    0x68,  # 0x65 : Sigma threshold LSB
    0x00,  # 0x66 : Min count Rate MSB (MCPS in 9.7 format for MSB+LSB), use SetSignalThreshold()
    0x80,  # 0x67 : Min count Rate LSB
    0x08,  # 0x68 : not user-modifiable
    0xB8,  # 0x69 : not user-modifiable
    0x00,  # 0x6a : not user-modifiable
    0x00,  # 0x6b : not user-modifiable
    0x00,  # 0x6c : Intermeasurement period MSB, 32 bits register, use SetIntermeasurementInMs()
    0x00,  # 0x6d : Intermeasurement period
    0x0F,  # 0x6e : Intermeasurement period
    0x89,  # 0x6f : Intermeasurement period LSB
    0x00,  # 0x70 : not user-modifiable
    0x00,  # 0x71 : not user-modifiable
    0x00,  # 0x72 :tanceThreshold()
    0x00,  # 0x73 : distance threshold high LSB
    0x00,  # 0x74 :tanceThreshold()
    0x00,  # 0x75 : distance threshold low LSB
    0x00,  # 0x76 : not user-modifiable
    0x01,  # 0x77 : not user-modifiable
    0x0F,  # 0x78 : not user-modifiable
    0x0D,  # 0x79 : not user-modifiable
    0x0E,  # 0x7a : not user-modifiable
    0x0E,  # 0x7b : not user-modifiable
    0x00,  # 0x7c : not user-modifiable
    0x00,  # 0x7d : not user-modifiable
    0x02,  # 0x7e : not user-modifiable
    0xC7,  # 0x7f : ROI center, use SetROI()
    0xFF,  # 0x80 : XY ROI (X=Width, Y=Height), use SetROI()
    0x9B,  # 0x81 : not user-modifiable
    0x00,  # 0x82 : not user-modifiable
    0x00,  # 0x83 : not user-modifiable
    0x00,  # 0x84 : not user-modifiable
    0x01,  # 0x85 : not user-modifiable
    0x00,  # 0x86 : clear interrupt, use ClearInterrupt()
    0x00,  # 0x87 : start ranging, use StartRanging() or StopRanging(), If you want an automatic start after VL53L1X_init() call, put 0x40 in location 0x87
]
