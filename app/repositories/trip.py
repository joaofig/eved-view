import pandas as pd

from app.models.MapNode import MapNode
from app.models.Signal import Signal
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


def load_signals(traj_id: int) -> list[Signal]:
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
        inner join  trajectory t on s.vehicle_id = t.vehicle_id and s.trip_id = t.trip_id
        where       t.traj_id = ?
    """
    rows = db.query(sql, parameters=[traj_id])
    return [
        Signal(
            signal_id=int(row[0]),
            day_num=float(row[1]),
            timestamp=int(row[2]),
            vehicle_id=int(row[3]),
            trip_id=int(row[4]),
            lat=float(row[5]),
            lon=float(row[6]),
            match_lat=float(row[7]),
            match_lon=float(row[8]),
            speed=float(row[9]),
            elevation=float(row[10]),
            elevation_smooth=float(row[11]),
            gradient=row[12],
            h3_12=int(row[13])
        ) for row in rows
    ]


def load_nodes(traj_id: int) -> list[MapNode]:
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
    rows = db.query(sql, parameters=[traj_id])
    return [
        MapNode(
            node_id=int(row[0]),
            traj_id=int(row[1]),
            lat=float(row[2]),
            lon=float(row[3]),
            h3_12=int(row[4]),
            match_error=row[5]
        ) for row in rows
    ]