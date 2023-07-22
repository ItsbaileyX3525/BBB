from networking import *
from ursina.prefabs.first_person_controller import *
from ursina import *

class InputState:
    def __init__(self, input_state=None):
        if input_state is not None:
            self.Movement = input_state.Movement
            self.sequence_number = input_state.sequence_number
            return

        self.Movement = False
        self.sequence_number = 0

    def copy(self):
        return InputState(self)
    
class BearState:
    def __init__(self, bear_state=None):
        if bear_state is not None:
            self.uuid = bear_state.uuid
            self.x = bear_state.x
            self.y = bear_state.y
            self.z = bear_state.z
            self.rx = bear_state.rx
            self.ry = bear_state.ry
            self.rz = bear_state.rz
            self.input_state = bear_state.input_state.copy()
            return

        self.uuid = 0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rx = 0.0
        self.ry = 0.0
        self.rz = 0.0
        self.input_state = InputState()

    def copy(self):
        return BearState(self)

def serialize_bear_state(writer, bear_state):
    writer.write(bear_state.uuid)
    writer.write(bear_state.x)
    writer.write(bear_state.y)
    writer.write(bear_state.z)
    writer.write(bear_state.rx)
    writer.write(bear_state.ry)
    writer.write(bear_state.rz)

def deserialize_bear_state(reader):
    bear_state = BearState()
    bear_state.uuid = reader.read(int)
    bear_state.x = reader.read(float)
    bear_state.y = reader.read(float)
    bear_state.z = reader.read(float)
    bear_state.rx = reader.read(float)
    bear_state.ry = reader.read(float)
    bear_state.rz = reader.read(float)
    return bear_state

class Bear(Entity):
    def __init__(self):
        super().__init__(parent=scene, model="cube",color=color.blue, scale=1)

        self.state = BearState()
        self.state.y = 0.1

        self.new_state = BearState()
        self.prev_state = self.new_state.copy()

        self.speed = 0.4  

    def update(self):
        self.x = self.state.x
        self.y = self.state.y
        self.z = self.state.z
        self.rotation_x = self.state.rx
        self.rotation_y = self.state.ry
        self.rotation_z = self.state.rz

    def interpolate(self):
        self.state = self.new_state.copy()

    def tick(self, dt):
        self.state.x = controller.x
        self.state.y = controller.y
        self.state.z = controller.z
        self.state.rx = controller.rotation_x
        self.state.ry = controller.rotation_y
        self.state.rz = controller.rotation_z

app=Ursina(borderless=False)
peer=RPCPeer()

peer.register_type(BearState, serialize_bear_state, deserialize_bear_state)

uuid_counter = 0
bears = []
my_bear_uuid = None
uuid_to_bear = dict()

connection_to_bear = dict()

input_state = InputState()

inputs_received = dict()
input_buffer = []
send_input_buffer = []

tick_rate = 1.0 / 60.0
tick_timer = 0.0
time_factor = 1.0

update_rate = 1.0 / 20.0
update_timer = 0.0
ground = Entity(model='plane',scale_x=100,scale_z=100,texture='grass',collider='box')
controller = FirstPersonController()
@rpc(peer)
def on_connect(connection,time_recieved):
    global uuid_counter
    if peer.is_hosting():
        b = Bear()
        b.state.uuid = uuid_counter
        uuid_counter += 1
        bears.append(b)
        uuid_to_bear[b.state.uuid] = b
        connection_to_bear[connection] = b
        inputs_received[b.state.uuid] = deque()
        connection.rpc_peer.set_bear_uuid(connection, b.state.uuid)
        s = [b.state for b in bears]
        for conn in connection.peer.get_connections():
            connection.rpc_peer.spawn_bears(conn, s)

@rpc(peer)
def on_disconnect(connection, time_disconnected):
    if peer.is_hosting():
        b = connection_to_bear.get(connection)
        if b is not None:
            destroy(b)
            bears.remove(b)
            del uuid_to_bear[b.state.uuid]
            del connection_to_bear[connection]
            del inputs_received[b.state.uuid]
            for conn in connection.rpc_peer.get_connections():
                connection.rpc_peer.remove_bears(conn, [b.state.uuid])
    else:
        for bear in bears:
            destroy(bear)
            del uuid_to_bear[bear.state.uuid]
        bears.clear()
        my_bear_uuid = None

