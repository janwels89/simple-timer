class ButtonInput:
    """
    Mock version of ButtonInput for testing.
    Tracks which buttons are pressed and exposes is_pressed and pressed_buttons.
    """
    def __init__(self):
        self._pressed = set()

    def press(self, key):
        """Simulate pressing a button."""
        self._pressed.add(key)

    def release(self, key):
        """Simulate releasing a button."""
        self._pressed.discard(key)

    def is_pressed(self, key):
        """Check if a button is pressed."""
        return key in self._pressed

    def pressed_buttons(self):
        """Return a list of currently pressed buttons."""
        return list(self._pressed)

class JoystickInput:
    """
    Mock version of JoystickInput for testing.
    Supports directions and press.
    """
    def __init__(self):
        self._active = set()

    def move(self, direction):
        """Simulate moving the joystick in a direction (e.g., 'up', 'down', 'left', 'right')."""
        self._active.add(direction)

    def release(self, direction):
        """Simulate releasing a direction."""
        self._active.discard(direction)

    def is_active(self, direction):
        """Check if a direction or 'press' is active."""
        return direction in self._active

    def active_directions(self):
        """Return a list of currently active directions."""
        return list(self._active)

    def press(self):
        """Simulate pressing the joystick in (center press)."""
        self._active.add('press')

    def release_press(self):
        """Simulate releasing the joystick press."""
        self._active.discard('press')