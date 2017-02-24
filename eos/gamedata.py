# ===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of eos.
#
# eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with eos.  If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================

import re
import traceback

from sqlalchemy.orm import reconstructor

import eos.db
from eqBase import EqBase

try:
    from collections import OrderedDict
except ImportError:
    from utils.compat import OrderedDict


class Effect(EqBase):
    """
    The effect handling class, it is used to proxy and load effect handler code,
    as well as a container for extra information regarding effects coming
    from the gamedata db.

    @ivar ID: the ID of this effect
    @ivar name: The name of this effect
    @ivar description: The description of this effect, this is usualy pretty useless
    @ivar published: Wether this effect is published or not, unpublished effects are typicaly unused.
    """
    # Filter to change names of effects to valid python method names
    nameFilter = re.compile("[^A-Za-z0-9]")

    @reconstructor
    def init(self):
        """
        Reconstructor, composes the object as we grab it from the database
        """
        self.__generated = False
        self.__effectModule = None
        self.handlerName = re.sub(self.nameFilter, "", self.name).lower()

    @property
    def handler(self):
        """
        The handler for the effect,
        It is automaticly fetched from effects/<effectName>.py if the file exists
        the first time this property is accessed.
        """
        if not self.__generated:
            self.__generateHandler()

        return self.__handler

    @property
    def runTime(self):
        """
        The runTime that this effect should be run at.
        This property is also automaticly fetched from effects/<effectName>.py if the file exists.
        the possible values are:
        None, "early", "normal", "late"
        None and "normal" are equivalent, and are also the default.

        effects with an early runTime will be ran first when things are calculated,
        followed by effects with a normal runTime and as last effects with a late runTime are ran.
        """
        if not self.__generated:
            self.__generateHandler()

        return self.__runTime

    @property
    def activeByDefault(self):
        """
        The state that this effect should be be in.
        This property is also automaticly fetched from effects/<effectName>.py if the file exists.
        the possible values are:
        None, True, False

        If this is not set:
        We simply assume that missing/none = True, and set it accordingly
        (much as we set runTime to Normalif not otherwise set).
        Nearly all effect files will fall under this category.

        If this is set to True:
        We would enable it anyway, but hey, it's double enabled.
        No effect files are currently configured this way (and probably will never be).

        If this is set to False:
        Basically we simply skip adding the effect to the effect handler when the effect is called,
        much as if the run time didn't match or other criteria failed.
        """
        if not self.__generated:
            self.__generateHandler()

        return self.__activeByDefault

    @activeByDefault.setter
    def activeByDefault(self, value):
        """
        Just assign the input values to the activeByDefault attribute.
        You *could* do something more interesting here if you wanted.
        """
        self.__activeByDefault = value

    @property
    def type(self):
        """
        The type of the effect, automaticly fetched from effects/<effectName>.py if the file exists.

        Valid values are:
        "passive", "active", "projected", "gang", "structure"

        Each gives valuable information to eos about what type the module having
        the effect is. passive vs active gives eos clues about wether to module
        is activatable or not (duh!) and projected and gang each tell eos that the
        module can be projected onto other fits, or used as a gang booster module respectivly
        """
        if not self.__generated:
            self.__generateHandler()

        return self.__type

    @property
    def isImplemented(self):
        """
        Wether this effect is implemented in code or not,
        unimplemented effects simply do nothing at all when run
        """
        return self.handler != effectDummy

    def isType(self, type):
        """
        Check if this effect is of the passed type
        """
        return self.type is not None and type in self.type

    def __generateHandler(self):
        """
        Grab the handler, type and runTime from the effect code if it exists,
        if it doesn't, set dummy values and add a dummy handler
        """
        try:
            self.__effectModule = effectModule = __import__('eos.effects.' + self.handlerName, fromlist=True)
            try:
                self.__handler = getattr(effectModule, "handler")
            except AttributeError:
                print "effect {} exists, but no handler".format(self.handlerName)
                raise

            try:
                self.__runTime = getattr(effectModule, "runTime") or "normal"
            except AttributeError:
                self.__runTime = "normal"

            try:
                self.__activeByDefault = getattr(effectModule, "activeByDefault")
            except AttributeError:
                self.__activeByDefault = True

            try:
                t = getattr(effectModule, "type")
            except AttributeError:
                t = None

            t = t if isinstance(t, tuple) or t is None else (t,)
            self.__type = t
        except (ImportError, AttributeError):
            self.__handler = effectDummy
            self.__runTime = "normal"
            self.__activeByDefault = True
            self.__type = None
        except Exception as e:
            traceback.print_exc(e)

        self.__generated = True

    def getattr(self, key):
        if not self.__generated:
            self.__generateHandler()

        return getattr(self.__effectModule, key, None)