@rpc(peer)
def set_bear_uuid(connection, time_received, uuid: int):
    global my_bear_uuid

    if connection.peer.is_hosting():
        return

    my_bear_uuid = uuid

@rpc(peer)
def spawn_bears(connection, time_received, new_bears: list[BearState]):
    if connection.peer.is_hosting():
        return

    for state in new_bears:
        if state.uuid not in uuid_to_bear:
            b = Bear()
            bears.append(b)
            uuid_to_bear[state.uuid] = b

@rpc(peer)
def remove_bears(connection, time_received, to_be_removed: list[int]):
    global my_bear_uuid

    if connection.peer.is_hosting():
        return

    for uuid in to_be_removed:
        bear = uuid_to_bear.get(uuid)
        if bear is not None:
            destroy(bear)
            bears.remove(bear)
            del uuid_to_bear[uuid]
            if uuid == my_bear_uuid:
                my_bear_uuid = None

@rpc(peer)
def set_states(connection, time_received, bear_states: list[BearState]):
    global time_factor

    if connection.peer.is_hosting():
        return

    for new_bear_state in bear_states:
        bear = uuid_to_bear.get(new_bear_state.uuid)
        if bear is None:
            continue

        if my_bear_uuid is None or my_bear_uuid != new_bear_state.uuid:
            bear.interpolate()
        else:
            # Compute processed input difference between client and host.
            sequence_delta = input_state.sequence_number - new_bear_state.input_state.sequence_number
            # Maybe slow down if ahead of host.
            max_delta = ((update_rate / tick_rate) + 1) * 2.5
            if sequence_delta > max_delta:
                time_factor = 0.95
            elif sequence_delta < max_delta * 0.75:
                time_factor = 1.0
            my_bear = uuid_to_bear.get(my_bear_uuid)
            if my_bear is None:
                continue
            # Reconcile with host.
            my_bear.state = new_bear_state.copy()
            if sequence_delta > 0 and sequence_delta < len(input_buffer):
                # Re-apply all inputs after the last processed input.
                for state in input_buffer[len(input_buffer) - sequence_delta:]:
                    bear.state.input_state = state.copy()
                    bear.tick(tick_rate)

def tick(dt):
    global last_input_sequence_number_processed

    if time_factor < 1.0:
        pass

    try:
        input_state.Movement = controller.direction
    except:
        pass
    if my_bear_uuid is not None:
        my_bear = uuid_to_bear.get(my_bear_uuid)
        if my_bear is not None:
            my_bear.state.input_state = input_state
            my_bear.tick(dt)

    if not peer.is_hosting():
        if my_bear_uuid is not None:
            input_state.sequence_number += 1
            input_buffer.append(input_state.copy())
            if len(input_buffer) >= 100:
                input_buffer.pop(0)
            send_input_buffer.append(input_buffer[-1])
            if len(send_input_buffer) > 10:
                send_input_buffer.pop(0)
    else:
        for bear in bears:
            if my_bear_uuid is None or my_bear_uuid != bear.state.uuid:
                input_queue = inputs_received.get(bear.state.uuid)
                if input_queue is None:
                    continue
                if len(input_queue) > 0:
                    bear.state.input_state = input_queue.popleft()
                else:
                    bear.state.input_state.Movement = False
                bear.tick(dt)

def update():
    global update_timer, tick_timer
    peer.update()
    print(uuid_counter)
    tick_timer += time.dt * time_factor
    while tick_timer >= tick_rate:
        tick(tick_rate)
        tick_timer -= tick_rate
def host():
    global uuid_counter, my_bear_uuid

    b = Bear()
    b.state.uuid = uuid_counter
    uuid_counter += 1
    bears.append(b)
    uuid_to_bear[b.state.uuid] = b
    my_bear_uuid = b.state.uuid

    h = ""
    try:
        h = h.split(":")
        port = int(h[1])
    except IndexError:
        port = 8080
    h = h[0]
    
    if h == "":
        h = "localhost"

    peer.start(h, port, is_host=True)
def join():
    h = ""
    try:
        h = h.split(":")
        port = int(h[1])
    except IndexError:
        port = 8080
    h = h[0]
    
    if h == "":
        h = "localhost"

    peer.start(h, port, is_host=False)
connType = input("Enter connection type: ")
if connType == 'h':
    host()
else:
    join()

app.run()