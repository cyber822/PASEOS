from loguru import logger

from paseos.actors.base_actor import BaseActor

from .utils.set_log_level import set_log_level
from .paseos import PASEOS
from .actors.spacecraft_actor import SpacecraftActor
from .actors.ground_station_actor import GroundstationActor

set_log_level("DEBUG")

logger.debug("Loaded module.")


def init_sim(local_actor: BaseActor):
    logger.debug("Initializing simulation.")
    sim = PASEOS(local_actor=local_actor)
    return sim


__all__ = ["GroundstationActor", "SpacecraftActor"]
