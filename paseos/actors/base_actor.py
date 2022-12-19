from abc import ABC

from loguru import logger
import pykep as pk
import numpy as np
from skspatial.objects import Sphere
from dotmap import DotMap

from ..communication.get_communication_window import get_communication_window
from ..communication.is_in_line_of_sight import is_in_line_of_sight
from ..power.is_in_eclipse import is_in_eclipse


class BaseActor(ABC):
    """This (abstract) class is the baseline implementation of an actor
    (e.g. spacecraft, ground station) in the simulation. The abstraction allows
    some actors to have e.g. limited power (spacecraft) and others not to.
    """

    # Actor name, has to be unique
    name = None

    # Actor's mass in kg
    _mass = None

    # Timestep this actor's info is at (excl. pos/vel)
    _local_time = None

    # Orbital parameters of the actor, stored in a pykep planet object
    _orbital_parameters = None

    # Earth as a sphere (for now)
    # TODO replace this in the future depending on central body
    # Note that this needs to be specified in solar reference frame for now
    _central_body_sphere = Sphere([0, 0, 0], 6371000)

    # Central body this actor is orbiting
    _central_body = None

    # Communication links dictionary
    _communication_devices = DotMap(_dynamic=False)

    # Tracks the current activity
    _current_activity = None

    # The following variables are used to track last evaluated state vectors to avoid recomputation.
    _last_position = None
    _time_of_last_position = None
    _last_velocity = None
    _last_eclipse_status = None
    _time_of_last_eclipse_status = None
    _last_altitude = None

    def __init__(self, name: str, epoch: pk.epoch) -> None:
        """Constructor for a base actor

        Args:
            name (str): Name of this actor
            epoch (pykep.epoch): Current local time of the actor.
        """
        logger.trace("Instantiating Actor.")
        super().__init__()
        self.name = name
        self._local_time = epoch

        self._communication_devices = DotMap(_dynamic=False)

    @property
    def mass(self) -> float:
        """Returns actor's mass in kg.

        Returns:
            float: Mass
        """
        return self._mass

    @property
    def current_activity(self) -> str:
        """Returns the name of the activity the actor is currently performing.

        Returns:
            str: Activity name. None if no activity being performed.
        """
        return self._current_activity

    @property
    def local_time(self) -> pk.epoch:
        """Returns local time of the actor as pykep epoch. Use e.g. epoch.mjd2000 to get time in days.

        Returns:
            pk.epoch: local time of the actor
        """
        return self._local_time

    @property
    def communication_devices(self) -> DotMap:
        """Returns the communications devices.

        Returns:
            DotMap: Dictionary (DotMap) of communication devices.
        """
        return self._communication_devices

    @staticmethod
    def _check_init_value_sensibility(
        position,
        velocity,
    ):
        """A function to check user inputs for sensibility

        Args:
            position (list of floats): [x,y,z]
            velocity (list of floats): [vx,vy,vz]
        """
        logger.trace("Checking constructor values for sensibility.")
        assert len(position) == 3, "Position has to have 3 elements (x,y,z)"
        assert len(velocity) == 3, "Velocity has to have 3 elements (vx,vy,vz)"

    def __str__(self):
        return self._orbital_parameters.name

    def set_time(self, t: pk.epoch):
        """Updates the local time of the actor.

        Args:
            t (pk.epoch): Local time to set to.
        """
        self._local_time = t

    def charge(self, t0: pk.epoch, t1: pk.epoch):
        """Charges the actor during that period. Not implemented by default.

        Args:
            t0 (pk.epoch): Start of the charging interval
            t1 (pk.epoch): End of the charging interval

        """
        pass

    def discharge(self, consumption_rate_in_W: float, duration_in_s: float):
        """Discharge battery depending on power consumption. Not implemented by default.

        Args:
            consumption_rate_in_W (float): Consumption rate of the activity in Watt
            duration_in_s (float): How long the activity is performed in seconds
        """
        pass

    @property
    def altitude(
        self,
        t0: pk.epoch = None,
    ) -> float:
        """Returns altitude above [0,0,0]. Will only compute if not computed for this timestep.

        Args:
            t0 (pk.epoch): Epoch to get altitude at. Defaults to local time.

        Returns:
            float: Altitude in meters.
        """
        if t0 is None:
            t0 = self._local_time
        if (
            t0.mjd2000 == self._time_of_last_position
            and self._last_altitude is not None
        ):
            return self._last_altitude
        else:
            self._last_altitude = np.sqrt(np.sum(np.power(self.get_position(t0), 2)))
            return self._last_altitude

    def get_position(self, epoch: pk.epoch):
        logger.trace(
            "Computing "
            + self._orbital_parameters.name
            + " position at time "
            + str(epoch.mjd2000)
            + " (mjd2000)."
        )

        if self._orbital_parameters is not None and hasattr(self, "_position"):
            raise ValueError(
                "Ambiguous position definition. Either set an orbit OR position with ActorBuilder."
            )

        # If the actor has no orbit, return position
        if self._orbital_parameters is None:
            if self._position is not None:
                self._last_position = self._position
                self._time_of_last_position = epoch.mjd2000
                return self._position
        else:
            return self._orbital_parameters.eph(epoch)[0]

        raise NotImplementedError(
            "No suitable way added to determine actor position. Either set an orbit or position with ActorBuilder."
        )

    def get_position_velocity(self, epoch: pk.epoch):
        if self._orbital_parameters is None:
            raise NotImplementedError(
                "No suitable way added to determine actor velocity. Set an orbit with ActorBuilder."
            )

        logger.trace(
            "Computing "
            + self._orbital_parameters.name
            + " position / velocity at time "
            + str(epoch.mjd2000)
            + " (mjd2000)."
        )
        pos, vel = self._orbital_parameters.eph(epoch)
        self._last_position = pos
        self._last_velocity = vel
        self._time_of_last_position = epoch.mjd2000
        return pos, vel

    def is_in_line_of_sight(
        self, other_actor: "BaseActor", epoch: pk.epoch, plot=False
    ):
        """Determines whether a position is in line of sight of this actor

        Args:
            other_actor (BaseActor): The actor to check line of sight with
            epoch (pk,.epoch): Epoch at which to check the line of sight
            plot (bool): Whether to plot a diagram illustrating the positions.

        Returns:
            bool: true if in line-of-sight.
        """
        return is_in_line_of_sight(self, other_actor, epoch, plot)

    def is_in_eclipse(self, t: pk.epoch = None):
        """Checks if the actors is in eclipse at the specified time.

        Args:
            t (pk.epoch, optional): Time to check, if None will use current local actor time.
        """
        if t is None:
            t = self._local_time
        if t.mjd2000 == self._time_of_last_eclipse_status:
            return self._last_eclipse_status
        else:
            self._last_eclipse_status = is_in_eclipse(self, self._central_body, t)
            self._time_of_last_eclipse_status = t.mjd2000
        return self._last_eclipse_status

    def get_communication_window(
        self,
        local_actor_communication_link_name,
        target_actor,
        dt: float,
        t0: float,
        data_to_send_in_b: int,
        window_timeout_value_in_s=7200.0,
    ):
        """Returning the communication window and the data amount that can be transmitted from the local to the target actor.

        Args:
            local_actor_communication_link_name (base_actor):  name of the local_actor's communication link to use.
            target_actor (base_actor): other actor.
            dt (float): simulation timestep.
            t0 (pk.epoch): current simulation time [s].
            data_to_send_in_b (int): amount of data to transmit [b].
            window_timeout_value_in_s (float, optional): timeout for estimating the communication window. Defaults to 7200.0.
        Returns:
            pk.epoch: communication window start time.
            k.epoch: communication window end time.
            int: data that can be transmitted in the communication window [b].
        """
        return get_communication_window(
            self,
            local_actor_communication_link_name,
            target_actor,
            dt,
            t0,
            data_to_send_in_b,
            window_timeout_value_in_s,
        )
