@ui @teacher
Feature: Teacher dashboard

  Scenario: Teacher dashboard shows key sections
    Given I am logged in as "teacher"
    Then I should be on the teacher dashboard page
    And I should see teacher dashboard navigation cards
