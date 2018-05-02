# shipShieldEmResistance1CBC2
#
# Used by:
# Ship: Drake
# Ship: Nighthawk
# Ship: Vulture
type = "passive"


def handler(fit, ship, context):
    fit.ship.boostItemAttr("shieldEmDamageResonance", ship.getModifiedItemAttr("shipBonusCBC2"),
                           skill="Caldari Battlecruiser")
