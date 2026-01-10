package com.paramtech.steps;

import com.paramtech.driver.DriverFactory;
import com.paramtech.locators.CommonLocators;
import com.paramtech.locators.DashboardLocators;
import com.paramtech.pages.LoginPage;
import com.paramtech.utils.ConfigReader;
import com.paramtech.utils.WaitUtils;
import org.junit.jupiter.api.Assertions;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

import java.time.Duration;

public class AuthSteps {

    private WebDriver driver() {
        return DriverFactory.getDriver();
    }

    private long timeoutSeconds() {
        try {
            return Long.parseLong(ConfigReader.getProperty("timeoutSeconds"));
        } catch (Exception e) {
            return 20;
        }
    }

    private String usernameForRole(String role) {
        return ConfigReader.getProperty(role + ".username");
    }

    private String passwordForRole(String role) {
        String pw = ConfigReader.getProperty(role + ".password");
        return pw;
    }


    @Given("I am logged in as {string}")
    public void iAmLoggedInAs(String role) throws InterruptedException {
        LoginPage loginPage = new LoginPage(driver());
        loginPage.open();
        loginPage.login(usernameForRole(role), passwordForRole(role));

        // Wait for dashboard redirect (role dependent)
        WebDriverWait wait = new WebDriverWait(driver(), Duration.ofSeconds(timeoutSeconds()));
        if ("admin".equalsIgnoreCase(role)) {
            wait.until(ExpectedConditions.visibilityOfElementLocated(DashboardLocators.ADMIN_H1));
        } else if ("teacher".equalsIgnoreCase(role)) {
            wait.until(ExpectedConditions.visibilityOfElementLocated(DashboardLocators.TEACHER_H1));
        } else if ("student".equalsIgnoreCase(role)) {
            wait.until(ExpectedConditions.visibilityOfElementLocated(DashboardLocators.STUDENT_H1));
        }
        Thread.sleep(1500);
    }

    @When("I log in as {string}")
    public void iLogInAs(String role) {
        LoginPage loginPage = new LoginPage(driver());
        loginPage.login(usernameForRole(role), passwordForRole(role));

        WaitUtils.waitForPageToLoad(driver(), timeoutSeconds());

        new WebDriverWait(driver(), Duration.ofSeconds(timeoutSeconds()))
                .until(d ->
                        d.getCurrentUrl().contains("/admin")
                                || d.getCurrentUrl().contains("/teacher")
                                || d.getCurrentUrl().contains("/student")
                                || !d.findElements(CommonLocators.ALERT).isEmpty()
                );
    }


    @When("I log in with username {string} and password {string}")
    public void iLogInWithCredentials(String username, String password) throws InterruptedException {
        LoginPage loginPage = new LoginPage(driver());
        loginPage.login(username, password);
        Thread.sleep(1500);
    }

    @When("I attempt to submit the login form with empty credentials")
    public void iAttemptSubmitEmptyLogin() {
        LoginPage loginPage = new LoginPage(driver());
        loginPage.submitEmpty();
    }

    @Then("I should be on the admin dashboard")
    public void iShouldBeOnAdminDashboard() {
        new WebDriverWait(driver(), Duration.ofSeconds(timeoutSeconds()))
                .until(ExpectedConditions.visibilityOfElementLocated(DashboardLocators.ADMIN_H1));
        Assertions.assertTrue(driver().findElement(DashboardLocators.ADMIN_H1).isDisplayed());
    }

    @Then("I should be on the teacher dashboard")
    public void iShouldBeOnTeacherDashboard() {
        new WebDriverWait(driver(), Duration.ofSeconds(timeoutSeconds()))
                .until(ExpectedConditions.visibilityOfElementLocated(DashboardLocators.TEACHER_H1));
        Assertions.assertTrue(driver().findElement(DashboardLocators.TEACHER_H1).isDisplayed());
    }

    @Then("I should be on the student dashboard")
    public void iShouldBeOnStudentDashboard() {
        new WebDriverWait(driver(), Duration.ofSeconds(timeoutSeconds()))
                .until(ExpectedConditions.visibilityOfElementLocated(DashboardLocators.STUDENT_H1));
        Assertions.assertTrue(driver().findElement(DashboardLocators.STUDENT_H1).isDisplayed());
    }

    @When("I log out")
    public void iLogOut() {
        // Try link first
        if (!driver().findElements(CommonLocators.LOGOUT_LINK).isEmpty()) {
            driver().findElement(CommonLocators.LOGOUT_LINK).click();
        }
    }
}

