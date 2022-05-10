from utils import smooth, BaseState, BaseConsumer
from evdev import ecodes as e
from functools import reduce
import time


class StateN(BaseState): # N

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
    
    def on_left_click(self, event): # A
        self.c.BTN_LEFT.update(event.value)
        #if event.value == 1: # +A
        #    self.consumer.set_state(self.consumer.state_A)

    def on_down_click(self, event): # B
        if event.value == 1: # +B
            self.consumer.set_state(self.consumer.state_B)
    
    def on_up_click(self, event): # C
        if event.value == 1: # +C
            self.consumer.set_state(self.consumer.state_C)

    def on_right_click(self, event): # D
        if event.value == 1: # +D
            self.consumer.set_state(self.consumer.state_D)
    
    def on_move_rel_x(self, event):
        self.c.bt_rel_x.update(smooth(event.value))

    def on_move_rel_y(self, event):
        self.c.bt_rel_y.update(smooth(event.value))


class StateA(BaseState):

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
        self.vr_mode = False
    
    def on_activate(self):
        super().on_activate()
        self.c.BTN_LEFT.update(1)

        self.vr_mode = False
        self.acc_x = 0
        self.acc_y = 0
        self.state_x = 0
        self.state_y = 0
        self.pending_x = 0
        self.pending_y = 0

        self.state = 0
        self.moves = []
        self.pending_moves = []
        self.return_to = (0,0)
    
    def on_deactivate(self):
        super().on_deactivate()
        self.c.BTN_LEFT.update(0)

    def on_left_click(self, event): # A
        if self.vr_mode:
            self.c.BTN_LEFT.update(event.value)

        else:
            if event.value == 0:
                self.consumer.set_state(self.consumer.state_N)
                self.c.BTN_LEFT.update(0)

    def on_down_click(self, event): # B
        if event.value == 0:
            if self.vr_mode:
                self.consumer.set_state(self.consumer.state_N)
            else:
                self.vr_mode = True
    
    def on_up_click(self, event): # C
        if self.vr_mode:
            self.c.BTN_RIGHT.update(event.value)

    def on_right_click(self, event): # D
        if self.vr_mode:
            self.c.BTN_MIDDLE.update(event.value)
    
    def on_move_rel_x(self, event):

        if self.vr_mode:
            value = smooth(event.value)
            self.moves.append((value, 0))
            self.update_state()

        else:
            # print("rel_x, non-vr", event.value, self.acc_x)
        
            self.c.bt_rel_x.update(smooth(event.value))

    def on_move_rel_y(self, event):
        if self.vr_mode:
            
            value = smooth(event.value)
            self.moves.append((0,value))
            self.update_state()

        else:
            self.c.bt_rel_y.update(smooth(event.value))

    def update_state(self):
        if self.state == 0:
            if len(self.moves) >= 2:

                self.pending_moves = reduce(lambda a,b : (a[0]+b[0], a[1]+b[1]), self.moves, (0,0))
                self.c.BTN_LEFT.update(1)
                self.return_to = (0,0)
                self.moves = []

                sx = self.pending_moves[0] / 3
                sy = self.pending_moves[1] / 3
                
                self.pending_moves = [ (int(sx), int(sy)), (int(sx*2), int(sy*2)) ]

                self.next_state = 1
                self.delay = 5
                self.state = 4
        
        elif self.state == 1:
            
            move = self.pending_moves.pop()

            dx = move[0]
            dy = move[1]

            self.return_to = (self.return_to[0] - dx, self.return_to[1] - dy)

            print("state1, moving ", dx, dy)

            self.c.bt_rel_x.update(dx)
            self.c.bt_rel_y.update(dy)
            self.c.BTN_LEFT.update(0)

            self.next_state = 2
            self.delay = 5
            self.state = 4
        
        elif self.state == 2:

            print("state2, releasing key")
            
            move = self.pending_moves.pop()

            dx = move[0]
            dy = move[1]

            self.return_to = (self.return_to[0] - dx, self.return_to[1] - dy)

            print("state2, moving ", dx, dy)

            self.c.bt_rel_x.update(dx)
            self.c.bt_rel_y.update(dy)

            self.next_state = 3
            self.delay = 5
            self.state = 4


        elif self.state == 3:
            print("state3, returning to origin")
            
            dx = self.return_to[0]
            dy = self.return_to[1]

            self.c.bt_rel_x.update(dx)
            self.c.bt_rel_y.update(dy)

            self.next_state = 0
            self.delay = 5
            self.state = 4
        
        elif self.state == 4:
            self.delay -= 1
            if self.delay == 0:
                self.state = self.next_state

            
    def update_state1(self):

        if self.state == 0:
            if len(self.moves) >= 5:
                print("state0, pressing left key")

                self.pending_moves = self.moves
                self.c.BTN_LEFT.update(1)
                self.return_to = (0,0)
                self.moves = []
                self.state = 1

                self.next_state = 1
                self.delay = 5
                self.state = 4
        
        elif self.state == 1:
            move1 = self.pending_moves.pop()
            move2 = self.pending_moves.pop()

            dx = move1[0] + move2[0]
            dy = move1[1] + move2[1]

            print("state1, moving ", dx, dy)

            self.c.bt_rel_x.update(dx)
            self.c.bt_rel_y.update(dy)
            
            self.return_to = (self.return_to[0] - dx, self.return_to[1] - dy)

            if len(self.pending_moves) < 2:
                self.next_state = 2
                self.delay = 5
                self.state = 4
        
        elif self.state == 2:

            print("state2, releasing key")
            self.c.BTN_LEFT.update(0)
            
            self.next_state = 3
            self.delay = 5
            self.state = 4
        
        elif self.state == 3:
            print("state3, returning to origin")

            dx = self.return_to[0]
            dy = self.return_to[1]

            self.c.bt_rel_x.update(dx)
            self.c.bt_rel_y.update(dy)

            # self.c.bt_abs_x.update(8192)
            # self.c.bt_abs_y.update(8192)

            self.next_state = 0
            self.delay = 5
            self.state = 4
        
        elif self.state == 4:
            self.delay -= 1
            if self.delay == 0:
                self.state = self.next_state

        

