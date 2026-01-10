@ui @navigation
Feature: Navigation and access control

  Scenario: Root path redirects to login
    When I visit path "/"
    Then I should be on the login page

  Scenario: Teacher navigation links work
    Given I am logged in as "teacher"
    When I click the teacher link to questions
    Then I should be on the teacher questions page
    When I click the teacher link to exams
    Then I should be on the teacher exams page

  Scenario: Student can access dashboard
    Given I am logged in as "student"
    When I visit path "/student/dashboard"
    Then I should be on the student dashboard page
