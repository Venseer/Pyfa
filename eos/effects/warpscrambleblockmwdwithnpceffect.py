# warpScrambleBlockMWDWithNPCEffect
#
# Used by:
# Modules named like: Warp Scrambler (26 of 26)

from eos.saveddata.module import State

runTime = "early"
type = "projected", "active"


def handler(fit, module, context):
    if "projected" not in context:
        return
    # this is such a dirty hack
    for mod in fit.modules:
        if not mod.isEmpty and mod.item.requiresSkill("High Speed Maneuvering") and mod.state > State.ONLINE:
            mod.state = State.ONLINE
