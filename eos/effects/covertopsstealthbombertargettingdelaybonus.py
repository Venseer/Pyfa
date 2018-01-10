# covertOpsStealthBomberTargettingDelayBonus
#
# Used by:
# Ships from group: Black Ops (5 of 5)
# Ships from group: Stealth Bomber (5 of 5)
# Ship: Caedes
# Ship: Chremoas
# Ship: Endurance
# Ship: Etana
# Ship: Rabisu
type = "passive"


def handler(fit, ship, context):
    fit.modules.filteredItemForce(lambda mod: mod.item.group.name == "Cloaking Device",
                                  "cloakingTargetingDelay",
                                  ship.getModifiedItemAttr("covertOpsStealthBomberTargettingDelay"))
