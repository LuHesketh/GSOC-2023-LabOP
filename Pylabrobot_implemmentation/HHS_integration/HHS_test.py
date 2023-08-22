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
    hhs_create_star_device,
    hhs_start_shaker_timed,
    hhs_start_temp_ctrl,
    hhs_stop_temp_ctrl,
    hhs_terminate,
    hhs_wait_for_shaker
)



def shake_samples(
    device_num,
    hhs_start_temp_ctrl,
    hhs_start_shaker_timed,
    hhs_wait_for_shaker,
    hhs_stop_temp_ctrl,
    hhs_terminate):

    hhs_start_temp_ctrl(ham_int, device_num, 50, 70)  # correct parameters

    # heatershaker_start_all_shaker_timed

    hhs_start_shaker_timed(ham_int, device_num, 100, 70)  # correct parameters

    hhs_wait_for_shaker(ham_int, device_num)

    # heatershaker_stop_all_shakers

    hhs_stop_temp_ctrl(ham_int, device_num)

    # heatershaker_end_method

    hhs_terminate(ham_int)


if __name__ == "__main__":
    with HamiltonInterface(simulate=True) as ham_int:
        initialize(ham_int)

        device_num = hhs_create_star_device(ham_int, used_node=1)
        device_num = 1

        shake_samples(
            device_num,
            hhs_start_temp_ctrl,
            hhs_start_shaker_timed,
            hhs_wait_for_shaker,
            hhs_stop_temp_ctrl,
            hhs_terminate
        )
