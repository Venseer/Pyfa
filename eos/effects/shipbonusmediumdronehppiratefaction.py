# shipBonusMediumDroneHPPirateFaction
#
# Used by:
# Ship: Chameleon
# Ship: Gila
type = "passive"


def handler(fit, ship, context):
    fit.drones.filteredItemBoost(lambda drone: drone.item.requiresSkill("Medium Drone Operation"),
                                 "hp", ship.getModifiedItemAttr("shipBonusRole7"))
