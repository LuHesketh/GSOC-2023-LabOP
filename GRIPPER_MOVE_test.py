import pyhamilton
import os
from pyhamilton import (HamiltonInterface,  LayoutManager, Plate96, Tip96, initialize, tip_pick_up, move_plate,
                        tip_eject, oemerr, aspirate, dispense, resource_list_with_prefix, normal_logging, ResourceType)


lmgr = LayoutManager('deck_.lay') # make sure you're inputing the right deck layout here
origin_place = lmgr.assign_unused_resource(ResourceType(Plate96, 'Cos_96_Filter_0001'))
destination_place = lmgr.assign_unused_resource(ResourceType(Plate96, 'PLT_CAR_L5MD_A00_0001'))

liq_class = 'StandardVolumeFilter_Water_DispenseJet_Part'




if __name__ == '__main__':
    with HamiltonInterface(simulate=True) as ham_int:
        initialize(ham_int)
        move_plate(ham_int, origin_place, destination_place)
