 Scenario: Timer alternates ON and OFF based on configured times
    Given the ON time is set to 3 seconds
    And the OFF time is set to 2 seconds
    And the timer is running
    When 5 seconds have passed
    Then the output should be ON for 3 seconds
    And OFF for 2 seconds
    And ON again after 5 seconds
