import socket
import signal
from logger import Logger
import json

from threading import Thread
from time import sleep, time

cursors = []
Logger.disable()


def _404():
    return {
        "status" : 404,
        "body": {
            "message": "Not found"
        }
    }

def _200(body={}):
    return {
        "status" : 200,
        "body": body
    }

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.logger = Logger("[Server]")
        self.logger.log(f"Listening on {self.host}:{self.port}...")
        self.sock.listen(5)


    def listen(self):
        while True:
            conn, addr = self.sock.accept()
            self.logger.log(f"Connection from {addr}")
            Thread(target=self.handle, args=(conn, addr)).start()
    
    def handle(self, conn, addr):
        logger = Logger(f"[{addr[0]}:{str(addr[1])}]")
        logger.log("Connected")

        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                except:
                    logger.warn("Exception while receiving data (Unexpected disconnect?)")
                    self.disconnect(conn, addr, logger)
                    break
                if not data:
                    self.disconnect(conn, addr, logger)
                    break   
                try:
                    data = data.decode()
                    data = json.loads(data)
                    logger.log(f"Received: {data}")
                    match data["method"]:
                        case "POST":
                            match data["body"]["id"]:
                                case "register":
                                    cursors.append({
                                        "id": addr,
                                        "name": data["body"]["name"],
                                        "position": data["body"]["position"]
                                    })
                                    response = _200()
                                    print(cursors)
                                case "move":
                                    for cursor in cursors:
                                        if cursor["id"] == addr:
                                            cursor["position"] = data["body"]["position"]
                                            break
                                    response = _200()
                                case _:
                                    response = _404()
                        case "GET":
                            match data["body"]["id"]:
                                case "positions":                      
                                    response = _200({"cursors": cursors})
                                case _:
                                    response = _404()
                        case _:
                            response = _404()


                    conn.sendall(json.dumps(response).encode())
                    logger.log(f"Sent: {response}")
                    
                except Exception as e:
                    logger.error(f"Error: {e}")
                    break
    
    def disconnect(self, conn, addr, logger):
        for cursor in cursors:
            if cursor["id"] == addr:
                cursors.remove(cursor)
                logger.log("Disconnected")
                break

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    server = Server("0.0.0.0", 5000)

    def sendCursor():
        while True:
            
            sleep(.1)
        

    server.listen()