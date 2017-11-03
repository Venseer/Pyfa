# missileSkillWarheadUpgradesExplosiveDamageBonus
#
# Used by:
# Implants named like: Agency Damage Booster (3 of 3)
# Skill: Warhead Upgrades
type = "passive"


def handler(fit, src, context):
    mod = src.level if "skill" in context else 1
    fit.modules.filteredChargeBoost(lambda mod: mod.charge.requiresSkill("Missile Launcher Operation"),
                                    "explosiveDamage", src.getModifiedItemAttr("damageMultiplierBonus") * mod)
