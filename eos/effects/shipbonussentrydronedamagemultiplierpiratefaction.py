# shipBonusSentryDroneDamageMultiplierPirateFaction
#
# Used by:
# Ships named like: Rattlesnake (2 of 2)
type = "passive"


def handler(fit, ship, context):
    fit.drones.filteredItemBoost(lambda drone: drone.item.requiresSkill("Sentry Drone Interfacing"),
                                 "damageMultiplier", ship.getModifiedItemAttr("shipBonusRole7"))
