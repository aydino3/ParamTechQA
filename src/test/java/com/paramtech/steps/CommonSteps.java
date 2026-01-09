package com.paramtech.steps;

import com.paramtech.driver.DriverFactory;
import com.paramtech.locators.CommonLocators;
import com.paramtech.utils.ConfigReader;
import org.junit.jupiter.api.Assertions;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

import java.time.Duration;

public class CommonSteps {

    private WebDriver driver() {
        return DriverFactory.getDriver();
    }

    private String baseUrl() {
        return ConfigReader.getProperty("baseUrl");
    }

    private void waitUrlContains(String fragment) {
        new WebDriverWait(driver(), Duration.ofSeconds(Long.parseLong(ConfigReader.getProperty("timeoutSeconds"))))
                .until(ExpectedConditions.urlContains(fragment));
    }

    @Given("I navigate to the Exam System login page")
    public void iNavigateToLoginPage() {
        driver().get(baseUrl() + "/login");
    }

    @When("I visit path {string}")
    public void iVisitPath(String path) {
        if (path == null || path.isBlank()) {
            path = "/";
        }
        driver().get(baseUrl() + path);
    }

    @Then("I should be on the login page")
    public void iShouldBeOnTheLoginPage() {
        waitUrlContains("/login");
        // Login form should be visible
        Assertions.assertTrue(driver().findElement(By.xpath("//input[@name='username']")).isDisplayed(),
                "Username input should be visible on login page");
        Assertions.assertTrue(driver().findElement(By.xpath("//input[@name='password']")).isDisplayed(),
                "Password input should be visible on login page");
    }

    @Then("accessing {string} should redirect to login")
    public void accessingShouldRedirectToLogin(String protectedPath) {
        driver().get(baseUrl() + protectedPath);
        waitUrlContains("/login");
    }

    @Then("I should see an alert containing {string}")
    public void iShouldSeeAlertContaining(String text) {
        new WebDriverWait(driver(), Duration.ofSeconds(Long.parseLong(ConfigReader.getProperty("timeoutSeconds"))))
                .until(ExpectedConditions.visibilityOfElementLocated(CommonLocators.ALERT));
        String alertText = driver().findElement(CommonLocators.ALERT).getText();
        Assertions.assertTrue(alertText.contains(text),
                "Expected alert to contain: " + text + " but was: " + alertText);
    }

    @Then("I should see a login error message")
    public void iShouldSeeLoginErrorMessage() {
        if (driver().findElements(CommonLocators.ALERT).isEmpty()) {
            Assertions.fail("Expected a login error alert, but no alert was found.");
        }
        String alertText = driver().findElement(CommonLocators.ALERT).getText();
        // Keep this flexible; different templates may vary the exact wording.
        Assertions.assertTrue(
                alertText.toLowerCase().contains("invalid") || alertText.toLowerCase().contains("incorrect"),
                "Expected an error message about invalid/incorrect credentials, but was: " + alertText
        );
    }

    @Then("I should see a login validation error")
    public void iShouldSeeLoginValidationError() {
        // HTML5 required fields may prevent a submission; in that case we simply stay on /login.
        Assertions.assertTrue(driver().getCurrentUrl().contains("/login"),
                "Expected to remain on /login, but was on: " + driver().getCurrentUrl());
        // If server-side validation is used, it will likely show an alert.
        if (!driver().findElements(CommonLocators.ALERT).isEmpty()) {
            String alertText = driver().findElement(CommonLocators.ALERT).getText();
            Assertions.assertFalse(alertText.isBlank(), "Validation alert was present but empty.");
        }
    }
}
