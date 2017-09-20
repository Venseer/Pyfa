# shipBonusLightDroneDamageMultiplierPirateFaction
#
# Used by:
# Ship: Whiptail
# Ship: Worm
type = "passive"


def handler(fit, ship, context):
    fit.drones.filteredItemBoost(lambda drone: drone.item.requiresSkill("Light Drone Operation"),
                                 "damageMultiplier", ship.getModifiedItemAttr("shipBonusRole7"))
