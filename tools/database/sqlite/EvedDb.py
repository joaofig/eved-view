import pandas as pd

from os import path
from tools.config import load_config
from tools.database.sqlite.BaseDb import BaseDb


class EvedDb(BaseDb):
    def __init__(self):
        config = load_config()
        database = config.get("database")
        filename = path.join(
            database.get("folder", "./data/eved.db"),
            database.get("eved", "eved.sqlite"),
        )
        super().__init__(db_name=filename)

    def insert_vehicles(self, vehicles):
        self.insert_list("sql/eved/insert_vehicle.sql", vehicles)

    def insert_signals(self, signals):
        self.insert_list("sql/eved/insert_signal.sql", signals)

    def create_trajectories(self):
        self.ddl_script("sql/eved/create_trajectory.sql")
        self.ddl_script("sql/eved/insert_trajectories.sql")
        self.ddl_script("sql/eved/create_trajectory_vehicle_index.sql")

    def get_vehicles(self) -> pd.DataFrame:
        sql = "SELECT vehicle_id, vehicle_type, vehicle_class FROM vehicle"
        return self.query_df(sql)

    def get_trajectories(self) -> pd.DataFrame:
        sql = """
        SELECT  traj_id
        ,       vehicle_id
        ,       trip_id
        ,       length_m
        ,       duration_s
        ,       dt_ini
        ,       dt_end
        ,       ROUND(length_m / 1000.0, 1) as km
        FROM    trajectory
        """
        return self.query_df(sql)

    def get_vehicle_trajectories(self, vehicle_id: int) -> pd.DataFrame:
        sql = "SELECT traj_id, vehicle_id, trip_id"
        return self.query_df(sql, parameters=[vehicle_id])

    def get_trajectory(self, traj_id: int) -> pd.DataFrame:
        sql = """
        SELECT      s.signal_id
        ,           s.vehicle_id
        ,           s.day_num
        ,           s.time_stamp
        ,           s.latitude
        ,           s.longitude   
        ,           s.match_latitude
        ,           s.match_longitude
        FROM        signal s
        INNER JOIN  trajectory t ON s.vehicle_id = t.vehicle_id AND s.trip_id = t.trip_id
        WHERE       t.traj_id = ?
        """
        return self.query_df(sql, parameters=[traj_id])
