package com.paramtech.pages;

import com.paramtech.locators.TeacherQuestionsLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.Select;

public class TeacherQuestionsPage extends BasePage {
    public TeacherQuestionsPage(WebDriver driver) {
        super(driver);
    }

    public void openList() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/teacher/questions");
    }

    public void openNew() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/teacher/questions/new");
    }

    public boolean isAtList() {
        return isDisplayed(TeacherQuestionsLocators.H1_QUESTIONS);
    }

    public void createMultipleChoice(String questionText, String optionA, String optionB, String optionC, String optionD, String correctValue, String tags) {
        sendKeys(TeacherQuestionsLocators.QUESTION_TEXT, questionText);

        Select type = new Select(driver.findElement(TeacherQuestionsLocators.QUESTION_TYPE));
        type.selectByValue("multiple_choice");

        sendKeys(TeacherQuestionsLocators.OPTION_A, optionA);
        sendKeys(TeacherQuestionsLocators.OPTION_B, optionB);
        sendKeys(TeacherQuestionsLocators.OPTION_C, optionC);
        sendKeys(TeacherQuestionsLocators.OPTION_D, optionD);

        Select correct = new Select(driver.findElement(TeacherQuestionsLocators.CORRECT_ANSWER));
        correct.selectByValue(correctValue);

        sendKeys(TeacherQuestionsLocators.TAGS, tags);
        click(TeacherQuestionsLocators.SUBMIT);
    }

    public void createTrueFalse(String questionText, String correctValue, String tags) {
        sendKeys(TeacherQuestionsLocators.QUESTION_TEXT, questionText);
        Select type = new Select(driver.findElement(TeacherQuestionsLocators.QUESTION_TYPE));
        type.selectByValue("true_false");

        Select correct = new Select(driver.findElement(TeacherQuestionsLocators.CORRECT_ANSWER));
        correct.selectByValue(correctValue);

        sendKeys(TeacherQuestionsLocators.TAGS, tags);
        click(TeacherQuestionsLocators.SUBMIT);
    }

    public boolean isQuestionInList(String questionText) {
        // Search by text anywhere on page (table or cards)
        return driver.getPageSource().contains(questionText);
    }

    public boolean isValidationErrorShown() {
        return driver.getPageSource().contains("required") || driver.getPageSource().toLowerCase().contains("error") || driver.getPageSource().contains("Please");
    }
}
