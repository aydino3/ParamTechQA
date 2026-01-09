@ui
Feature: Teacher question creation

  Scenario: Teacher can create a multiple-choice question
    Given I am logged in as "teacher"
    When I create a new multiple-choice question
    Then I should see the new question in the questions list

  Scenario: Teacher can create a true/false question
    Given I am logged in as "teacher"
    When I create a new true/false question
    Then I should see the new question in the questions list

  Scenario: Question form validates required fields
    Given I am logged in as "teacher"
    When I try to create a question without a question text
    Then I should see a question validation error
