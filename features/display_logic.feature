Feature: Display output

  Scenario: Shows default timer values after reset
    Given the device is powered on
    And the timer settings are reset
    And the timer starts with default values
    When the application runs
    Then the display should show "5" for OPEN
    And the display should show "5" for CLOSE

  Scenario: Shows updated timer values after increment
    Given the device is powered on
    And the timer settings are reset
    And the timer starts with default values
    When the user increments the OPEN timer
    And the application runs
    Then the display should show "6" for OPEN
    And the display should show "5" for CLOSE