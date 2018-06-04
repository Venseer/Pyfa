# warpDisruptSphere
#
# Used by:
# Modules from group: Warp Disrupt Field Generator (7 of 7)

# warpDisruptSphere
#
# Used by:
# Modules from group: Warp Disrupt Field Generator (7 of 7)
from eos.saveddata.module import State

type = "projected", "active"
runTime = "early"


def handler(fit, module, context):

    if "projected" in context:
        fit.ship.increaseItemAttr("warpScrambleStatus", module.getModifiedItemAttr("warpScrambleStrength"))
        if module.charge is not None and module.charge.ID == 45010:
            for mod in fit.modules:
                if not mod.isEmpty and mod.item.requiresSkill("High Speed Maneuvering") and mod.state > State.ONLINE:
                    mod.state = State.ONLINE
                if not mod.isEmpty and mod.item.requiresSkill("Micro Jump Drive Operation") and mod.state > State.ONLINE:
                    mod.state = State.ONLINE
    else:
        if module.charge is None:
            fit.ship.boostItemAttr("mass", module.getModifiedItemAttr("massBonusPercentage"))
            fit.ship.boostItemAttr("signatureRadius", module.getModifiedItemAttr("signatureRadiusBonus"))
            fit.modules.filteredItemBoost(lambda mod: mod.item.group.name == "Propulsion Module",
                                          "speedBoostFactor", module.getModifiedItemAttr("speedBoostFactorBonus"))
            fit.modules.filteredItemBoost(lambda mod: mod.item.group.name == "Propulsion Module",
                                      "speedFactor", module.getModifiedItemAttr("speedFactorBonus"))

        fit.ship.forceItemAttr("disallowAssistance", 1)
