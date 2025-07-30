class ButtonInput:
    """
    Mock version of ButtonInput for testing button presses.
    """
    def __init__(self, pin_mapping=None):
        # Default to 5 common buttons if no mapping is given
        self.buttons = ['up', 'down', 'left', 'right', 'select']
        self.state = {b: False for b in self.buttons}

    def is_pressed(self, button_name):
        return self.state.get(button_name, False)

    def pressed_buttons(self):
        return [btn for btn, pressed in self.state.items() if pressed]

    def press(self, button_name):
        if button_name in self.state:
            self.state[button_name] = True

    def release(self, button_name):
        if button_name in self.state:
            self.state[button_name] = False

    def cleanup(self):
        # Nothing to clean up in the mock
        pass


class JoystickInput:
    """
    Mock version of JoystickInput for testing directions and press.
    """
    def __init__(self, pin_mapping=None):
        self.directions = ['up', 'down', 'left', 'right', 'press']
        self.state = {d: False for d in self.directions}

    def is_active(self, direction):
        return self.state.get(direction, False)

    def active_directions(self):
        return [d for d, active in self.state.items() if active]

    def move(self, direction):
        if direction in self.state and direction != 'press':
            self.state[direction] = True

    def release(self, direction):
        if direction in self.state:
            self.state[direction] = False

    def press(self):
        self.state['press'] = True

    def release_press(self):
        self.state['press'] = False

    def cleanup(self):
        # Nothing to clean up in the mock
        pass
