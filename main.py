import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

from sc2.constants import UnitTypeId

class WorkerRushBot(sc2.BotAI):
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_refineries()

    async def build_refineries(self):
        # If we have no refinery, build refinery
        if (
            self.gas_buildings.amount + self.already_pending(UnitTypeId.REFINERY) == 0
            and self.can_afford(UnitTypeId.REFINERY)
            and self.workers
        ):
            scv: Unit = self.workers.random
            target: Unit = self.vespene_geyser.closest_to(scv)
            scv.build_gas(target)


run_game(maps.get("AcropolisLE"), [
    Bot(Race.Terran, WorkerRushBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)