import sc2

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units

from typing import Tuple, List

class MyBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_depots()
        await self.build_refinary()
        await self.build_barrack()
        await self.build_base_army()
        await self.build_engineering_bay()
        await self.build_factory()
        await self.build_starport()
        await self.build_starport_techlab()
        await self.build_fusion_core()
        await self.train_BC()
        await self.BC_attack()
        await self.expand()
                

    async def build_workers(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        if self.can_afford(UnitTypeId.SCV) and self.workers.amount < 20 and cc.is_idle:
            self.do(cc.train(UnitTypeId.SCV))

    async def build_depots(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first      
        if self.supply_left < 6 and self.supply_used >= 14 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8)) 
    
    async def build_refinary(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        if self.gas_buildings.amount < 2 and self.can_afford(UnitTypeId.REFINERY):
            vgs: Units = self.vespene_geyser.closer_than(20, cc)
            for vg in vgs:
                if self.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
                    break
                worker: Unit = self.select_build_worker(vg.position)
                if worker is None: 
                    break

                worker.build(UnitTypeId.REFINERY, vg)
                break
        for refinery in self.gas_buildings:
            if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker: Units = self.workers.closer_than(10, refinery)
                if worker:
                    worker.random.gather(refinery)

    async def build_barrack(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        if not self.structures(UnitTypeId.BARRACKS) and self.can_afford(UnitTypeId.BARRACKS):
            await self.build(UnitTypeId.BARRACKS, near=cc.position.towards(self.game_info.map_center, 8))

    async def build_base_army(self):
        if self.structures(UnitTypeId.BARRACKS) and self.can_afford(UnitTypeId.MARINE) and self.supply_army < 30 and not self.already_pending(UnitTypeId.MARINE):
            self.train(UnitTypeId.MARINE, 1)

    async def expand(self):
        if self.minerals < 1000 and self.vespene < 500:
            location = await self.get_next_expansion()
            await self.build(UnitTypeId.COMMANDCENTER, near=location, max_distance=10, random_alternative=False, placement_step=1)

    async def build_engineering_bay(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        if self.can_afford(UnitTypeId.ENGINEERINGBAY) and not self.structures(UnitTypeId.ENGINEERINGBAY) :
            await self.build(UnitTypeId.ENGINEERINGBAY, near=cc.position.towards(self.game_info.map_center, 8))

    async def build_factory(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        if self.structures(UnitTypeId.BARRACKS) and not self.structures(UnitTypeId.FACTORY) and self.can_afford(UnitTypeId.FACTORY):
            await self.build(UnitTypeId.FACTORY, near=cc.position.towards(self.game_info.map_center, 8))

    async def build_starport(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        if self.structures(UnitTypeId.FACTORY) and not self.structures(UnitTypeId.STARPORT) and self.can_afford(UnitTypeId.STARPORT):
            await self.build(UnitTypeId.STARPORT, near=cc.position.towards(self.game_info.map_center, 8))

    async def build_fusion_core(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        
        if self.structures(UnitTypeId.STARPORT) and not self.structures(UnitTypeId.FUSIONCORE) and self.can_afford(UnitTypeId.FUSIONCORE):
            await self.build(UnitTypeId.FUSIONCORE, near=cc.position.towards(self.game_info.map_center, 8))

    async def train_BC(self):
        for sp in self.structures(UnitTypeId.STARPORT).idle:
                if sp.has_add_on:
                    if not self.can_afford(UnitTypeId.BATTLECRUISER):
                        break
                    sp.train(UnitTypeId.BATTLECRUISER)
        
    async def starport_points_to_build_addon(self,sp_position: Point2) -> List[Point2]:
            """ Return all points that need to be checked when trying to build an addon. Returns 4 points. """
            addon_offset: Point2 = Point2((2.5, -0.5))
            addon_position: Point2 = sp_position + addon_offset
            addon_points = [
                (addon_position + Point2((x - 0.5, y - 0.5))).rounded for x in range(0, 2) for y in range(0, 2)
            ]
            return addon_points
    
    async def build_starport_techlab(self):
        sp: Unit
        for sp in self.structures(UnitTypeId.STARPORT).ready.idle:
            if not sp.has_add_on and self.can_afford(UnitTypeId.STARPORTTECHLAB):
                addon_points = await self.starport_points_to_build_addon(sp.position)
                if all(
                    self.in_map_bounds(addon_point)
                    and self.in_placement_grid(addon_point)
                    and self.in_pathing_grid(addon_point)
                    for addon_point in addon_points
                ):
                    sp.build(UnitTypeId.STARPORTTECHLAB)

    async def select_target(self) -> Tuple[Point2, bool]:
        """ Select an enemy target the units should attack. """
        targets: Units = self.enemy_structures
        if targets:
            return targets.random.position, True

        targets: Units = self.enemy_units
        if targets:
            return targets.random.position, True

        if self.units and min([u.position.distance_to(self.enemy_start_locations[0]) for u in self.units]) < 5:
            return self.enemy_start_locations[0].position, False

        return self.mineral_field.random.position, False

    async def BC_attack(self):
        bcs: Units = self.units(UnitTypeId.BATTLECRUISER)
        if bcs:
            target, target_is_enemy_unit = await self.select_target()
            bc: Unit
            for bc in bcs:
                # Order the BC to attack-move the target
                if target_is_enemy_unit and (bc.is_idle or bc.is_moving):
                    bc.attack(target)
                # Order the BC to move to the target, and once the select_target returns an attack-target, change it to attack-move
                elif bc.is_idle:
                    bc.move(target)
def main():
    map = "AcropolisLE"
    sc2.run_game(
        sc2.maps.get(map),
        [Bot(Race.Terran, MyBot()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()
