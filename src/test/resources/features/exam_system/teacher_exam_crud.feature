@ui
Feature: Teacher exam creation

  Scenario: Teacher can create a new exam
    Given I am logged in as "teacher"
    When I create a new exam
    Then I should see the new exam in the exams list

  Scenario: Exam form validates required fields
    Given I am logged in as "teacher"
    When I try to create an exam without a title
    Then I should see an exam validation error
