Feature: Timer Logic

  Scenario: Timer alternates OPEN and CLOSE based on configured times
    Given the device is powered on
    And the OPEN time is set to 3 seconds
    And the CLOSE time is set to 2 seconds
    And the timer is running
    When 5 seconds have passed
    Then the output should be OPEN for 3 seconds
    And CLOSE for 2 seconds
    And OPEN again after 5 seconds

  Scenario: Timer settings are saved and reloaded after reboot
    Given the device is powered on
    And the OPEN time is set to 7 seconds
    And the CLOSE time is set to 4 seconds
    When the device is rebooted
    Then the OPEN time should be 7 seconds
    And the CLOSE time should be 4 seconds

 Scenario: Timer settings can be reset to defaults
    Given the device is powered on
    And the OPEN time is set to 12 seconds
    And the CLOSE time is set to 8 seconds
    When the timer settings are reset
    And the device is rebooted
    Then the OPEN time should be 5 seconds
    And the CLOSE time should be 5 seconds