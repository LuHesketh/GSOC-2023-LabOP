import json
from json import JSONEncoder
import pyhamilton
import os
from pyhamilton import (
    HamiltonInterface,
    LayoutManager,
    Plate96,
    Tip96,
    initialize,
    hhs_start_shaker,
    hhs_stop_shaker,
    oemerr,
    resource_list_with_prefix,
    normal_logging,
    ResourceType,
)

from pyhamilton import (
    hhs_begin_monitoring,
    hhs_create_star_device,
    hhs_create_usb_device,
    hhs_end_monitoring,
    hhs_get_firmware_version,
    hhs_get_serial_num,
    hhs_get_shaker_param,
    hhs_get_shaker_speed,
    hhs_get_temp_param,
    hhs_get_temp,
    hhs_get_temp_state,
    hhs_send_firmware_cmd,
    hhs_set_plate_lock,
    hhs_stop_all_shakers,
    hhs_set_shaker_param,
    hhs_set_simulation,
    hhs_set_temp_param,
    hhs_set_usb_trace,
    hhs_start_all_shaker,
    hhs_start_all_shaker_timed,
    hhs_start_shaker,
    hhs_start_shaker_timed,
    hhs_start_temp_ctrl,
    hhs_stop_shaker,
    hhs_stop_temp_ctrl,
    hhs_terminate,
    hhs_wait_for_shaker,
    hhs_wait_for_temp_ctrl,
)


def shake_samples(
    device_num,
    hhs_begin_monitoring,
    hhs_start_temp_ctrl,
    hhs_start_shaker_timed,
    hhs_wait_for_shaker,
    hhs_wait_for_temp_ctrl,
    hhs_stop_shaker,
    hhs_stop_temp_ctrl,
    hhs_terminate,
):
    device_num = hhs_create_star_device(ham_int, used_node=1)

    device_num = 1

    hhs_begin_monitoring(ham_int, device_num, 10, 5, 0)  # correct parameters

    hhs_start_temp_ctrl(ham_int, device_num, 50, 0)  # correct parameters

    # heatershaker_start_all_shaker_timed

    hhs_start_shaker_timed(ham_int, device_num, 100, 5)  # correct parameters

    hhs_wait_for_shaker(ham_int, device_num)

    hhs_wait_for_temp_ctrl(ham_int, device_num)

    # heatershaker_stop_all_shakers

    hhs_stop_shaker(ham_int, device_num)

    hhs_stop_temp_ctrl(ham_int, device_num)

    # heatershaker_end_method

    hhs_terminate(ham_int)


if __name__ == "__main__":
    with HamiltonInterface(simulate=True) as ham_int:
        initialize(ham_int)

        device_num = hhs_create_star_device(ham_int, used_node=1)
        print(Heater_shaker_id)

        shake_samples(
            device_num,
            hhs_begin_monitoring,
            hhs_start_temp_ctrl,
            hhs_start_shaker_timed,
            hhs_wait_for_shaker,
            hhs_wait_for_temp_ctrl,
            hhs_stop_shaker,
            hhs_stop_temp_ctrl,
            hhs_terminate,
        )
