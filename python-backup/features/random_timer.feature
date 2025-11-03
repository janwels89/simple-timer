Feature: Timer random mode

  Scenario: User enables random mode with joystick right
    Given the device is powered on
    And the OPEN time is set to 10 seconds
    And the CLOSE time is set to 5 seconds
    And the timer is running
    When the user moves the joystick right
    Then the timer mode should be "random"
    And the OPEN time should remain 10 seconds
    And the CLOSE time should remain 5 seconds

  Scenario: Timer sets open and close times randomly each cycle
    Given the device is powered on
    Given the timer mode is "random"
    And the OPEN time is set to 10 seconds
    And the CLOSE time is set to 5 seconds
    When the timer starts a new period
    Then the displayed period time should be between 0 and its base time
    And the base OPEN and CLOSE times should not change

  Scenario: Timer randomizes again each cycle, base times do not change
    Given the device is powered on
    Given the timer mode is "random"
    And the timer completes a period
    When a new period starts
    Then the new period time should be different from the previous period and between 0 and its base time
    And the base times should not change

  Scenario: User disables random mode with joystick right again
    Given the device is powered on
    Given the timer mode is "random"
    When the user moves the joystick right
    Then the timer mode should be "loop"
    And the timer should use the OPEN and CLOSE base times