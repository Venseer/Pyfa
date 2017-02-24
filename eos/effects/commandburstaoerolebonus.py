# commandBurstAoERoleBonus
#
# Used by:
# Ships from group: Carrier (4 of 4)
# Ships from group: Combat Battlecruiser (13 of 13)
# Ships from group: Command Ship (8 of 8)
# Ships from group: Force Auxiliary (4 of 4)
# Ships from group: Supercarrier (6 of 6)
# Ships from group: Titan (5 of 5)
# Subsystems named like: Defensive Warfare Processor (4 of 4)
# Ship: Orca
# Ship: Rorqual
type = "passive"


def handler(fit, src, context):
    fit.modules.filteredItemBoost(lambda mod: mod.item.requiresSkill("Leadership"), "maxRange",
                                  src.getModifiedItemAttr("roleBonusCommandBurstAoERange"))
