import socket
import signal
from logger import Logger
import json
from threading import Thread
from time import sleep, time
from queue import Queue


HOST = "legion.dynamic-dns.net"
PORT = 5000

Logger.disable()

signal.signal(signal.SIGINT, signal.SIG_DFL)
clientLogger = Logger("[Client]")
serverLogger = Logger("[Server]")


def post(body):
    req = {}
    req["method"] = "POST"
    req["body"] = body
    return req

def get(body=None):
    req = {}
    req["method"] = "GET"
    if body:
        req["body"] = body
    return req


class Connection:
    def __init__(self):
        self.cursors = []

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.running = True
        self.thread = Thread(target=self.syncLoop)

        self.queue = Queue()

    def connect(self, host, port):
        self.conn.connect((host, port))
        self.conn.settimeout(60)
        self.register()
        self.thread.start()


    def syncLoop(self):
        logger = Logger("[Sync]")
        max = 0
        while self.running:
            start = time()
            res = self.request(get({"id": "positions"}))
            ping = "{:.1f}".format((time() - start)*1000)
            if float(ping) > max:
                max = float(ping)
                print(f"Request took {ping} ms")
            
            if res["status"] == 200:
                self.cursors = res["body"]["cursors"]
                logger.log(f"Received: {res}")
        
            res = self.request(post({
                "id": "move",
                "position": {
                    "x": self.x,
                    "y": self.y
                }
            }))
            if res["status"] == 200:
                logger.log(f"Sent: {res}")
    
    def register(self):
        res = self.request(post({
            "id": "register",
            "name": "Emmet",
            "position": {
                "x": 100,
                "y": 100
            }
        }))

        if res["status"] == 200:
            clientLogger.log("Registered")
        else:
            clientLogger.error(f"Failed to register: {res['body']['message']}")

    def setPos(self, x, y):
        self.x, self.y = x, y
    
    def getCursors(self):
        return self.cursors

    def quit(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.conn.close()

    def request(self, req):
        self.conn.send(json.dumps(req).encode())
        return json.loads(self.conn.recv(1024).decode())

import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Client")
clock = pygame.time.Clock()

conn = Connection()
conn.connect(HOST, PORT)

pygame.mouse.set_visible(False)
running = True
frame = 0
while running:
    frame+=1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    screen.fill((0, 0, 0))

    x, y = pygame.mouse.get_pos()
    conn.setPos(x, y)

    for cursor in conn.getCursors():
        pygame.draw.circle(screen, (255, 255, 255), (cursor["position"]["x"], cursor["position"]["y"]), 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
conn.quit()
