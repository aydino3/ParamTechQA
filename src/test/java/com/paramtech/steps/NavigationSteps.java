package com.paramtech.steps;

import com.paramtech.driver.DriverFactory;
import com.paramtech.locators.CommonLocators;
import com.paramtech.utils.ConfigReader;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.jupiter.api.Assertions;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

import static com.paramtech.utils.WaitUtils.waitForVisibility;

public class NavigationSteps {

    private WebDriver driver() {
        return DriverFactory.getDriver();
    }

    private void waitUrlContains(String fragment) {
        new WebDriverWait(driver(), Duration.ofSeconds(Long.parseLong(ConfigReader.getProperty("timeoutSeconds"))))
                .until(ExpectedConditions.urlContains(fragment));
    }

    @When("I click the teacher link to questions")
    public void iClickTeacherLinkToQuestions() throws InterruptedException {
        waitForVisibility(driver(), CommonLocators.NAV_TEACHER_QUESTIONS);
        driver().findElement(CommonLocators.NAV_TEACHER_QUESTIONS).click();
        Thread.sleep(1500);
    }

    @Then("I should be on the teacher questions page")
    public void iShouldBeOnTeacherQuestionsPage() {
        waitUrlContains("/teacher/questions");
    }

    @When("I click the teacher link to exams")
    public void iClickTeacherLinkToExams() {
        waitForVisibility(driver(), CommonLocators.NAV_TEACHER_EXAMS);
        driver().findElement(CommonLocators.NAV_TEACHER_EXAMS).click();
    }

    @Then("I should be on the teacher exams page")
    public void iShouldBeOnTeacherExamsPage() {
        waitUrlContains("/teacher/exams");
    }
}