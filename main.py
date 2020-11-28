import sc2

from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units
import random
from typing import Tuple, List

from examples.zerg.zerg_rush import ZergRushBot

class MyBot(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS = 65
        self.ITERATIONS_PER_MINUTE = 165

    async def on_step(self, iteration):
        self.iteration = iteration
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
        await self.army_atack()
        await self.expand()
        await self.reactive_depot()
        await self.scout()
                
    async def build_workers(self):
        if len(self.townhalls(UnitTypeId.COMMANDCENTER))*16 > len(self.units(SCV)):
            if len(self.units(SCV)) < self.MAX_WORKERS:
                for cc in self.townhalls(UnitTypeId.COMMANDCENTER):
                    if self.can_afford(UnitTypeId.SCV) and cc.is_idle:
                        self.do(cc.train(UnitTypeId.SCV))

    async def build_depots(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.random

        #if self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
            # depot_placement_positions = self.main_base_ramp.corner_depots | {self.main_base_ramp.depot_in_middle}
            # depots: Units = self.structures.of_type({UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED})
            # if depots:
            #     depot_placement_positions: Set[Point2] = {
            #         d for d in depot_placement_positions if depots.closest_distance_to(d) > 1
            #     }
            # if len(depot_placement_positions) == 0:
            #     return
            # # Choose any depot location
            # target_depot_location: Point2 = depot_placement_positions.pop()
            # workers: Units = self.workers.gathering
            # if workers:  # if workers were found
            #     worker: Unit = workers.random
            #     self.do(worker.build(UnitTypeId.SUPPLYDEPOT, target_depot_location))

        if self.supply_left < 6 and self.supply_used >= 14 and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                workers: Units = self.workers.gathering
                if workers:  # if workers were found
                    worker: Unit = workers.random
                    depot_placement_positions = self.main_base_ramp.depot_in_middle
                    depot_position = await self.find_placement(UnitTypeId.SUPPLYDEPOT, near=depot_placement_positions)
                    self.do(worker.build(UnitTypeId.SUPPLYDEPOT, depot_position))
    
    async def build_refinary(self):
        for cc in self.townhalls(UnitTypeId.COMMANDCENTER):
            if self.gas_buildings.amount < 2*len(self.townhalls(UnitTypeId.COMMANDCENTER)) and self.can_afford(UnitTypeId.REFINERY):
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
        for barrack in self.structures(UnitTypeId.BARRACKS):
            if  self.can_afford(UnitTypeId.MARINE) and self.supply_army < 10 and not self.already_pending(UnitTypeId.MARINE) and barrack.is_idle:
                self.train(UnitTypeId.MARINE, 1)
        for factory in self.structures(UnitTypeId.FACTORY):
            if  self.can_afford(UnitTypeId.HELLION) and self.supply_army < 20 and not self.already_pending(UnitTypeId.HELLION):
                self.train(UnitTypeId.HELLION, 1)

    async def expand(self):
        if self.townhalls(UnitTypeId.COMMANDCENTER).amount < (self.iteration/self.ITERATIONS_PER_MINUTE)/5 and self.can_afford(UnitTypeId.COMMANDCENTER):
            location = await self.get_next_expansion()
            workers: Units = self.workers.gathering
            if workers:  # if workers were found
                worker: Unit = workers.random
                self.do(worker.build(UnitTypeId.COMMANDCENTER, location))

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
        if self.structures(UnitTypeId.BARRACKS) and not self.structures(UnitTypeId.FACTORY) and self.can_afford(UnitTypeId.FACTORY) and not self.already_pending(UnitTypeId.FACTORY):
            workers: Units = self.workers.gathering
            if workers:  # if workers were found
                worker: Unit = workers.random
                factory_position = await self.find_placement(UnitTypeId.FACTORY, near=cc.position.towards(self.game_info.map_center, 8))
                self.do(worker.build(UnitTypeId.FACTORY, factory_position))

    async def build_starport(self):
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        if not ccs:
            return
        else:
            cc: Unit = ccs.first
        if self.structures(UnitTypeId.FACTORY) and self.structures(UnitTypeId.STARPORT).amount < 4 and self.can_afford(UnitTypeId.STARPORT) and not self.already_pending(UnitTypeId.FACTORY):
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

    async def reactive_depot(self):
        for depo in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depo) < 15:
                    break
            else:
                depo(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

        # Lower depos when no enemies are nearby
        for depo in self.structures(UnitTypeId.SUPPLYDEPOTLOWERED).ready:
            for unit in self.enemy_units:
                if unit.distance_to(depo) < 10:
                    depo(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
                    break

    def select_army_target(self,state):
        if len(self.enemy_units) > 0:
            return random.choice(self.enemy_units)

        elif len(self.enemy_structures) > 0:
            return random.choice(self.enemy_structures)

        else: 
            self.enemy_start_locations[0]

    async def army_atack(self):
        aggressive_units = {MARINE: [50, 5],
                            HELLION: [50, 3]}

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    self.do(s.attack(self.select_army_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        self.do(s.attack(random.choice(self.enemy_units)))

    def random_location_variance(self, enemy_start_location):
            x = enemy_start_location[0]
            y = enemy_start_location[1]

            x += ((random.randrange(-20, 20))/100) * enemy_start_location[0]
            y += ((random.randrange(-20, 20))/100) * enemy_start_location[1]

            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if x > self.game_info.map_size[0]:
                x = self.game_info.map_size[0]
            if y > self.game_info.map_size[1]:
                y = self.game_info.map_size[1]

            go_to = position.Point2(position.Pointlike((x,y)))
            return go_to

    async def scout(self):
        if len(self.units(REAPER)) > 0:
            scout = self.units(REAPER)[0]
            if scout.is_idle:
                enemy_location = self.enemy_start_locations[0]
                move_to = self.random_location_variance(enemy_location)
                print(move_to)
                await self.do(scout.move(move_to))

        else:
            for barrack in self.units(BARRACKS):
                if self.can_afford(REAPER):
                    print("treinando scout")
                    self.train(UnitTypeId.REAPER, 1)
        
def main():
    map = "AcropolisLE"
    sc2.run_game(
        sc2.maps.get(map),
        [Bot(Race.Terran, MyBot()), Computer(Race.Protoss, Difficulty.Hard)],
        realtime=False,
    )

if __name__ == "__main__":
    main()