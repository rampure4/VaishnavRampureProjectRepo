from concurrent import futures
import grpc
import station_pb2
import station_pb2_grpc
from concurrent import futures
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, ConsistencyLevel

class StationServicer(station_pb2_grpc.StationServicer):
    def __init__(self, session):
        self.session = session

    def RecordTemps(self, request, context):
        try:
            insert_statement = self.session.prepare("INSERT INTO weather.stations (station, date, tmax, tmin) VALUES (?, ?, ?, ?)")
            insert_statement.consistency_level = ConsistencyLevel.ONE

            for record in request.records:
                self.session.execute(
                    insert_statement,
                    (record.station, record.date, record.tmax, record.tmin)
                )

            return station_pb2.RecordTempsReply(error="")
        except Exception as e:
            return station_pb2.RecordTempsReply(error=str(e))

    def StationMax(self, request, context):
        try:
            max_statement = self.session.prepare("SELECT MAX(tmax) FROM weather.stations WHERE station = ?")
            max_statement.consistency_level = ConsistencyLevel.ONE

            result = self.session.execute(max_statement, (request.station,))
            max_tmax = result.one()[0]

            return station_pb2.StationMaxReply(max_tmax=max_tmax, error="")
        except Exception as e:
            return station_pb2.StationMaxReply(error=str(e))

def connect_to_cassandra():
    try:
        cluster = Cluster(['p6-db-1', 'p6-db-2', 'p6-db-3'])  # Use the service names
        session = cluster.connect('')  # Connect to the 'weather' keyspace

        return cluster, session
    except Exception as e:
        raise Exception("Failed to connect to Cassandra") from e

if __name__ == "__main__":
    cluster, session = connect_to_cassandra()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    station_pb2_grpc.add_StationServicer_to_server(StationServicer(session), server)
    server.add_insecure_port('[::]:5440')
    server.start()
    server.wait_for_termination()
