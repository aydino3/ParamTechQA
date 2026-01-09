@ui
Feature: Login
  As a user of the Online Exam System
  I want to log in with role-based accounts
  So I can access my dashboard

  Scenario: Login page loads
    Given I navigate to the Exam System login page
    Then I should be on the login page

  Scenario: Admin can log in
    Given I navigate to the Exam System login page
    When I log in as "admin"
    Then I should see the Admin Dashboard

  Scenario: Teacher can log in
    Given I navigate to the Exam System login page
    When I log in as "teacher"
    Then I should see the Teacher Dashboard

  Scenario: Student can log in
    Given I navigate to the Exam System login page
    When I log in as "student"
    Then I should see the Student Dashboard

  Scenario Outline: Invalid login is rejected
    Given I navigate to the Exam System login page
    When I log in with username "<username>" and password "<password>"
    Then I should remain on the login page
    And I should see an authentication error message

    Examples:
      | username | password |
      | wrong    | wrong    |
      | admin    | wrong    |
      | wrong    | admin123 |

  Scenario: Empty credentials do not log in
    Given I navigate to the Exam System login page
    When I submit the login form without credentials
    Then I should remain on the login page
