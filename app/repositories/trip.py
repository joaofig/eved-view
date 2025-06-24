import pandas as pd

from tools.database.sqlite.EvedDb import EvedDb


def load_all_trips() -> pd.DataFrame:
    db = EvedDb()
    sql = """
        select      t.traj_id
        ,           t.vehicle_id
        ,           t.trip_id
        ,           t.length_m
        ,           t.dt_ini
        ,           t.dt_end
        ,           t.duration_s
        ,           v.engine
        ,           v.weight
        from        trajectory t
        inner join  vehicle v on v.vehicle_id = t.vehicle_id
    """
    return db.query_df(sql)


def load_signals(traj_id: int) -> pd.DataFrame:
    db = EvedDb()
    sql = """
        select      s.signal_id
        ,           s.day_num
        ,           s.time_stamp
        ,           s.vehicle_id
        ,           s.trip_id
        ,           s.latitude
        ,           s.longitude   
        ,           s.match_latitude
        ,           s.match_longitude
        ,           s.speed
        ,           s.elevation
        ,           s.elevation_smooth
        ,           s.gradient
        ,           s.h3_12
        from        signal s
        inner join  trajectory t on s.vehicle_id = t.vehicle_id AND s.trip_id = t.trip_id
        where       t.traj_id = ?
    """
    return db.query_df(sql, parameters=[traj_id])


def load_nodes(traj_id: int) -> pd.DataFrame:
    db = EvedDb()
    sql = """
        select      n.node_id
        ,           n.traj_id
        ,           n.latitude
        ,           n.longitude
        ,           n.h3_12
        ,           n.match_error
        from        node n
        where       n.traj_id = ?
    """
    return db.query_df(sql, parameters=[traj_id])
