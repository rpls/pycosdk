from ctypes import c_uint32
from enum import IntEnum


class PICO_INFO(IntEnum):
    PICO_DRIVER_VERSION = 0x00000000
    PICO_USB_VERSION = 0x00000001
    PICO_HARDWARE_VERSION = 0x00000002
    PICO_VARIANT_INFO = 0x00000003
    PICO_BATCH_AND_SERIAL = 0x00000004
    PICO_CAL_DATE = 0x00000005
    PICO_KERNEL_VERSION = 0x00000006
    PICO_DIGITAL_HARDWARE_VERSION = 0x00000007
    PICO_ANALOGUE_HARDWARE_VERSION = 0x00000008
    PICO_FIRMWARE_VERSION_1 = 0x00000009
    PICO_FIRMWARE_VERSION_2 = 0x0000000A
    PICO_MAC_ADDRESS = 0x0000000B
    PICO_SHADOW_CAL = 0x0000000C
    PICO_IPP_VERSION = 0x0000000D
    PICO_DRIVER_PATH = 0x0000000E
    PICO_FIRMWARE_VERSION_3 = 0x0000000F
    PICO_FRONT_PANEL_FIRMWARE_VERSION = 0x00000010
    PICO_BOOTLOADER_VERSION = 0x10000001


PICO_INFO_T = c_uint32


