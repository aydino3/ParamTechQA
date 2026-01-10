@ui @student
Feature: Student dashboard

  Scenario: Student dashboard shows assignments table
    Given I am logged in as "student"
    Then I should be on the student dashboard page
    And I should see assigned exams table
