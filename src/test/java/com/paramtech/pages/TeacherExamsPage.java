package com.paramtech.pages;

import com.paramtech.locators.TeacherExamsLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class TeacherExamsPage extends BasePage {
    public TeacherExamsPage(WebDriver driver) {
        super(driver);
    }

    public void openList() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/teacher/exams");
    }

    public void openNew() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/teacher/exams/new");
    }

    // Alias used by feature step implementations
    public void openNewExam() {
        openNew();
    }

    public boolean isAtList() {
        return isDisplayed(TeacherExamsLocators.H1_EXAMS);
    }

    // Alias used by step definitions
    public boolean isOnExamsList() {
        return isAtList();
    }

    public void createExam(String title, String description, String durationMinutes, String maxAttempts, String gradingPolicyValue) {
        sendKeys(TeacherExamsLocators.NAME, title);
        if (description != null && !driver.findElements(TeacherExamsLocators.DESCRIPTION).isEmpty()) {
            sendKeys(TeacherExamsLocators.DESCRIPTION, description);
        }
        sendKeys(TeacherExamsLocators.DURATION_MINUTES, durationMinutes);
        if (maxAttempts != null && !maxAttempts.isBlank() && !driver.findElements(TeacherExamsLocators.MAX_ATTEMPTS).isEmpty()) {
            sendKeys(TeacherExamsLocators.MAX_ATTEMPTS, maxAttempts);
        }
Select gradingPolicy = new Select(driver.findElement(TeacherExamsLocators.GRADING_POLICY));
        gradingPolicy.selectByValue(gradingPolicyValue);

        click(TeacherExamsLocators.SUBMIT);
    }

    public boolean isExamInList(String title) {
        return driver.getPageSource().contains(title);
    }

    public boolean isValidationErrorShown() {
        return driver.getPageSource().contains("required") || driver.getPageSource().toLowerCase().contains("error") || driver.getPageSource().contains("Please");
    }

    public boolean isExamPresentInList(String title) {
        // Liste sayfasında exam adı geçen satırı arıyoruz
        By examTitleInList = By.xpath("//*[normalize-space(text())='" + title + "']");
        return count(examTitleInList) > 0;
    }

    private final By SUCCESS_ALERT = By.cssSelector("div.alert.alert-success");

    public boolean waitForSuccessMessageContains(String expectedText) {
        WebElement alert = new WebDriverWait(driver, Duration.ofSeconds(20))
                .until(ExpectedConditions.visibilityOfElementLocated(SUCCESS_ALERT));

        String actual = alert.getText().trim();
        return actual.contains(expectedText);
    }

}
