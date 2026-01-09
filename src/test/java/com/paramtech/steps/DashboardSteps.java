package com.paramtech.steps;

import com.paramtech.driver.DriverFactory;
import com.paramtech.locators.DashboardLocators;
import io.cucumber.java.en.Then;
import org.junit.jupiter.api.Assertions;
import org.openqa.selenium.WebDriver;

import static com.paramtech.utils.WaitUtils.waitForVisibility;

public class DashboardSteps {

    private WebDriver driver() {
        return DriverFactory.getDriver();
    }

    @Then("I should be on the teacher dashboard page")
    public void iShouldBeOnTheTeacherDashboardPage() {
        Assertions.assertTrue(driver().getCurrentUrl().contains("/teacher/dashboard"),
                "Expected teacher dashboard URL but was: " + driver().getCurrentUrl());
        waitForVisibility(driver(), DashboardLocators.TEACHER_H1);
        Assertions.assertTrue(driver().findElement(DashboardLocators.TEACHER_H1).isDisplayed());
    }

    @Then("I should see teacher dashboard navigation cards")
    public void iShouldSeeTeacherDashboardNavigationCards() {
        waitForVisibility(driver(), DashboardLocators.TEACHER_EXAMS_LINK);
        Assertions.assertTrue(driver().findElement(DashboardLocators.TEACHER_EXAMS_LINK).isDisplayed());
        Assertions.assertTrue(driver().findElement(DashboardLocators.TEACHER_QUESTIONS_LINK).isDisplayed());
        Assertions.assertTrue(driver().findElement(DashboardLocators.TEACHER_ASSIGNMENTS_LINK).isDisplayed());
    }

    @Then("I should be on the student dashboard page")
    public void iShouldBeOnTheStudentDashboardPage() {
        Assertions.assertTrue(driver().getCurrentUrl().contains("/student/dashboard"),
                "Expected student dashboard URL but was: " + driver().getCurrentUrl());
        waitForVisibility(driver(), DashboardLocators.STUDENT_H1);
        Assertions.assertTrue(driver().findElement(DashboardLocators.STUDENT_H1).isDisplayed());
    }

    @Then("I should see assigned exams table")
    public void iShouldSeeAssignedExamsTable() {
        waitForVisibility(driver(), DashboardLocators.STUDENT_ASSIGNMENTS_TABLE);
        Assertions.assertTrue(driver().findElement(DashboardLocators.STUDENT_ASSIGNMENTS_TABLE).isDisplayed());
    }
}