class PICO_STATUS(IntEnum):
    # The PicoScope is functioning correctly.
    PICO_OK = 0x00000000
    # An attempt has been made to open more than <API>_MAX_UNITS.
    PICO_MAX_UNITS_OPENED = 0x00000001
    # Not enough memory could be allocated on the host machine.
    PICO_MEMORY_FAIL = 0x00000002
    # No Pico Technology device could be found.
    PICO_NOT_FOUND = 0x00000003
    # Unable to download firmware.
    PICO_FW_FAIL = 0x00000004
    # The driver is busy opening a device.
    PICO_OPEN_OPERATION_IN_PROGRESS = 0x00000005
    # An unspecified failure occurred.
    PICO_OPERATION_FAILED = 0x00000006
    # The PicoScope is not responding to commands from the PC.
    PICO_NOT_RESPONDING = 0x00000007
    # The configuration information in the PicoScope is corrupt or missing.
    PICO_CONFIG_FAIL = 0x00000008
    # The picopp.sys file is too old to be used with the device driver.
    PICO_KERNEL_DRIVER_TOO_OLD = 0x00000009
    # The EEPROM has become corrupt, so the device will use a default setting.
    PICO_EEPROM_CORRUPT = 0x0000000A
    # The operating system on the PC is not supported by this driver.
    PICO_OS_NOT_SUPPORTED = 0x0000000B
    # There is no device with the handle value passed.
    PICO_INVALID_HANDLE = 0x0000000C
    # A parameter value is not valid.
    PICO_INVALID_PARAMETER = 0x0000000D
    # The timebase is not supported or is invalid.
    PICO_INVALID_TIMEBASE = 0x0000000E
    # The voltage range is not supported or is invalid.
    PICO_INVALID_VOLTAGE_RANGE = 0x0000000F
    # The channel number is not valid on this device or no channels have been set.
    PICO_INVALID_CHANNEL = 0x00000010
    # The channel set for a trigger is not available on this device.
    PICO_INVALID_TRIGGER_CHANNEL = 0x00000011
    # The channel set for a condition is not available on this device.
    PICO_INVALID_CONDITION_CHANNEL = 0x00000012
    # The device does not have a signal generator.
    PICO_NO_SIGNAL_GENERATOR = 0x00000013
    # Streaming has failed to start or has stopped without user request.
    PICO_STREAMING_FAILED = 0x00000014
    # Block failed to start - a parameter may have been set wrongly.
    PICO_BLOCK_MODE_FAILED = 0x00000015
    # A parameter that was required is NULL.
    PICO_NULL_PARAMETER = 0x00000016
    # The current functionality is not available while using ETS capture mode.
    PICO_ETS_MODE_SET = 0x00000017
    # No data is available from a run block call.
    PICO_DATA_NOT_AVAILABLE = 0x00000018
    # The buffer passed for the information was too small.
    PICO_STRING_BUFFER_TO_SMALL = 0x00000019
    # ETS is not supported on this device.
    PICO_ETS_NOT_SUPPORTED = 0x0000001A
    # The auto trigger time is less than the time it will take to collect the pre-trigger data.
    PICO_AUTO_TRIGGER_TIME_TO_SHORT = 0x0000001B
    # The collection of data has stalled as unread data would be overwritten.
    PICO_BUFFER_STALL = 0x0000001C
    # Number of samples requested is more than available in the current memory segment.
    PICO_TOO_MANY_SAMPLES = 0x0000001D
    # Not possible to create number of segments requested.
    PICO_TOO_MANY_SEGMENTS = 0x0000001E
    # A null pointer has been passed in the trigger function or one of the parameters is out of range.
    PICO_PULSE_WIDTH_QUALIFIER = 0x0000001F
    # One or more of the hold-off parameters are out of range.
    PICO_DELAY = 0x00000020
    # One or more of the source details are incorrect.
    PICO_SOURCE_DETAILS = 0x00000021
    # One or more of the conditions are incorrect.
    PICO_CONDITIONS = 0x00000022
    # The driver's thread is currently in the <API>Ready callback
    # function and therefore the action cannot be carried out.
    PICO_USER_CALLBACK = 0x00000023
    # An attempt is being made to get stored data while streaming.
    # Either stop streaming by calling <API>Stop, or use <API>GetStreamingLatestValues.
    PICO_DEVICE_SAMPLING = 0x00000024
    # Data is unavailable because a run has not been completed.
    PICO_NO_SAMPLES_AVAILABLE = 0x00000025
    # The memory segment index is out of range.
    PICO_SEGMENT_OUT_OF_RANGE = 0x00000026
    # The device is busy so data cannot be returned yet.
    PICO_BUSY = 0x00000027
    # The start time to get stored data is out of range.
    PICO_STARTINDEX_INVALID = 0x00000028
    # The information number requested is not a valid number.
    PICO_INVALID_INFO = 0x00000029
    # The handle is invalid so no information is available about the device.
    # Only PICO_DRIVER_VERSION is available.
    PICO_INFO_UNAVAILABLE = 0x0000002A
    # The sample interval selected for streaming is out of range.
    PICO_INVALID_SAMPLE_INTERVAL = 0x0000002B
    # ETS is set but no trigger has been set. A trigger setting is required for ETS.
    PICO_TRIGGER_ERROR = 0x0000002C
    # Driver cannot allocate memory.
    PICO_MEMORY = 0x0000002D
    # Incorrect parameter passed to the signal generator.
    PICO_SIG_GEN_PARAM = 0x0000002E
    # Conflict between the shots and sweeps parameters sent to the signal generator.
    PICO_SHOTS_SWEEPS_WARNING = 0x0000002F
    # A software trigger has been sent but the trigger source is not a software trigger.
    PICO_SIGGEN_TRIGGER_SOURCE = 0x00000030
    # An <API>SetTrigger call has found a conflict between the trigger source and the AUX output enable.
    PICO_AUX_OUTPUT_CONFLICT = 0x00000031
    # ETS mode is being used and AUX is set as an input.
    PICO_AUX_OUTPUT_ETS_CONFLICT = 0x00000032
    # Attempt to set different EXT input thresholds set for signal generator and oscilloscope trigger.
    PICO_WARNING_EXT_THRESHOLD_CONFLICT = 0x00000033
    # An <API>SetTrigger... function has set AUX as an output and the signal generator is using it as a trigger.
    PICO_WARNING_AUX_OUTPUT_CONFLICT = 0x00000034
    # The combined peak-to-peak voltage and the analog offset voltage exceed the maximum voltage the signal generator can produce.
    PICO_SIGGEN_OUTPUT_OVER_VOLTAGE = 0x00000035
    # NULL pointer passed as delay parameter.
    PICO_DELAY_NULL = 0x00000036
    # The buffers for overview data have not been set while streaming.
    PICO_INVALID_BUFFER = 0x00000037
    # The analog offset voltage is out of range.
    PICO_SIGGEN_OFFSET_VOLTAGE = 0x00000038
    # The analog peak-to-peak voltage is out of range.
    PICO_SIGGEN_PK_TO_PK = 0x00000039
    # A block collection has been cancelled.
    PICO_CANCELLED = 0x0000003A
    # The segment index is not currently being used.
    PICO_SEGMENT_NOT_USED = 0x0000003B
    # The wrong GetValues function has been called for the collection mode in use.
    PICO_INVALID_CALL = 0x0000003C
    PICO_GET_VALUES_INTERRUPTED = 0x0000003D
    # The function is not available.
    PICO_NOT_USED = 0x0000003F
    # The aggregation ratio requested is out of range.
    PICO_INVALID_SAMPLERATIO = 0x00000040
    # Device is in an invalid state.
    PICO_INVALID_STATE = 0x00000041
    # The number of segments allocated is fewer than the number of captures requested.
    PICO_NOT_ENOUGH_SEGMENTS = 0x00000042
    # A driver function has already been called and not yet finished.
    # Only one call to the driver can be made at any one time.
    PICO_DRIVER_FUNCTION = 0x00000043
    # Not used.
    PICO_RESERVED = 0x00000044
    # An invalid coupling type was specified in <API>SetChannel.
    PICO_INVALID_COUPLING = 0x00000045
    # An attempt was made to get data before a data buffer was defined.
    PICO_BUFFERS_NOT_SET = 0x00000046
    # The selected downsampling mode (used for data reduction) is not allowed.
    PICO_RATIO_MODE_NOT_SUPPORTED = 0x00000047
    # Aggregation was requested in rapid block mode.
    PICO_RAPID_NOT_SUPPORT_AGGREGATION = 0x00000048
    # An invalid parameter was passed to <API>SetTriggerChannelProperties(V2).
    PICO_INVALID_TRIGGER_PROPERTY = 0x00000049
    # The driver was unable to contact the oscilloscope.
    PICO_INTERFACE_NOT_CONNECTED = 0x0000004A
    # Resistance-measuring mode is not allowed in conjunction with the specified probe.
    PICO_RESISTANCE_AND_PROBE_NOT_ALLOWED = 0x0000004B
    # The device was unexpectedly powered down.
    PICO_POWER_FAILED = 0x0000004C
    # A problem occurred in <API>SetSigGenBuiltIn or <API>SetSigGenArbitrary.
    PICO_SIGGEN_WAVEFORM_SETUP_FAILED = 0x0000004D
    # FPGA not successfully set up.
    PICO_FPGA_FAIL = 0x0000004E
    PICO_POWER_MANAGER = 0x0000004F
    # An impossible analog offset value was specified in <API>SetChannel.
    PICO_INVALID_ANALOGUE_OFFSET = 0x00000050
    # There is an error within the device hardware.
    PICO_PLL_LOCK_FAILED = 0x00000051
    # There is an error within the device hardware.
    PICO_ANALOG_BOARD = 0x00000052
    # Unable to configure the signal generator.
    PICO_CONFIG_FAIL_AWG = 0x00000053
    # The FPGA cannot be initialized, so unit cannot be opened.
    PICO_INITIALISE_FPGA = 0x00000054
    # The frequency for the external clock is not within 15% of the nominal value.
    PICO_EXTERNAL_FREQUENCY_INVALID = 0x00000056
    # The FPGA could not lock the clock signal.
    PICO_CLOCK_CHANGE_ERROR = 0x00000057
    # You are trying to configure the AUX input as both a trigger and a reference clock.
    PICO_TRIGGER_AND_EXTERNAL_CLOCK_CLASH = 0x00000058
    # You are trying to configure the AUX input as both a pulse width qualifier and a reference clock.
    PICO_PWQ_AND_EXTERNAL_CLOCK_CLASH = 0x00000059
    # The requested scaling file cannot be opened.
    PICO_UNABLE_TO_OPEN_SCALING_FILE = 0x0000005A
    # The frequency of the memory is reporting incorrectly.
    PICO_MEMORY_CLOCK_FREQUENCY = 0x0000005B
    # The I2C that is being actioned is not responding to requests.
    PICO_I2C_NOT_RESPONDING = 0x0000005C
    # There are no captures available and therefore no data can be returned.
    PICO_NO_CAPTURES_AVAILABLE = 0x0000005D
    # The number of trigger channels is greater than 4,
    # except for a PicoScope 4824 where 8 channels are allowed for rising/falling/rising_or_falling trigger directions.
    PICO_TOO_MANY_TRIGGER_CHANNELS_IN_USE = 0x0000005F
    # If you have specified a trigger direction which is not allowed, for example specifying PICO_ABOVE
    # without another condition which crosses a threshold on another channel.
    PICO_INVALID_TRIGGER_DIRECTION = 0x00000060
    # When more than 4 trigger channels are set and their trigger condition states are not <API>_CONDITION_TRUE.
    PICO_INVALID_TRIGGER_STATES = 0x00000061
    # The capture mode the device is currently running in does not support the current request.
    PICO_NOT_USED_IN_THIS_CAPTURE_MODE = 0x0000005E
    PICO_GET_DATA_ACTIVE = 0x00000103
    # Codes 104 to 10B are used by the PT104 (USB) when connected via the Network Socket.
    # The device is currently connected via the IP Network socket and thus the call made is not supported.
    PICO_IP_NETWORKED = 0x00000104
    # An incorrect IP address has been passed to the driver.
    PICO_INVALID_IP_ADDRESS = 0x00000105
    # The IP socket has failed.
    PICO_IPSOCKET_FAILED = 0x00000106
    # The IP socket has timed out.
    PICO_IPSOCKET_TIMEDOUT = 0x00000107
    # Failed to apply the requested settings.
    PICO_SETTINGS_FAILED = 0x00000108
    # The network connection has failed.
    PICO_NETWORK_FAILED = 0x00000109
    # Unable to load the WS2 DLL.
    PICO_WS2_32_DLL_NOT_LOADED = 0x0000010A
    # The specified IP port is invalid.
    PICO_INVALID_IP_PORT = 0x0000010B
    # The type of coupling requested is not supported on the opened device.
    PICO_COUPLING_NOT_SUPPORTED = 0x0000010C
    # Bandwidth limiting is not supported on the opened device.
    PICO_BANDWIDTH_NOT_SUPPORTED = 0x0000010D
    # The value requested for the bandwidth limit is out of range.
    PICO_INVALID_BANDWIDTH = 0x0000010E
    # The arbitrary waveform generator is not supported by the opened device.
    PICO_AWG_NOT_SUPPORTED = 0x0000010F
    # Data has been requested with ETS mode set but run block has not been called,
    # or stop has been called.
    PICO_ETS_NOT_RUNNING = 0x00000110
    # White noise output is not supported on the opened device.
    PICO_SIG_GEN_WHITENOISE_NOT_SUPPORTED = 0x00000111
    # The wave type requested is not supported by the opened device.
    PICO_SIG_GEN_WAVETYPE_NOT_SUPPORTED = 0x00000112
    # The requested digital port number is out of range (MSOs only).
    PICO_INVALID_DIGITAL_PORT = 0x00000113
    # The digital channel is not in the range <API>_DIGITAL_CHANNEL0 to
    # <API>_DIGITAL_CHANNEL15, the digital channels that are supported.
    PICO_INVALID_DIGITAL_CHANNEL = 0x00000114
    # The digital trigger direction is not a valid trigger direction and should be equal
    # in value to one of the <API>_DIGITAL_DIRECTION enumerations.
    PICO_INVALID_DIGITAL_TRIGGER_DIRECTION = 0x00000115
    # Signal generator does not generate pseudo-random binary sequence.
    PICO_SIG_GEN_PRBS_NOT_SUPPORTED = 0x00000116
    # When a digital port is enabled, ETS sample mode is not available for use.
    PICO_ETS_NOT_AVAILABLE_WITH_LOGIC_CHANNELS = 0x00000117
    # There has been no new sample taken, this value has already been returned previously.
    PICO_WARNING_REPEAT_VALUE = 0x00000118
    # The DC power supply is connected.
    PICO_POWER_SUPPLY_CONNECTED = 0x00000119
    # The DC power supply is not connected.
    # For many 4+ Channel devices this will mean a restricted feature set is offered e.g. for a 4 channel device - C and D are usually disabled.
    # Check the respective API programmers guide of your device for the full details.
    PICO_POWER_SUPPLY_NOT_CONNECTED = 0x0000011A
    # Incorrect power mode passed for current power source.
    PICO_POWER_SUPPLY_REQUEST_INVALID = 0x0000011B
    # The supply voltage from the USB source is too low.
    PICO_POWER_SUPPLY_UNDERVOLTAGE = 0x0000011C
    # The oscilloscope is in the process of capturing data.
    PICO_CAPTURING_DATA = 0x0000011D
    # A USB 3.0 device is connected to a non-USB 3.0 port.
    PICO_USB3_0_DEVICE_NON_USB3_0_PORT = 0x0000011E
    # A function has been called that is not supported by the current device.
    PICO_NOT_SUPPORTED_BY_THIS_DEVICE = 0x0000011F
    # The device resolution is invalid (out of range).
    PICO_INVALID_DEVICE_RESOLUTION = 0x00000120
    # The number of channels that can be enabled is limited in 15 and 16-bit modes.
    # (Flexible Resolution Oscilloscopes only)
    PICO_INVALID_NUMBER_CHANNELS_FOR_RESOLUTION = 0x00000121
    # USB power not sufficient for all requested channels.
    PICO_CHANNEL_DISABLED_DUE_TO_USB_POWERED = 0x00000122
    # The signal generator does not have a configurable DC offset.
    PICO_SIGGEN_DC_VOLTAGE_NOT_CONFIGURABLE = 0x00000123
    # An attempt has been made to define pre-trigger delay without first enabling a trigger.
    PICO_NO_TRIGGER_ENABLED_FOR_TRIGGER_IN_PRE_TRIG = 0x00000124
    # An attempt has been made to define pre-trigger delay without first arming a trigger.
    PICO_TRIGGER_WITHIN_PRE_TRIG_NOT_ARMED = 0x00000125
    # Pre-trigger delay and post-trigger delay cannot be used at the same time.
    PICO_TRIGGER_WITHIN_PRE_NOT_ALLOWED_WITH_DELAY = 0x00000126
    # The array index points to a nonexistent trigger.
    PICO_TRIGGER_INDEX_UNAVAILABLE = 0x00000127
    PICO_AWG_CLOCK_FREQUENCY = 0x00000128
    # There are more than 4 analog channels with a trigger condition set.
    PICO_TOO_MANY_CHANNELS_IN_USE = 0x00000129
    # The condition parameter is a null pointer.
    PICO_NULL_CONDITIONS = 0x0000012A
    # There is more than one condition pertaining to the same channel.
    PICO_DUPLICATE_CONDITION_SOURCE = 0x0000012B
    # The parameter relating to condition information is out of range.
    PICO_INVALID_CONDITION_INFO = 0x0000012C
    # Reading the meta data has failed.
    PICO_SETTINGS_READ_FAILED = 0x0000012D
    # Writing the meta data has failed.
    PICO_SETTINGS_WRITE_FAILED = 0x0000012E
    # A parameter has a value out of the expected range.
    PICO_ARGUMENT_OUT_OF_RANGE = 0x0000012F
    # The driver does not support the hardware variant connected.
    PICO_HARDWARE_VERSION_NOT_SUPPORTED = 0x00000130
    # The driver does not support the digital hardware variant connected.
    PICO_DIGITAL_HARDWARE_VERSION_NOT_SUPPORTED = 0x00000131
    # The driver does not support the analog hardware variant connected.
    PICO_ANALOGUE_HARDWARE_VERSION_NOT_SUPPORTED = 0x00000132
    # Converting a channel's ADC value to resistance has failed.
    PICO_UNABLE_TO_CONVERT_TO_RESISTANCE = 0x00000133
    # The channel is listed more than once in the function call.
    PICO_DUPLICATED_CHANNEL = 0x00000134
    # The range cannot have resistance conversion applied.
    PICO_INVALID_RESISTANCE_CONVERSION = 0x00000135
    # An invalid value is in the max buffer.
    PICO_INVALID_VALUE_IN_MAX_BUFFER = 0x00000136
    # An invalid value is in the min buffer.
    PICO_INVALID_VALUE_IN_MIN_BUFFER = 0x00000137
    # When calculating the frequency for phase conversion,
    # the frequency is greater than that supported by the current variant.
    PICO_SIGGEN_FREQUENCY_OUT_OF_RANGE = 0x00000138
    # The device's EEPROM is corrupt. Contact Pico Technology support: https://www.picotech.com/tech-support.
    PICO_EEPROM2_CORRUPT = 0x00000139
    # The EEPROM has failed.
    PICO_EEPROM2_FAIL = 0x0000013A
    # The serial buffer is too small for the required information.
    PICO_SERIAL_BUFFER_TOO_SMALL = 0x0000013B
    # The signal generator trigger and the external clock have both been set.
    # This is not allowed.
    PICO_SIGGEN_TRIGGER_AND_EXTERNAL_CLOCK_CLASH = 0x0000013C
    # The AUX trigger was enabled and the external clock has been enabled,
    # so the AUX has been automatically disabled.
    PICO_WARNING_SIGGEN_AUXIO_TRIGGER_DISABLED = 0x0000013D
    # The AUX I/O was set as a scope trigger and is now being set as a signal generator
    # gating trigger. This is not allowed.
    PICO_SIGGEN_GATING_AUXIO_NOT_AVAILABLE = 0x00000013E
    # The AUX I/O was set by the signal generator as a gating trigger and is now being set
    # as a scope trigger. This is not allowed.
    PICO_SIGGEN_GATING_AUXIO_ENABLED = 0x00000013F
    # A resource has failed to initialise.
    PICO_RESOURCE_ERROR = 0x00000140
    # The temperature type is out of range.
    PICO_TEMPERATURE_TYPE_INVALID = 0x000000141
    # A requested temperature type is not supported on this device.
    PICO_TEMPERATURE_TYPE_NOT_SUPPORTED = 0x000000142
    # A read/write to the device has timed out.
    PICO_TIMEOUT = 0x00000143
    # The device cannot be connected correctly.
    PICO_DEVICE_NOT_FUNCTIONING = 0x00000144
    # The driver has experienced an unknown error and is unable to recover from this error.
    PICO_INTERNAL_ERROR = 0x00000145
    # Used when opening units via IP and more than multiple units have the same IP address.
    PICO_MULTIPLE_DEVICES_FOUND = 0x00000146
    PICO_WARNING_NUMBER_OF_SEGMENTS_REDUCED = 0x00000147
    # The calibration pin states argument is out of range.
    PICO_CAL_PINS_STATES = 0x00000148
    # The calibration pin frequency argument is out of range.
    PICO_CAL_PINS_FREQUENCY = 0x00000149
    # The calibration pin amplitude argument is out of range.
    PICO_CAL_PINS_AMPLITUDE = 0x0000014A
    # The calibration pin wavetype argument is out of range.
    PICO_CAL_PINS_WAVETYPE = 0x0000014B
    # The calibration pin offset argument is out of range.
    PICO_CAL_PINS_OFFSET = 0x0000014C
    # The probe's identity has a problem.
    PICO_PROBE_FAULT = 0x0000014D
    # The probe has not been identified.
    PICO_PROBE_IDENTITY_UNKNOWN = 0x0000014E
    # Enabling the probe would cause the device to exceed the allowable current limit.
    PICO_PROBE_POWER_DC_POWER_SUPPLY_REQUIRED = 0x0000014F
    # The DC power supply is connected; enabling the probe would cause the device to exceed the
    # allowable current limit.
    PICO_PROBE_NOT_POWERED_WITH_DC_POWER_SUPPLY = 0x00000150
    # Failed to complete probe configuration.
    PICO_PROBE_CONFIG_FAILURE = 0x00000151
    # Failed to set the callback function, as currently in current callback function.
    PICO_PROBE_INTERACTION_CALLBACK = 0x00000152
    # The probe has been verified but not known on this driver.
    PICO_UNKNOWN_INTELLIGENT_PROBE = 0x00000153
    # The intelligent probe cannot be verified.
    PICO_INTELLIGENT_PROBE_CORRUPT = 0x00000154
    # The callback is null, probe collection will only start when
    # first callback is a none null pointer.
    PICO_PROBE_COLLECTION_NOT_STARTED = 0x00000155
    # The current drawn by the probe(s) has exceeded the allowed limit.
    PICO_PROBE_POWER_CONSUMPTION_EXCEEDED = 0x00000156
    # The channel range limits have changed due to connecting or disconnecting a probe
    # the channel has been enabled.
    PICO_WARNING_PROBE_CHANNEL_OUT_OF_SYNC = 0x00000157
    PICO_ENDPOINT_MISSING = 0x00000158
    PICO_UNKNOWN_ENDPOINT_REQUEST = 0x00000159
    # The ADC on board the device has not been correctly identified.
    PICO_ADC_TYPE_ERROR = 0x0000015A
    PICO_FPGA2_FAILED = 0x0000015B
    PICO_FPGA2_DEVICE_STATUS = 0x0000015C
    PICO_ENABLE_PROGRAM_FPGA2_FAILED = 0x0000015D
    PICO_NO_CHANNELS_OR_PORTS_ENABLED = 0x0000015E
    PICO_INVALID_RATIO_MODE = 0x0000015F
    PICO_READS_NOT_SUPPORTED_IN_CURRENT_CAPTURE_MODE = 0x00000160
    # These selection tests can be masked together to show that mode than one read selection has failed the tests,
    # therefore theses error codes cover 0x00000161UL to 0x0000016FUL.
    PICO_TRIGGER_READ_SELECTION_CHECK_FAILED = 0x00000161
    PICO_DATA_READ1_SELECTION_CHECK_FAILED = 0x00000162
    PICO_DATA_READ2_SELECTION_CHECK_FAILED = 0x00000164
    PICO_DATA_READ3_SELECTION_CHECK_FAILED = 0x00000168
    # The requested read is not one of the reads available in enPicoReadSelection.
    PICO_READ_SELECTION_OUT_OF_RANGE = 0x00000170
    # The downsample ratio options cannot be combined together for this request.
    PICO_MULTIPLE_RATIO_MODES = 0x00000171
    # The enPicoReadSelection request has no samples available.
    PICO_NO_SAMPLES_READ = 0x00000172
    # The enPicoReadSelection did not include one of the downsample ratios now requested.
    PICO_RATIO_MODE_NOT_REQUESTED = 0x00000173
    # No read requests have been made.
    PICO_NO_USER_READ_REQUESTS_SET = 0x00000174
    # The parameter for <number of values> cannot be zero.
    PICO_ZERO_SAMPLES_INVALID = 0x00000175
    # The analog hardware cannot be identified; contact Pico Technology Technical Support.
    PICO_ANALOGUE_HARDWARE_MISSING = 0x00000176
    # Setting of the analog hardware pins failed.
    PICO_ANALOGUE_HARDWARE_PINS = 0x00000177
    # An SMPS fault has occurred.
    PICO_ANALOGUE_HARDWARE_SMPS_FAULT = 0x00000178
    # There appears to be a conflict between the expected and actual hardware in the device; contact Pico Technology Technical Support.
    PICO_DIGITAL_ANALOGUE_HARDWARE_CONFLICT = 0x00000179
    # One or more of the enPicoRatioMode requested do not have a data buffer set.
    PICO_RATIO_MODE_BUFFER_NOT_SET = 0x0000017A
    # The resolution is valid but not supported by the opened device.
    PICO_RESOLUTION_NOT_SUPPORTED_BY_VARIANT = 0x0000017B
    # The requested trigger threshold is out of range for the current device resolution.
    PICO_THRESHOLD_OUT_OF_RANGE = 0x0000017C
    # The simple trigger only supports upper edge direction options.
    PICO_INVALID_SIMPLE_TRIGGER_DIRECTION = 0x0000017D
    # The aux trigger is not supported on this variant.
    PICO_AUX_NOT_SUPPORTED = 0x0000017E
    # The trigger directions pointer may not be null.
    PICO_NULL_DIRECTIONS = 0x0000017F
    # The trigger channel properties pointer may not be null.
    PICO_NULL_CHANNEL_PROPERTIES = 0x00000180
    # A trigger is set on a channel that has not been enabled.
    PICO_TRIGGER_CHANNEL_NOT_ENABLED = 0x00000181
    # A trigger condition has been set but a trigger property not set.
    PICO_CONDITION_HAS_NO_TRIGGER_PROPERTY = 0x00000182
    # When requesting trigger data, this option can only be combined with the segment header ratio mode flag.
    PICO_RATIO_MODE_TRIGGER_MASKING_INVALID = 0x00000183
    # The trigger data buffer must be 40 or more samples in size.
    PICO_TRIGGER_DATA_REQUIRES_MIN_BUFFER_SIZE_OF_40_SAMPLES = 0x00000184
    # The number of requested waveforms is greater than the number of memory segments allocated.
    PICO_NO_OF_CAPTURES_OUT_OF_RANGE = 0x00000185
    # When requesting segment header information, the segment header does not require a data buffer,
    # to get the segment information use GetTriggerInfo.
    PICO_RATIO_MODE_SEGMENT_HEADER_DOES_NOT_REQUIRE_BUFFERS = 0x00000186
    # Use GetTriggerInfo to retrieve the segment header information.
    PICO_FOR_SEGMENT_HEADER_USE_GETTRIGGERINFO = 0x00000187
    # A read request has not been set.
    PICO_READ_NOT_SET = 0x00000188
    # The expected and actual states of the ADCs do not match.
    PICO_ADC_SETTING_MISMATCH = 0x00000189
    # The requested data type is not one of the enPicoDataType listed.
    PICO_DATATYPE_INVALID = 0x0000018A
    # The down sample ratio mode requested does not support the enPicoDataType option chosen.
    PICO_RATIO_MODE_DOES_NOT_SUPPORT_DATATYPE = 0x0000018B
    # The channel combination is not valid for the resolution.
    PICO_CHANNEL_COMBINATION_NOT_VALID_IN_THIS_RESOLUTION = 0x0000018C
    PICO_USE_8BIT_RESOLUTION = 0x0000018D
    # The buffer for minimum data values and maximum data values are the same buffers.
    PICO_AGGREGATE_BUFFERS_SAME_POINTER = 0x0000018E
    # The read request number of samples requested for an overlapped operation are more
    # than the total number of samples to capture.
    PICO_OVERLAPPED_READ_VALUES_OUT_OF_RANGE = 0x0000018F
    # The overlapped read request has more segments specified than segments allocated.
    PICO_OVERLAPPED_READ_SEGMENTS_OUT_OF_RANGE = 0x00000190
    # The number of channel combinations available are greater than the array size received.
    PICO_CHANNELFLAGSCOMBINATIONS_ARRAY_SIZE_TOO_SMALL = 0x00000191
    # The number of captures is larger than the maximum number of segments allowed for the device variant.
    PICO_CAPTURES_EXCEEDS_NO_OF_SUPPORTED_SEGMENTS = 0x00000192
    # The time unit requested is not one of the listed enPicoTimeUnits.
    PICO_TIME_UNITS_OUT_OF_RANGE = 0x00000193
    # The number of samples parameter may not be zero.
    PICO_NO_SAMPLES_REQUESTED = 0x00000194
    # The action requested is not listed in enPicoAction.
    PICO_INVALID_ACTION = 0x00000195
    # When adding buffers for the same read request the buffers for all ratio mode requests have to be the same size.
    PICO_NO_OF_SAMPLES_NEED_TO_BE_EQUAL_WHEN_ADDING_BUFFERS = 0x00000196
    # The data is being processed but there is no empty data buffers available, a new data buffer needs to be set sent to the driver
    # so that the data can be processed.
    PICO_WAITING_FOR_DATA_BUFFERS = 0x00000197
    # when streaming data, only one read option is available.
    PICO_STREAMING_ONLY_SUPPORTS_ONE_READ = 0x00000198
    # A clear read request is not one of the enPicoAction listed.
    PICO_CLEAR_DATA_BUFFER_INVALID = 0x00000199
    # The combination of action flags are not allowed.
    PICO_INVALID_ACTION_FLAGS_COMBINATION = 0x0000019A
    #  PICO_ADD request has been made but both data buffers are set to null and so there is nowhere to put the data.
    PICO_BOTH_MIN_AND_MAX_NULL_BUFFERS_CANNOT_BE_ADDED = 0x0000019B
    # A conflict between the data buffers being set has occurred. Please use the PICO_CLEAR_ALL action to reset.
    PICO_CONFLICT_IN_SET_DATA_BUFFERS_CALL_REMOVE_DATA_BUFFER_TO_RESET = 0x0000019C
    # While processing data, buffers cannot be removed from the data buffers list.
    PICO_REMOVING_DATA_BUFFER_ENTRIES_NOT_ALLOWED_WHILE_DATA_PROCESSING = 0x0000019D
    #  An USB request has failed.
    PICO_CYUSB_REQUEST_FAILED = 0x00000200
    # A request has been made to retrieve the latest streaming data, but with either a null pointer or an array size set to zero.
    PICO_STREAMING_DATA_REQUIRED = 0x00000201
    # A buffer being set has a length that is invalid (ie less than zero).
    PICO_INVALID_NUMBER_OF_SAMPLES = 0x00000202
    # The distribution size may not be zero.
    PICO_INVALID_DISTRIBUTION = 0x00000203
    # The buffer length in bytes is greater than a 4-byte word.
    PICO_BUFFER_LENGTH_GREATER_THAN_INT32_T = 0x00000204
    # The PLL has failed.
    PICO_PLL_MUX_OUT_FAILED = 0x00000209
    # Pulse width only supports one direction.
    PICO_ONE_PULSE_WIDTH_DIRECTION_ALLOWED = 0x0000020A
    # There is no external trigger available on the device specified by the handle.
    PICO_EXTERNAL_TRIGGER_NOT_SUPPORTED = 0x0000020B
    # The condition parameter is a null pointer.
    PICO_NO_TRIGGER_CONDITIONS_SET = 0x0000020C
    # The number of trigger channel properties it outside the allowed range (is less than zero).
    PICO_NO_OF_CHANNEL_TRIGGER_PROPERTIES_OUT_OF_RANGE = 0x0000020D
    # A probe has been plugged into a channel, but can not be identified correctly.
    PICO_PROBE_COMPONENT_ERROR = 0x0000020E
    # The probe is incompatible with the device channel it is connected to. This could lead to error in the measurements.
    PICO_INCOMPATIBLE_PROBE = 0x0000020F
    # The requested channel for ETS triggering is not supported.
    PICO_INVALID_TRIGGER_CHANNEL_FOR_ETS = 0x00000210
    # While the device is streaming the get values method is not available
    PICO_NOT_AVAILABLE_WHEN_STREAMING_IS_RUNNING = 0x00000211
    # the requested state is not one of the enSharedTriggerWithinPreTrigger values
    PICO_INVALID_TRIGGER_WITHIN_PRE_TRIGGER_STATE = 0x00000212
    # the number of captures have to be greater than zero
    PICO_ZERO_NUMBER_OF_CAPTURES_INVALID = 0x00000213
    # the quantifier for a pointer, defining the length in bytes is invalid
    PICO_INVALID_LENGTH = 0x00000214
    # the trigger delay is greater than supported by the hardware
    PICO_TRIGGER_DELAY_OUT_OF_RANGE = 0x00000300
    # the requested threshold direction is not allowed with the specified channel
    PICO_INVALID_THRESHOLD_DIRECTION = 0x00000301
    # the requested threshold mode is not allowed with the specified channel
    PICO_INVALID_THRESHOLD_MODE = 0x00000302
    # The timebase is not supported or is invalid.
    PICO_TIMEBASE_NOT_SUPPORTED_BY_RESOLUTION = 0x00000303
    # The device variant is not supported by this current driver.
    PICO_INVALID_VARIANT = 0x00001000
    # The actual memory module does not match the expected memory module.
    PICO_MEMORY_MODULE_ERROR = 0x00001001
    # A null pointer has been passed in the trigger function or one of the parameters is out of range.
    PICO_PULSE_WIDTH_QUALIFIER_LOWER_UPPER_CONFILCT = 0x00002000
    # The pulse width qualifier type is not one of the listed options.
    PICO_PULSE_WIDTH_QUALIFIER_TYPE = 0x00002001
    # The pulse width qualifier direction is not one of the listed options.
    PICO_PULSE_WIDTH_QUALIFIER_DIRECTION = 0x00002002
    # The threshold range is not one of the listed options.
    PICO_THRESHOLD_MODE_OUT_OF_RANGE = 0x00002003
    # The trigger direction and pulse width option conflict with each other.
    PICO_TRIGGER_AND_PULSEWIDTH_DIRECTION_IN_CONFLICT = 0x00002004
    # The thresholds upper limits and thresholds lower limits conflict with each other.
    PICO_THRESHOLD_UPPER_LOWER_MISMATCH = 0x00002005
    # The pulse width lower count is out of range.
    PICO_PULSE_WIDTH_LOWER_OUT_OF_RANGE = 0x00002006
    # The pulse width upper count is out of range.
    PICO_PULSE_WIDTH_UPPER_OUT_OF_RANGE = 0x00002007
    # The devices front panel has caused an error.
    PICO_FRONT_PANEL_ERROR = 0x00002008
    # The actual and expected mode of the front panel do not match.
    PICO_FRONT_PANEL_MODE = 0x0000200B
    # A front panel feature is not available or failed to configure.
    PICO_FRONT_PANEL_FEATURE = 0x0000200C
    # When setting the pulse width conditions either the pointer is null or the number of conditions is set to zero.
    PICO_NO_PULSE_WIDTH_CONDITIONS_SET = 0x0000200D
    # a trigger condition exists for a port, but the port has not been enabled
    PICO_TRIGGER_PORT_NOT_ENABLED = 0x0000200E
    # a trigger condition exists for a port, but no digital channel directions have been set
    PICO_DIGITAL_DIRECTION_NOT_SET = 0x0000200F
    PICO_I2C_DEVICE_INVALID_READ_COMMAND = 0x00002010
    PICO_I2C_DEVICE_INVALID_RESPONSE = 0x00002011
    PICO_I2C_DEVICE_INVALID_WRITE_COMMAND = 0x00002012
    PICO_I2C_DEVICE_ARGUMENT_OUT_OF_RANGE = 0x00002013
    # The actual and expected mode do not match.
    PICO_I2C_DEVICE_MODE = 0x00002014
    # While trying to configure the device, set up failed.
    PICO_I2C_DEVICE_SETUP_FAILED = 0x00002015
    # A feature is not available or failed to configure.
    PICO_I2C_DEVICE_FEATURE = 0x00002016
    # The device did not pass the validation checks.
    PICO_I2C_DEVICE_VALIDATION_FAILED = 0x00002017
    PICO_INTERNAL_HEADER_ERROR = 0x00002018
    # The device couldn't write the channel settings due to a hardware fault
    PICO_FAILED_TO_WRITE_HARDWARE_FAULT = 0x00002019
    # The number of MSO's edge transitions being set is not supported by this device (RISING, FALLING, or RISING_OR_FALLING).
    PICO_MSO_TOO_MANY_EDGE_TRANSITIONS_WHEN_USING_PULSE_WIDTH = 0x00003000
    # A probe LED position requested is not one of the available probe positions in the ProbeLedPosition enum.
    PICO_INVALID_PROBE_LED_POSITION = 0x00003001
    # The LED position is not supported by the selected variant.
    PICO_PROBE_LED_POSITION_NOT_SUPPORTED = 0x00003002
    # A channel has more than one of the same LED position in the ProbeChannelLedSetting struct.
    PICO_DUPLICATE_PROBE_CHANNEL_LED_POSITION = 0x00003003
    # Setting the probes LED has failed.
    PICO_PROBE_LED_FAILURE = 0x00003004
    # Probe is not supported by the selected variant.
    PICO_PROBE_NOT_SUPPORTED_BY_THIS_DEVICE = 0x00003005
    # The probe name is not in the list of enPicoConnectProbe enums.
    PICO_INVALID_PROBE_NAME = 0x00003006
    # The number of colour settings are zero or a null pointer passed to the function.
    PICO_NO_PROBE_COLOUR_SETTINGS = 0x00003007
    # Channel has no probe connected to it.
    PICO_NO_PROBE_CONNECTED_ON_REQUESTED_CHANNEL = 0x00003008
    # Connected probe does not require calibration.
    PICO_PROBE_DOES_NOT_REQUIRE_CALIBRATION = 0x00003009
    # Connected probe could not be calibrated - hardware fault is a possible cause.
    PICO_PROBE_CALIBRATION_FAILED = 0x0000300A
    # A probe has been connected, but the version is not recognised.
    PICO_PROBE_VERSION_ERROR = 0x0000300B
    # The channel with the frequency counter enabled has a probe connected that does not support this feature
    PICO_PROBE_DOES_NOT_SUPPORT_FREQUENCY_COUNTER = 0x0000300C
    # The requested trigger time is to long for the selected variant.
    PICO_AUTO_TRIGGER_TIME_TOO_LONG = 0x00004000
    # The MSO pod did not pass the validation checks.
    PICO_MSO_POD_VALIDATION_FAILED = 0x00005000
    # No MSO pod found on the requested digital port.
    PICO_NO_MSO_POD_CONNECTED = 0x00005001
    # the digital port enum value is not in the enPicoDigitalPortHysteresis declaration
    PICO_DIGITAL_PORT_HYSTERESIS_OUT_OF_RANGE = 0x00005002
    PICO_MSO_POD_FAILED_UNIT = 0x00005003
    # The device's EEPROM is corrupt. Contact Pico Technology support: https://www.picotech.com/tech-support.
    PICO_ATTENUATION_FAILED = 0x00005004
    # a channel set to the 50Ohm Path has Tripped due to the input signal
    PICO_DC_50OHM_OVERVOLTAGE_TRIPPED = 0x00005005
    # The MSO pod over current protection activated, unplug and replug the MSO pod
    PICO_MSO_OVER_CURRENT_TRIPPED = 0x00005006
    # Status error for when the device has overheated.
    PICO_NOT_RESPONDING_OVERHEATED = 0x00005010
    # The USB version of the port is not supported by this variant
    PICO_USB_VERSION_NOT_SUPPORTED = 0x00005100
    # waiting for the device to capture timed out
    PICO_HARDWARE_CAPTURE_TIMEOUT = 0x00006000
    # waiting for the device be ready for capture timed out
    PICO_HARDWARE_READY_TIMEOUT = 0x00006001
    # the driver is performing a capture requested by RunStreaming or RunBlock
    # to interrupt this capture call Stop on the device first
    PICO_HARDWARE_CAPTURING_CALL_STOP = 0x00006002
    # the number of samples is less than the minimum number allowed
    PICO_TOO_FEW_REQUESTED_STREAMING_SAMPLES = 0x00007000
    # a streaming capture has been made but re-reading the data is not allowed
    PICO_STREAMING_REREAD_DATA_NOT_AVAILABLE = 0x00007001
    # When requesting data only Raw and one of the following aggregation data types allowed
    #   - PICO_RATIO_MODE_AGGREGATE (Min Max),
    #     PICO_RATIO_MODE_DECIMATE,
    #     PICO_RATIO_MODE_AVERAGE and/or PICO_RATIO_MODE_SUM,
    #     PICO_RATIO_MODE_DISTRIBUTION
    # average and sum are classed as one aggregation type
    PICO_STREAMING_COMBINATION_OF_RAW_DATA_AND_ONE_AGGREGATION_DATA_TYPE_ALLOWED = (
        0x00007002
    )
    # The time stamp per waveform segment has been reset.
    PICO_DEVICE_TIME_STAMP_RESET = 0x01000000
    # When requesting the TriggerTimeOffset the trigger time has not been set.
    PICO_TRIGGER_TIME_NOT_REQUESTED = 0x02000001
    # Trigger time buffer not set.
    PICO_TRIGGER_TIME_BUFFER_NOT_SET = 0x02000002
    # The trigger time failed to be calculated.
    PICO_TRIGGER_TIME_FAILED_TO_CALCULATE = 0x02000004
    # The trigger time failed to be calculated.
    PICO_TRIGGER_WITHIN_A_PRE_TRIGGER_FAILED_TO_CALCULATE = 0x02000008
    # The trigger time stamp was not requested.
    PICO_TRIGGER_TIME_STAMP_NOT_REQUESTED = 0x02000100
    # RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION cannot have a buffer set
    PICO_RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION_DOES_NOT_REQUIRE_BUFFERS = (
        0x02200000
    )
    # it is not possible to set a buffer for RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION therefore
    # information is not available pertaining to samples
    PICO_RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION_DOES_NOT_HAVE_BUFFERS = 0x02200001
    # to get the trigger time use either GetTriggerInfo or GetTriggerTimeOffset api calls
    PICO_RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION_USE_GETTRIGGERINFO = 0x02200002
    # PICO_RATIO_MDOE_TRIGGER and RATIO_MODE_TRIGGER_DATA_FOR_TIME_CALCULATION is not supported in streaming capture
    PICO_STREAMING_DOES_NOT_SUPPORT_TRIGGER_RATIO_MODES = 0x02200003
    # only the PICO_TRIGGER_READ may be used to read PICO_RATIO_MODE_TRIGGER, and PICO_RATIO_MODE_TRIGGER_FOR_CALCULATION
    PICO_USE_THE_TRIGGER_READ = 0x02200004
    # one of the PICO_DATA_READs should be used to read:
    # PICO_RATIO_MODE_RAW
    # PICO_RATIO_MODE_AGGREGATE
    # PICO_RATIO_MODE_DECIMATE
    # PICO_RATIO_MODE_AVERAGE
    PICO_USE_A_DATA_READ = 0x02200005
    # trigger data always requires a PICO_INT16_T data type
    PICO_TRIGGER_READ_REQUIRES_INT16_T_DATA_TYPE = 0x02200006
    # a ratio mode passed to the API call requires the number of samples to be greater than zero
    PICO_RATIO_MODE_REQUIRES_NUMBER_OF_SAMPLES_TO_BE_SET = 0x02200007
    # Attempted to set up the signal generator with an inconsistent configuration.
    PICO_SIGGEN_SETTINGS_MISMATCH = 0x03000010
    # The signal generator has been partially reconfigured and the new settings must be applied before it can be paused or restarted.
    PICO_SIGGEN_SETTINGS_CHANGED_CALL_APPLY = 0x03000011
    # The wave type is not listed in enPicoWaveType.
    PICO_SIGGEN_WAVETYPE_NOT_SUPPORTED = 0x03000012
    # The trigger type is not listed in enSigGenTrigType.
    PICO_SIGGEN_TRIGGERTYPE_NOT_SUPPORTED = 0x03000013
    # The trigger source is not listed in enSigGenTrigSource.
    PICO_SIGGEN_TRIGGERSOURCE_NOT_SUPPORTED = 0x03000014
    # The filter state is not listed in enPicoSigGenFilterState.
    PICO_SIGGEN_FILTER_STATE_NOT_SUPPORTED = 0x03000015
    # The arbitrary waveform buffer is a null pointer.
    PICO_SIGGEN_NULL_PARAMETER = 0x03000020
    # The arbitrary waveform buffer length is zero.
    PICO_SIGGEN_EMPTY_BUFFER_SUPPLIED = 0x03000021
    # The sig gen voltage offset and peak to peak have not been set.
    PICO_SIGGEN_RANGE_NOT_SUPPLIED = 0x03000022
    # The sig gen arbitrary waveform buffer not been set.
    PICO_SIGGEN_BUFFER_NOT_SUPPLIED = 0x03000023
    # The sig gen frequency have not been set.
    PICO_SIGGEN_FREQUENCY_NOT_SUPPLIED = 0x03000024
    # The sig gen sweep information has not been set.
    PICO_SIGGEN_SWEEP_INFO_NOT_SUPPLIED = 0x03000025
    # The sig gen trigger information has not been set.
    PICO_SIGGEN_TRIGGER_INFO_NOT_SUPPLIED = 0x03000026
    # The sig gen clock frequency have not been set.
    PICO_SIGGEN_CLOCK_FREQ_NOT_SUPPLIED = 0x03000027
    # The sig gen arbitrary waveform buffer length is too long.
    PICO_SIGGEN_TOO_MANY_SAMPLES = 0x03000030
    # The duty cycle value is out of range.
    PICO_SIGGEN_DUTYCYCLE_OUT_OF_RANGE = 0x03000031
    # The number of cycles is out of range.
    PICO_SIGGEN_CYCLES_OUT_OF_RANGE = 0x03000032
    # The pre-scaler is out of range.
    PICO_SIGGEN_PRESCALE_OUT_OF_RANGE = 0x03000033
    # The sweep type is not listed in enPicoSweepType.
    PICO_SIGGEN_SWEEPTYPE_INVALID = 0x03000034
    # A mismatch has occurred while checking the sweeps wave type.
    PICO_SIGGEN_SWEEP_WAVETYPE_MISMATCH = 0x03000035
    # The sweeps or shots and trigger type are not valid when combined together.
    PICO_SIGGEN_INVALID_SWEEP_PARAMETERS = 0x03000036
    # The sweep and prescaler are not valid when combined together.
    PICO_SIGGEN_SWEEP_PRESCALE_NOT_SUPPORTED = 0x03000037
    # The potential applied to the AWG output exceeds the maximum voltage range of the AWG.
    PICO_AWG_OVER_VOLTAGE_RANGE = 0x03000038
    # The reference signal cannot be locked to.
    PICO_NOT_LOCKED_TO_REFERENCE_FREQUENCY = 0x03000039
    # (Linux only.) udev rules are incorrectly configured. The user does
    # not have read/write permissions on the device's file descriptor.
    PICO_PERMISSIONS_ERROR = 0x03000040
    # The digital ports without analog channels are only allowed in 8-bit resolution.
    PICO_PORTS_WITHOUT_ANALOGUE_CHANNELS_ONLY_ALLOWED_IN_8BIT_RESOLUTION = 0x03001000
    PICO_ANALOGUE_FRONTEND_MISSING = 0x03003001
    PICO_FRONT_PANEL_MISSING = 0x03003002
    PICO_ANALOGUE_FRONTEND_AND_FRONT_PANEL_MISSING = 0x03003003
    # The digital board has reported an error to the driver
    PICO_DIGITAL_BOARD_HARDWARE_ERROR = 0x03003800
    # checking if the firmware needs updating the updateRequired parameter is null
    PICO_FIRMWARE_UPDATE_REQUIRED_TO_USE_DEVICE_WITH_THIS_DRIVER = 0x03004000
    PICO_UPDATE_REQUIRED_NULL = 0x03004001
    PICO_FIRMWARE_UP_TO_DATE = 0x03004002
    PICO_FLASH_FAIL = 0x03004003
    PICO_INTERNAL_ERROR_FIRMWARE_LENGTH_INVALID = 0x03004004
    PICO_INTERNAL_ERROR_FIRMWARE_NULL = 0x03004005
    PICO_FIRMWARE_FAILED_TO_BE_CHANGED = 0x03004006
    PICO_FIRMWARE_FAILED_TO_RELOAD = 0x03004007
    PICO_FIRMWARE_FAILED_TO_BE_UPDATE = 0x03004008
    PICO_FIRMWARE_VERSION_OUT_OF_RANGE = 0x03004009
    PICO_OPTIONAL_BOOTLOADER_UPDATE_AVAILABLE_WITH_THIS_DRIVER = 0x03005000
    PICO_BOOTLOADER_VERSION_NOT_AVAILABLE = 0x03005001
    PICO_NO_APPS_AVAILABLE = 0x03008000
    PICO_UNSUPPORTED_APP = 0x03008001
    # the adc is powered down when trying to capture data
    PICO_ADC_POWERED_DOWN = 0x03002000
    # An internal error has occurred and a watchdog timer has been called.
    PICO_WATCHDOGTIMER = 0x10000000
    # The picoipp.dll has not been found.
    PICO_IPP_NOT_FOUND = 0x10000001
    # A function in the picoipp.dll does not exist.
    PICO_IPP_NO_FUNCTION = 0x10000002
    # The Pico IPP call has failed.
    PICO_IPP_ERROR = 0x10000003
    # Shadow calibration is not available on this device.
    PICO_SHADOW_CAL_NOT_AVAILABLE = 0x10000004
    # Shadow calibration is currently disabled.
    PICO_SHADOW_CAL_DISABLED = 0x10000005
    # Shadow calibration error has occurred.
    PICO_SHADOW_CAL_ERROR = 0x10000006
    # The shadow calibration is corrupt.
    PICO_SHADOW_CAL_CORRUPT = 0x10000007
    # The memory on board the device has overflowed.
    PICO_DEVICE_MEMORY_OVERFLOW = 0x10000008
    # The device Adc test failed.
    PICO_ADC_TEST_FAILURE = 0x10000010
    PICO_RESERVED_1 = 0x11000000
    # The PicoSource device is not ready to accept instructions.
    PICO_SOURCE_NOT_READY = 0x20000000
    PICO_SOURCE_INVALID_BAUD_RATE = 0x20000001
    PICO_SOURCE_NOT_OPENED_FOR_WRITE = 0x20000002
    PICO_SOURCE_FAILED_TO_WRITE_DEVICE = 0x20000003
    PICO_SOURCE_EEPROM_FAIL = 0x20000004
    PICO_SOURCE_EEPROM_NOT_PRESENT = 0x20000005
    PICO_SOURCE_EEPROM_NOT_PROGRAMMED = 0x20000006
    PICO_SOURCE_LIST_NOT_READY = 0x20000007
    PICO_SOURCE_FTD2XX_NOT_FOUND = 0x20000008
    PICO_SOURCE_FTD2XX_NO_FUNCTION = 0x20000009


