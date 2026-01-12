package com.paramtech.steps;

import com.paramtech.driver.DriverFactory;
import com.paramtech.locators.DashboardLocators;
import com.paramtech.locators.TeacherDashboardLocators;
import io.cucumber.java.en.Then;
import org.junit.jupiter.api.Assertions;
import org.openqa.selenium.WebDriver;

import static com.paramtech.utils.WaitUtils.waitForVisibility;

public class DashboardSteps {

    private WebDriver driver() {
        return DriverFactory.getDriver();
    }

    private void assertUrlMatchesAny(String... needles) {
        String url = driver().getCurrentUrl();
        boolean ok = false;
        for (String n : needles) {
            if (url.contains(n)) {
                ok = true;
                break;
            }
        }
        Assertions.assertTrue(ok, "Unexpected URL. Expected one of: " + String.join(" OR ", needles) + " but was: " + url);
    }

    private void assertVisible(org.openqa.selenium.By locator, String nameForError) {
        waitForVisibility(driver(), locator);
        Assertions.assertTrue(driver().findElements(locator).size() > 0,
                nameForError + " not found/visible. URL: " + driver().getCurrentUrl());
        Assertions.assertTrue(driver().findElement(locator).isDisplayed(),
                nameForError + " not displayed. URL: " + driver().getCurrentUrl());
    }

    @Then("I should be on the teacher dashboard page")
    public void iShouldBeOnTheTeacherDashboardPage() {
        assertUrlMatchesAny("/teacher/dashboard", "/teacher");
        assertVisible(DashboardLocators.TEACHER_H1, "Teacher dashboard H1");
    }

    @Then("I should see teacher dashboard navigation cards")
    public void iShouldSeeTeacherDashboardNavigationCards() {
        assertVisible(TeacherDashboardLocators.PAGE_H1, "Teacher dashboard page H1");
        assertVisible(TeacherDashboardLocators.QUESTIONS_LINK, "Teacher Questions link");
        assertVisible(TeacherDashboardLocators.EXAMS_LINK, "Teacher Exams link");
        assertVisible(TeacherDashboardLocators.ASSIGNMENTS_LINK, "Teacher Assignments link");
    }

    @Then("I should be on the student dashboard page")
    public void iShouldBeOnTheStudentDashboardPage() {
        assertUrlMatchesAny("/student/dashboard", "/student");
        assertVisible(DashboardLocators.STUDENT_H1, "Student dashboard H1");
    }

    @Then("I should be on the admin dashboard page")
    public void iShouldBeOnTheAdminDashboardPage() {
        assertUrlMatchesAny("/admin/dashboard", "/admin");
        assertVisible(DashboardLocators.ADMIN_H1, "Admin dashboard H1");
    }

    @Then("I should see assigned exams table")
    public void iShouldSeeAssignedExamsTable() {
        assertVisible(DashboardLocators.STUDENT_ASSIGNMENTS_TABLE, "Student assignments table");
    }

    @Then("I should see the Admin Dashboard")
    public void iShouldSeeTheAdminDashboard() {
        iShouldBeOnTheAdminDashboardPage();
    }

    @Then("I should see the Teacher Dashboard")
    public void iShouldSeeTheTeacherDashboard() {
        iShouldBeOnTheTeacherDashboardPage();
    }

    @Then("I should see the Student Dashboard")
    public void iShouldSeeTheStudentDashboard() {
        iShouldBeOnTheStudentDashboardPage();
    }
}