class StateB(BaseState):

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
        self.clean = True
    
    def on_activate(self):
        super().on_activate()
        self.clean = True
    
    def on_deactivate(self):
        super().on_deactivate()

    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTMETA.press()

        elif event.value == 0:
            self.c.KEY_LEFTMETA.release()

    def on_down_click(self, event): # B
        if event.value == 0:

            if self.clean:
                self.c.KEY_LEFTCTRL.press()
                self.c.BTN_LEFT.press()

                time.sleep(0.25) # The click must happen after the IDE has created the "button"

                self.c.BTN_LEFT.release()
                self.c.KEY_LEFTCTRL.release()
            
            self.consumer.set_state(self.consumer.state_N)
    
    def on_up_click(self, event): # C
        self.clean = False
        self.c.BTN_SIDE.update(event.value)

    def on_right_click(self, event): # D
        self.clean = False
        self.c.BTN_EXTRA.update(event.value)
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.c.bt_wheel_h.update(event.value * 20)

    def on_move_rel_y(self, event):
        self.clean = False
        self.c.bt_wheel_v.update(-event.value * 10)


class StateC(BaseState):

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_T.press()
        
        else:
            self.c.KEY_T.release()
            self.c.KEY_LEFTCTRL.release()

    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_LEFTSHIFT.press()
            self.c.KEY_T.press()
        
        else:
            self.c.KEY_T.release()
            self.c.KEY_LEFTSHIFT.release()
            self.c.KEY_LEFTCTRL.release()
    
    def on_up_click(self, event): # C

        if event.value == 0: # -C

            if self.clean:
                self.c.BTN_RIGHT.press()
                self.c.BTN_RIGHT.release()
            
            self.c.lockable2.unlock()
            self.consumer.set_state(self.consumer.state_N)

    def on_right_click(self, event): # D
        self.clean = False
        
        if event.value == 0:
            self.c.KEY_LEFTALT.press()

            self.c.BTN_RIGHT.press()
            self.c.BTN_RIGHT.release()

            time.sleep(0.2)

            self.c.KEY_S.press()
            self.c.KEY_S.release()

            self.c.KEY_LEFTALT.release()
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.c.lockable2.update_h(event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        self.c.lockable2.update_v(-event.value * 5)


class StateD(BaseState):

    def __init__(self, consumer, context):
        super().__init__(context)
        self.consumer = consumer
        self.clean = True
    
    def on_activate(self):
        self.clean = True
    
    def on_left_click(self, event): # A
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_W.press()

        else:
            self.c.KEY_W.release()
            self.c.KEY_LEFTCTRL.release()
    
    def on_down_click(self, event): # B
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTALT.press()
            self.c.KEY_F4.press()

        else:
            self.c.KEY_F4.release()
            self.c.KEY_LEFTALT.release()

    def on_up_click(self, event): # C
        self.clean = False

        if event.value == 1:
            self.c.KEY_LEFTCTRL.press()
            self.c.KEY_D.press()

        else:
            self.c.KEY_D.release()
            self.c.KEY_LEFTCTRL.release()
    
    def on_right_click(self, event): # D
        if event.value == 0:

            if self.clean:
                self.c.BTN_MIDDLE.press()
                self.c.BTN_MIDDLE.release()
            
            self.c.lockable1.unlock()

            self.consumer.set_state(self.consumer.state_N)
    
    def on_move_rel_x(self, event):
        self.clean = False
        self.c.lockable1.update_h(event.value * 5)

    def on_move_rel_y(self, event):
        self.clean = False
        self.c.lockable1.update_v(-event.value * 5)


FILTERS = ["Logitech USB Trackball"]


class Consumer(BaseConsumer):

    def __init__(self, context):
        super().__init__(context)

        self.state_N = StateN(self, context)
        self.state_A = StateA(self, context)
        self.state_B = StateB(self, context)
        self.state_C = StateC(self, context)
        self.state_D = StateD(self, context)
        self.state   = self.state_N

    def on_event(self, event):
        #print(event.value, event.code, event.type)

        if event.type == e.EV_KEY:

            # big_left
            if event.code == e.BTN_LEFT:
                self.state.on_left_click(event)

            # small left
            elif event.code == e.BTN_SIDE:
                self.state.on_down_click(event)                    

            # small right
            elif event.code == e.BTN_EXTRA:
                self.state.on_up_click(event)

            # big right
            elif event.code == e.BTN_RIGHT:
                self.state.on_right_click(event)

        elif event.type == e.EV_REL:

            # Ball rotates horizontally
            if event.code == e.REL_X:
                self.state.on_move_rel_x(event)

            # Ball rotates vertically
            elif event.code == e.REL_Y:
                self.state.on_move_rel_y(event)
