# shipBonusHeavyDroneHPPirateFaction
#
# Used by:
# Ship: Rattlesnake
type = "passive"


def handler(fit, ship, context):
    fit.drones.filteredItemBoost(lambda drone: drone.item.requiresSkill("Heavy Drone Operation"),
                                 "hp", ship.getModifiedItemAttr("shipBonusRole7"))
