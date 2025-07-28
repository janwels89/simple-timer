Scenario: Increase selected timer value
  Given the device is powered on
  And a timer (ON or OFF) is selected
  And the selected timer is currently set to 5 seconds
  When the user moves the joystick up
  Then the selected timer value should increase by 1 second
  And the display should show the updated timer value

Scenario: Decrease selected timer value
  Given the device is powered on
  And a timer (ON or OFF) is selected
  And the selected timer is currently set to 12 seconds
  When the user moves the joystick down
  Then the selected timer value should decrease by 1 second
  And the display should show the updated timer value