def effectDummy(*args, **kwargs):
    pass


class Item(EqBase):
    MOVE_ATTRS = (4,  # Mass
                  38,  # Capacity
                  161)  # Volume

    MOVE_ATTR_INFO = None

    @classmethod
    def getMoveAttrInfo(cls):
        info = getattr(cls, "MOVE_ATTR_INFO", None)
        if info is None:
            cls.MOVE_ATTR_INFO = info = []
            for id in cls.MOVE_ATTRS:
                info.append(eos.db.getAttributeInfo(id))

        return info

    def moveAttrs(self):
        self.__moved = True
        for info in self.getMoveAttrInfo():
            val = getattr(self, info.name, 0)
            if val != 0:
                attr = Attribute()
                attr.info = info
                attr.value = val
                self.__attributes[info.name] = attr

    @reconstructor
    def init(self):
        self.__race = None
        self.__requiredSkills = None
        self.__moved = False
        self.__offensive = None
        self.__assistive = None
        self.__overrides = None

    @property
    def attributes(self):
        if not self.__moved:
            self.moveAttrs()

        return self.__attributes

    def getAttribute(self, key, default=None):
        if key in self.attributes:
            return self.attributes[key].value
        else:
            return default

    def isType(self, type):
        for effect in self.effects.itervalues():
            if effect.isType(type):
                return True

        return False

    @property
    def overrides(self):
        if self.__overrides is None:
            self.__overrides = {}
            overrides = eos.db.getOverrides(self.ID)
            for x in overrides:
                if x.attr.name in self.__attributes:
                    self.__overrides[x.attr.name] = x

        return self.__overrides

    def setOverride(self, attr, value):
        from eos.saveddata.override import Override
        if attr.name in self.__overrides:
            override = self.__overrides.get(attr.name)
            override.value = value
        else:
            override = Override(self, attr, value)
            self.__overrides[attr.name] = override
        eos.db.save(override)

    def deleteOverride(self, attr):
        override = self.__overrides.pop(attr.name, None)
        eos.db.saveddata_session.delete(override)
        eos.db.commit()

    @property
    def requiredSkills(self):
        if self.__requiredSkills is None:
            # This import should be here to make sure it's fully initialized
            from eos import db
            requiredSkills = OrderedDict()
            self.__requiredSkills = requiredSkills
            # Map containing attribute IDs we may need for required skills
            # { requiredSkillX : requiredSkillXLevel }
            srqIDMap = {182: 277, 183: 278, 184: 279, 1285: 1286, 1289: 1287, 1290: 1288}
            combinedAttrIDs = set(srqIDMap.iterkeys()).union(set(srqIDMap.itervalues()))
            # Map containing result of the request
            # { attributeID : attributeValue }
            skillAttrs = {}
            # Get relevant attribute values from db (required skill IDs and levels) for our item
            for attrInfo in db.directAttributeRequest((self.ID,), tuple(combinedAttrIDs)):
                attrID = attrInfo[1]
                attrVal = attrInfo[2]
                skillAttrs[attrID] = attrVal
            # Go through all attributeID pairs
            for srqIDAtrr, srqLvlAttr in srqIDMap.iteritems():
                # Check if we have both in returned result
                if srqIDAtrr in skillAttrs and srqLvlAttr in skillAttrs:
                    skillID = int(skillAttrs[srqIDAtrr])
                    skillLvl = skillAttrs[srqLvlAttr]
                    # Fetch item from database and fill map
                    item = db.getItem(skillID)
                    requiredSkills[item] = skillLvl
        return self.__requiredSkills

    factionMap = {
        500001: "caldari",
        500002: "minmatar",
        500003: "amarr",
        500004: "gallente",
        500005: "jove",
        500010: "guristas",
        500011: "angel",
        500012: "blood",
        500014: "ore",
        500016: "sisters",
        500018: "mordu",
        500019: "sansha",
        500020: "serpentis"
    }

    @property
    def race(self):
        if self.__race is None:

            try:
                if self.category.categoryName == 'Structure':
                    self.__race = "upwell"
                else:
                    self.__race = self.factionMap[self.factionID]
            # Some ships (like few limited issue ships) do not have factionID set,
            # thus keep old mechanism for now
            except KeyError:
                # Define race map
                map = {1: "caldari",
                       2: "minmatar",
                       4: "amarr",
                       5: "sansha",  # Caldari + Amarr
                       6: "blood",  # Minmatar + Amarr
                       8: "gallente",
                       9: "guristas",  # Caldari + Gallente
                       10: "angelserp",  # Minmatar + Gallente, final race depends on the order of skills
                       12: "sisters",  # Amarr + Gallente
                       16: "jove",
                       32: "sansha",  # Incrusion Sansha
                       128: "ore"}
                # Race is None by default
                race = None
                # Check primary and secondary required skills' races
                if race is None:
                    skillRaces = tuple(filter(lambda rid: rid, (s.raceID for s in tuple(self.requiredSkills.keys()))))
                    if sum(skillRaces) in map:
                        race = map[sum(skillRaces)]
                        if race == "angelserp":
                            if skillRaces == (2, 8):
                                race = "angel"
                            else:
                                race = "serpentis"
                # Rely on item's own raceID as last resort
                if race is None:
                    race = map.get(self.raceID, None)
                # Store our final value
                self.__race = race
        return self.__race

    @property
    def assistive(self):
        """Detects if item can be used as assistance"""
        # Make sure we cache results
        if self.__assistive is None:
            assistive = False
            # Go through all effects and find first assistive
            for effect in self.effects.itervalues():
                if effect.info.isAssistance is True:
                    # If we find one, stop and mark item as assistive
                    assistive = True
                    break
            self.__assistive = assistive
        return self.__assistive

    @property
    def offensive(self):
        """Detects if item can be used as something offensive"""
        # Make sure we cache results
        if self.__offensive is None:
            offensive = False
            # Go through all effects and find first offensive
            for effect in self.effects.itervalues():
                if effect.info.isOffensive is True:
                    # If we find one, stop and mark item as offensive
                    offensive = True
                    break
            self.__offensive = offensive
        return self.__offensive

    def requiresSkill(self, skill, level=None):
        for s, l in self.requiredSkills.iteritems():
            if isinstance(skill, basestring):
                if s.name == skill and (level is None or l == level):
                    return True

            elif isinstance(skill, int) and (level is None or l == level):
                if s.ID == skill:
                    return True

            elif skill == s and (level is None or l == level):
                return True

            elif hasattr(skill, "item") and skill.item == s and (level is None or l == level):
                return True

        return False

    def __repr__(self):
        return "Item(ID={}, name={}) at {}".format(
            self.ID, self.name, hex(id(self))
        )


class MetaData(EqBase):
    pass


class EffectInfo(EqBase):
    pass


class AttributeInfo(EqBase):
    pass


class Attribute(EqBase):
    pass


class Category(EqBase):
    pass


class AlphaClone(EqBase):

    @reconstructor
    def init(self):
        self.skillCache = {}

        for x in self.skills:
            self.skillCache[x.typeID] = x

    def getSkillLevel(self, skill):
        if skill.item.ID in self.skillCache:
            return self.skillCache[skill.item.ID].level
        else:
            return None


class AlphaCloneSkill(EqBase):
    pass


class Group(EqBase):
    pass


class Icon(EqBase):
    pass


class MarketGroup(EqBase):

    def __repr__(self):
        return u"MarketGroup(ID={}, name={}, parent={}) at {}".format(
            self.ID, self.name, getattr(self.parent, "name", None), self.name, hex(id(self))
        ).encode('utf8')


class MetaGroup(EqBase):
    pass


class MetaType(EqBase):
    pass


class Unit(EqBase):
    pass


class Traits(EqBase):
    pass
