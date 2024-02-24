import station_pb2_grpc
import grpc
import station_pb2
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from concurrent import futures
import cassandra
import traceback
import time

class record:
    def __init__(self,tmin,tmax):
        self.tmin = tmin
        self.tmax = tmax
       
class StationServicer(station_pb2_grpc.StationServicer):
    def __init__(self):
        cluster = Cluster(['p6-db-1', 'p6-db-2', 'p6-db-3'])
        cluster.register_user_type('weather', 'station_record', record)
        self.cass = cluster.connect()
        self.cass.execute("use weather")
        self.insert_statement = self.cass.prepare("""INSERT INTO stations (id, date, record) VALUES(?,?,?) """)
        self.insert_statement.consistency_level = ConsistencyLevel.ONE
        self.max_statement = self.cass.prepare("""SELECT MAX(record.tmax) FROM stations WHERE id = ? """)
        self.max_statement.consistency_level = ConsistencyLevel.THREE
    def RecordTemps(self, request, context):
        try:
            self.cass.execute(self.insert_statement,(request.station, request.date, record(request.tmin,request.tmax)))
            err = ""
        except cassandra.Unavailable as e:
             err = 'need '+ str(e.required_replicas) +' replicas, but only have '+str(e.alive_replicas)
        except cassandra.cluster.NoHostAvailable as e:
            for node, error in e.errors.items():
                if isinstance(e, cassandra.Unavailable):
                     err = 'need '+ str(e.required_replicas) +' replicas, but only have '+str(e.alive_replicas)
        except:
            err= traceback.format_exc()
        return station_pb2.RecordTempsReply(error = err)
       
    def StationMax(self, request, context):
        tmaxres =0
        try:
            tmaxres = self.cass.execute(self.max_statement, (request.station,)).one()[0]
            err = ""
        except cassandra.Unavailable as e:
            err = 'need '+ str(e.required_replicas) +' replicas, but only have '+str(e.alive_replicas)
        except cassandra.cluster.NoHostAvailable as e:
            for node, error in e.errors.items():
                if isinstance(e, cassandra.Unavailable):
                    err ='need '+ str(e.required_replicas) +' replicas, but only have '+str(e.alive_replicas)
        except:
            print("Failed")
            err= "Failed" + str(traceback.format_exc())
        return station_pb2.StationMaxReply(tmax = tmaxres, error = err)
           
if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4), options=(('grpc.so_reuseport', 0),))
    station_pb2_grpc.add_StationServicer_to_server(StationServicer(), server)
    server.add_insecure_port('0.0.0.0:5440')
    print("Started", flush = True)
    server.start()
    server.wait_for_termination()