# shipBonusHeavyMissileKineticDamageCBC2
#
# Used by:
# Ship: Drake Navy Issue
type = "passive"


def handler(fit, src, context):
    fit.modules.filteredChargeBoost(lambda mod: mod.charge.requiresSkill("Heavy Missiles"), "kineticDamage",
                                    src.getModifiedItemAttr("shipBonusCBC2"), skill="Caldari Battlecruiser")
