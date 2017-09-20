# shipMissileVelocityPirateFactionLight
#
# Used by:
# Ship: Corax
# Ship: Talwar
type = "passive"


def handler(fit, ship, context):
    fit.modules.filteredChargeBoost(lambda mod: mod.charge.requiresSkill("Light Missiles"),
                                    "maxVelocity", ship.getModifiedItemAttr("shipBonusRole7"))
