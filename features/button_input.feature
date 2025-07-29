Feature: Button control

  Scenario: KEY3 selects OPEN timer
    Given the device is powered on
    When the user presses KEY3
    Then the timer module selected should be OPEN

  Scenario: KEY1 selects CLOSE timer
    Given the device is powered on
    When the user presses KEY1
    Then the timer module selected should be CLOSE

  Scenario: KEY2 toggles enable state
    Given the device is powered on
    And the timer is disabled
    When the user presses KEY2
    Then the timer should be enabled
