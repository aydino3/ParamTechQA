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

        String alertText = driver().findElement(CommonLocators.ALERT).getText().trim().toLowerCase();


        Assertions.assertTrue(
                alertText.contains("invalid username or password")
                        || alertText.contains("invalid")
                        || alertText.contains("incorrect")
                        || alertText.contains("error"),
                "Expected a login error message, but was: " + alertText
        );
    }



    @When("I submit the login form without credentials")
    public void iSubmitLoginFormWithoutCredentials() {
        if (!driver().findElements(By.xpath("//input[@id='username']")).isEmpty()) {
            driver().findElement(By.xpath("//input[@id='username']")).clear();
        }
        if (!driver().findElements(By.xpath("//input[@id='password']")).isEmpty()) {
            driver().findElement(By.xpath("//input[@id='password']")).clear();
        }
        if (!driver().findElements(By.xpath("//button[@type='submit']")).isEmpty()) {
            driver().findElement(By.xpath("//button[@type='submit']")).click();
        }
    }

    @Then("I should remain on the login page")
    public void iShouldRemainOnLoginPage() {
        iShouldBeOnTheLoginPage();
    }

    @Then("I should see an authentication error message")
    public void iShouldSeeAuthenticationErrorMessage() {
        iShouldSeeLoginErrorMessage();
    }

    @Then("I should see a login validation error")
    public void iShouldSeeLoginValidationError() {
        Assertions.assertTrue(driver().getCurrentUrl().contains("/login"),
                "Expected to remain on /login, but was on: " + driver().getCurrentUrl());
        if (!driver().findElements(CommonLocators.ALERT).isEmpty()) {
            String alertText = driver().findElement(CommonLocators.ALERT).getText();
            Assertions.assertFalse(alertText.isBlank(), "Validation alert was present but empty.");
        }
    }
}
