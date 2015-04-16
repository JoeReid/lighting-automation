import pygame
import array
import random
import socket
import threading

COLOR_BACKGROUND = (0, 0, 0, 255)


# Pygame Helpers ---------------------------------------------------------------
#  Try to keep underlying implementation/libs of grapics handling away from logic

class PygameBase(object):

    def __init__(self, framerate=3):
        pygame.init()
        self.screen = pygame.display.set_mode((320, 240))
        self.clock = pygame.time.Clock()
        self.running = True
        self.framerate = framerate

    def start(self):
        while self.running:
            self.clock.tick(self.framerate)
            self.screen.fill(COLOR_BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False

            self.loop()

            pygame.display.flip()

        pygame.quit()

    def stop(self):
        self.running = False

    def loop(self):
        assert False, 'loop must be overriden'


# UDP Mixin --------------------------------------------------------------------

class UDPMixin(object):
    BUFFER_SIZE = 1024

    def __init__(self, ip='127.0.0.1', port=5005):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))

        self.thread = threading.Thread(target=self.recieve_loop, args=())
        self.thread.daemon = True

        self.running = True

    def listen(self):
        self.thread.start()

    def recieve_loop(self):
        while self.running:
            data, addr = self.sock.recvfrom(UDPMixin.BUFFER_SIZE)
            self.recieve(addr, data)

    def recieve(self, addr, data):
        print("received {0}: {1}".format(addr, data))


# DMX Simulator ----------------------------------------------------------------

class DMXLight(object):
    data_size = 8

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(self.x, self.y, self.size * 8, self.size * 5)
        #self.func_get_data = func_get_data
        self.func_get_data = lambda: []

    @property
    def data(self):
        return self.func_get_data()

    @property
    def color(self):
        red, green, blue, white = (c//2 for c in self.data[0:4])
        return (red + white, green + white, blue + white, 255)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        red, green, blue, white = self.data[0:4]
        def draw_led(value, color, y_offset):
            for i in range(value//32):
                pygame.draw.circle(screen, color, (self.size + self.x + i * self.size, self.size + self.y + y_offset * self.size), self.size//2)
        draw_led(red, (255, 0, 0), 0)
        draw_led(green, (0, 255, 0), 1)
        draw_led(blue, (0, 0, 255), 2)
        draw_led(white, (255, 255, 255), 3)


class DMXSimulator(UDPMixin, PygameBase):

    def __init__(self):
        UDPMixin.__init__(self)
        self.listen()

        PygameBase.__init__(self)

        self._init_dmx_items(
            DMXLight(10, 10, 8),
            DMXLight(50, 50, 8),
            DMXLight(100, 100, 8),
        )
        self.state = [random.randint(0, 255) for i in range(512)]

    def _init_dmx_items(self, *dmx_items):
        self.dmx_items = dmx_items

        def func_get_data(index, data_size):  # By passing index and size to this function, the values become bound so they can be used in the lambda
            return lambda: self.state[index:index + data_size]

        index = 0
        for dmx_item in dmx_items:
            dmx_item.func_get_data = func_get_data(index, dmx_item.data_size)
            index += dmx_item.data_size

    def loop(self):
        for item in self.dmx_items:
            item.render(self.screen)

    def update(self, state):
        self.state = state

    def recieve(self, addr, data):
        self.update(data)


# Notes ------------------------------------------------------------------------

def send_example():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b'HelloWorld', ('127.0.0.1', 5005))
    sock.sendto(b'\x00'*512, ('127.0.0.1', 5005))


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    dmx = DMXSimulator()
    dmx.start()
