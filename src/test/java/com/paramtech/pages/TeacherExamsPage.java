package com.paramtech.pages;

import com.paramtech.locators.TeacherExamsLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.By;
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

    public void openNewExam() {
        openNew();
    }

    public boolean isAtList() {
        return isDisplayed(TeacherExamsLocators.H1_EXAMS);
    }

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
    public boolean isExamPresentInList(String title) {
        By examTitleInList = By.xpath("//*[normalize-space(text())='" + title + "']");
        return count(examTitleInList) > 0;
    }
}