class PICO_STRING_VALUE(IntEnum):
    PICO_SV_MEMORY = 0
    PICO_SV_MEMORY_NO_OF_SEGMENTS = 1
    PICO_SV_MEMORY_MAX_SAMPLES = 2
    PICO_SV_NO_OF_CHANNELS = 3
    PICO_SV_ARRAY_OF_CHANNELS = 4
    PICO_SV_CHANNEL = 5
    PICO_SV_CHANNEL_NAME = 6
    PICO_SV_CHANNEL_RANGE = 7
    PICO_SV_CHANNEL_COUPLING = 8
    PICO_SV_CHANNEL_ENABLED = 9
    PICO_SV_CHANNEL_ANALOGUE_OFFSET = 10
    PICO_SV_CHANNEL_FILTER = 11
    PICO_SV_TRIGGER = 12
    PICO_SV_TRIGGER_AUXIO_OUTPUT_ENABLED = 13
    PICO_SV_TRIGGER_AUTO_TRIGGER_MICROSECONDS = 14
    PICO_SV_TRIGGER_PROPERTIES = 15
    PICO_SV_NO_OF_TRIGGER_PROPERTIES = 16
    PICO_SV_TRIGGER_PROPERTIES_CHANNEL = 17
    PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_UPPER = 18
    PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_UPPER_HYSTERESIS = 19
    PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_LOWER = 20
    PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_LOWER_HYSTERESIS = 21
    PICO_SV_TRIGGER_PROPERTIES_THRESHOLD_MODE = 22
    PICO_SV_TRIGGER_ARRAY_OF_BLOCK_CONDITIONS = 23
    PICO_SV_TRIGGER_NO_OF_BLOCK_CONDITIONS = 24
    PICO_SV_TRIGGER_CONDITIONS = 25
    PICO_SV_TRIGGER_NO_OF_CONDITIONS = 26
    PICO_SV_TRIGGER_CONDITION_SOURCE = 27
    PICO_SV_TRIGGER_CONDITION_STATE = 28
    PICO_SV_TRIGGER_DIRECTION = 29
    PICO_SV_TRIGGER_NO_OF_DIRECTIONS = 30
    PICO_SV_TRIGGER_DIRECTION_CHANNEL = 31
    PICO_SV_TRIGGER_DIRECTION_DIRECTION = 32
    PICO_SV_TRIGGER_DELAY = 33
    PICO_SV_TRIGGER_DELAY_MS = 34
    PICO_SV_FREQUENCY_COUNTER = 35
    PICO_SV_FREQUENCY_COUNTER_ENABLED = 36
    PICO_SV_FREQUENCY_COUNTER_CHANNEL = 37
    PICO_SV_FREQUENCY_COUNTER_RANGE = 38
    PICO_SV_FREQUENCY_COUNTER_TRESHOLDMAJOR = 39
    PICO_SV_FREQUENCY_COUNTER_TRESHOLDMINOR = 40
    PICO_SV_PULSE_WIDTH_PROPERTIES = 41
    PICO_SV_PULSE_WIDTH_PROPERTIES_DIRECTION = 42
    PICO_SV_PULSE_WIDTH_PROPERTIES_LOWER = 43
    PICO_SV_PULSE_WIDTH_PROPERTIES_UPPER = 44
    PICO_SV_PULSE_WIDTH_PROPERTIES_TYPE = 45
    PICO_SV_PULSE_WIDTH_ARRAY_OF_BLOCK_CONDITIONS = 46
    PICO_SV_PULSE_WIDTH_NO_OF_BLOCK_CONDITIONS = 47
    PICO_SV_PULSE_WIDTH_CONDITIONS = 48
    PICO_SV_PULSE_WIDTH_NO_OF_CONDITIONS = 49
    PICO_SV_PULSE_WIDTH_CONDITIONS_SOURCE = 50
    PICO_SV_PULSE_WIDTH_CONDITIONS_STATE = 51
    PICO_SV_SAMPLE_PROPERTIES = 52
    PICO_SV_SAMPLE_PROPERTIES_PRE_TRIGGER_SAMPLES = 53
    PICO_SV_SAMPLE_PROPERTIES_POST_TRIGGER_SAMPLES = 54
    PICO_SV_SAMPLE_PROPERTIES_TIMEBASE = 55
    PICO_SV_SAMPLE_PROPERTIES_NO_OF_CAPTURES = 56
    PICO_SV_SAMPLE_PROPERTIES_RESOLUTION = 57
    PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED = 58
    PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_DOWN_SAMPLE_RATIO = 59
    PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_DOWN_SAMPLE_RATIO_MODE = 60
    PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_REQUERSTED_NO_OF_SAMPLES = 61
    PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_SEGMENT_INDEX_FROM = 62
    PICO_SV_SAMPLE_PROPERTIES_OVERLAPPED_SEGMENT_INDEX_TO = 63
    PICO_SV_SIGNAL_GENERATOR = 64
    PICO_SV_SIGNAL_GENERATOR_BUILT_IN = 65
    PICO_SV_SIGNAL_GENERATOR_BUILT_IN_WAVE_TYPE = 66
    PICO_SV_SIGNAL_GENERATOR_BUILT_IN_START_FREQUENCY = 67
    PICO_SV_SIGNAL_GENERATOR_BUILT_IN_STOP_FREQUENCY = 68
    PICO_SV_SIGNAL_GENERATOR_BUILT_IN_INCREMENT = 69
    PICO_SV_SIGNAL_GENERATOR_BUILT_IN_DWELL_TIME = 70
    PICO_SV_SIGNAL_GENERATOR_AWG = 71
    PICO_SV_SIGNAL_GENERATOR_AWG_START_DELTA_PHASE = 72
    PICO_SV_SIGNAL_GENERATOR_AWG_STOP_DELTA_PHASE = 73
    PICO_SV_SIGNAL_GENERATOR_AWG_DELTA_PHASE_INCREMENT = 74
    PICO_SV_SIGNAL_GENERATOR_AWG_DWELL_COUNT = 75
    PICO_SV_SIGNAL_GENERATOR_AWG_INDEX_MODE = 76
    PICO_SV_SIGNAL_GENERATOR_AWG_WAVEFORM_SIZE = 77
    PICO_SV_SIGNAL_GENERATOR_ARRAY_OF_AWG_WAVEFORM_VALUES = 78
    PICO_SV_SIGNAL_GENERATOR_OFFSET_VOLTAGE = 79
    PICO_SV_SIGNAL_GENERATOR_PK_TO_PK = 80
    PICO_SV_SIGNAL_GENERATOR_OPERATION = 81
    PICO_SV_SIGNAL_GENERATOR_SHOTS = 82
    PICO_SV_SIGNAL_GENERATOR_SWEEPS = 83
    PICO_SV_SIGNAL_GENERATOR_SWEEP_TYPE = 84
    PICO_SV_SIGNAL_GENERATOR_TRIGGER_TYPE = 85
    PICO_SV_SIGNAL_GENERATOR_TRIGGER_SOURCE = 86
    PICO_SV_SIGNAL_GENERATOR_EXT_IN_THRESHOLD = 87
    PICO_SV_ETS = 88
    PICO_SV_ETS_STATE = 89
    PICO_SV_ETS_CYCLE = 90
    PICO_SV_ETS_INTERLEAVE = 91
    PICO_SV_ETS_SAMPLE_TIME_PICOSECONDS = 92


PICO_STATUS_T = c_uint32


__all__ = (
    "PICO_INFO",
    "PICO_INFO_T",
    "PICO_STATUS",
    "PICO_STATUS_T",
)
