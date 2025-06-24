# from src.db.AsyncEvedDb import AsyncEvedDb
# from src.db.AsyncMatchDb import AsyncMatchDb
# from src.ui.models.trip import TripModel
#
#
# async def get_noisy_trajectory(traj_id: int) -> TripModel:
#     db = AsyncEvedDb()
#     sql = """
#     select      s.latitude
#     ,           s.longitude
#     from        signal s
#     inner join  trajectory t on s.trip_id = t.trip_id and s.vehicle_id = t.vehicle_id
#     where       t.traj_id = ?
#     """
#     return TripModel(points=await db.query(sql, parameters=[traj_id]), color="orange")
#
#
# async def get_match_trajectory(traj_id: int) -> TripModel:
#     db = AsyncEvedDb()
#     sql = """
#     select      s.match_latitude
#     ,           s.match_longitude
#     from        signal s
#     inner join  trajectory t on s.trip_id = t.trip_id and s.vehicle_id = t.vehicle_id
#     where       t.traj_id = ?
#     """
#     return TripModel(points=await db.query(sql, parameters=[traj_id]))
#
#
# async def get_graph_trajectory(traj_id: int) -> TripModel:
#     db = AsyncMatchDb()
#     sql = """
#     select      n.latitude
#     ,           n.longitude
#     from        node n
#     where       n.traj_id = ? and n.match_error is null
#     """
#     return TripModel(points=await db.query(sql, parameters=[traj_id]), color="green")

