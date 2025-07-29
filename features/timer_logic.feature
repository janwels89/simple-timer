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
