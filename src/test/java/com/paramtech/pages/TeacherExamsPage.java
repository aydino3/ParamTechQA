package com.paramtech.pages;

import com.paramtech.locators.TeacherExamsLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.Select;

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

    public boolean isAtList() {
        return isDisplayed(TeacherExamsLocators.H1_EXAMS);
    }

    public void createExam(String title, String description, String durationMinutes, String maxAttempts, String gradingPolicyValue) {
        sendKeys(TeacherExamsLocators.TITLE, title);
        if (description != null) {
            sendKeys(TeacherExamsLocators.DESCRIPTION, description);
        }
        sendKeys(TeacherExamsLocators.DURATION_MINUTES, durationMinutes);
        sendKeys(TeacherExamsLocators.MAX_ATTEMPTS, maxAttempts);

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
}
