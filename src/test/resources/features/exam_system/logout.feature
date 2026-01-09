@ui
Feature: Logout
  Users should be able to log out and lose session access.

  Scenario Outline: Logged in users can log out
    Given I am logged in as "<role>"
    When I log out
    Then I should be on the login page
    And accessing "<protectedPath>" should redirect to login

    Examples:
      | role    | protectedPath        |
      | admin   | /admin/dashboard     |
      | teacher | /teacher/dashboard   |
      | student | /student/dashboard   |
