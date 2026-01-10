package com.paramtech.pages;

import com.paramtech.locators.TeacherQuestionsLocators;
import com.paramtech.utils.ConfigReader;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;
import java.util.List;

public class TeacherQuestionsPage extends BasePage {

    public TeacherQuestionsPage(WebDriver driver) {
        super(driver);
    }

    // ---------------- NAV ----------------
    public void openList() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/teacher/questions");
    }

    public void openNewQuestion() {
        driver.get(ConfigReader.getProperty("baseUrl") + "/teacher/questions/new");
    }

    public boolean isAtList() {
        return isDisplayed(TeacherQuestionsLocators.H1_QUESTIONS);
    }

    // ---------------- CREATE (MCQ) ----------------
    public void createMultipleChoiceQuestion(
            String title,
            String body,
            String optionA,
            String optionB,
            String optionC,
            String optionD,
            String optionE,
            String correctOptionLetter,
            String tag
    ) {
        // title + body
        sendKeys(TeacherQuestionsLocators.TITLE, title);

        // BODY textarea varsa doldur
        if (!driver.findElements(TeacherQuestionsLocators.BODY).isEmpty()) {
            sendKeys(TeacherQuestionsLocators.BODY, body);
        }

        // difficulty (input/select)
        if (!driver.findElements(TeacherQuestionsLocators.DIFFICULTY_INPUT).isEmpty()) {
            sendKeys(TeacherQuestionsLocators.DIFFICULTY_INPUT, "1");
        } else if (!driver.findElements(TeacherQuestionsLocators.DIFFICULTY_SELECT).isEmpty()) {
            new Select(driver.findElement(TeacherQuestionsLocators.DIFFICULTY_SELECT)).selectByValue("1");
        }

        // type
        if (!driver.findElements(TeacherQuestionsLocators.QUESTION_TYPE).isEmpty()) {
            new Select(driver.findElement(TeacherQuestionsLocators.QUESTION_TYPE)).selectByValue("multiple_choice");
        }

        // Ensure 5 option inputs
        int safety = 0;
        while (driver.findElements(TeacherQuestionsLocators.OPTION_TEXT_INPUTS).size() < 5 && safety++ < 10) {
            if (!driver.findElements(TeacherQuestionsLocators.ADD_OPTION_BUTTON).isEmpty()) {
                click(TeacherQuestionsLocators.ADD_OPTION_BUTTON);
            } else break;
        }

        List<WebElement> optionInputs = driver.findElements(TeacherQuestionsLocators.OPTION_TEXT_INPUTS);

        if (optionInputs.size() > 0) { optionInputs.get(0).clear(); optionInputs.get(0).sendKeys(optionA); }
        if (optionInputs.size() > 1) { optionInputs.get(1).clear(); optionInputs.get(1).sendKeys(optionB); }
        if (optionInputs.size() > 2) { optionInputs.get(2).clear(); optionInputs.get(2).sendKeys(optionC); }
        if (optionInputs.size() > 3) { optionInputs.get(3).clear(); optionInputs.get(3).sendKeys(optionD); }
        if (optionInputs.size() > 4) { optionInputs.get(4).clear(); optionInputs.get(4).sendKeys(optionE); }

        // correct checkbox index
        int idx = 0; // default A
        if (correctOptionLetter != null) {
            String c = correctOptionLetter.trim().toUpperCase();
            if ("B".equals(c)) idx = 1;
            else if ("C".equals(c)) idx = 2;
            else if ("D".equals(c)) idx = 3;
            else if ("E".equals(c)) idx = 4;
        }

        List<WebElement> checks = driver.findElements(TeacherQuestionsLocators.OPTION_CORRECT_CHECKBOXES);
        if (checks.size() > idx && !checks.get(idx).isSelected()) {
            checks.get(idx).click();
        }

        // tag
        if (tag != null && !tag.isBlank() && !driver.findElements(TeacherQuestionsLocators.TAGS).isEmpty()) {
            sendKeys(TeacherQuestionsLocators.TAGS, tag);
        }

        // submit
        click(TeacherQuestionsLocators.SUBMIT);
    }

    // ---------------- CREATE (TRUE/FALSE) ----------------
    public void createTrueFalseQuestion(String title, boolean correctIsTrue, String tag) {
        sendKeys(TeacherQuestionsLocators.TITLE, title);

        if (!driver.findElements(TeacherQuestionsLocators.BODY).isEmpty()) {
            sendKeys(TeacherQuestionsLocators.BODY, "Auto-generated body for: " + title);
        }

        if (!driver.findElements(TeacherQuestionsLocators.DIFFICULTY_INPUT).isEmpty()) {
            sendKeys(TeacherQuestionsLocators.DIFFICULTY_INPUT, "1");
        } else if (!driver.findElements(TeacherQuestionsLocators.DIFFICULTY_SELECT).isEmpty()) {
            new Select(driver.findElement(TeacherQuestionsLocators.DIFFICULTY_SELECT)).selectByValue("1");
        }

        if (!driver.findElements(TeacherQuestionsLocators.QUESTION_TYPE).isEmpty()) {
            new Select(driver.findElement(TeacherQuestionsLocators.QUESTION_TYPE)).selectByValue("true_false");
        }

        if (correctIsTrue) {
            if (!driver.findElements(TeacherQuestionsLocators.TRUE_CORRECT).isEmpty()) click(TeacherQuestionsLocators.TRUE_CORRECT);
        } else {
            if (!driver.findElements(TeacherQuestionsLocators.FALSE_CORRECT).isEmpty()) click(TeacherQuestionsLocators.FALSE_CORRECT);
        }

        if (tag != null && !tag.isBlank() && !driver.findElements(TeacherQuestionsLocators.TAGS).isEmpty()) {
            sendKeys(TeacherQuestionsLocators.TAGS, tag);
        }

        click(TeacherQuestionsLocators.SUBMIT);
    }

    // ---------------- SUCCESS ALERT ASSERT ----------------
    private final By SUCCESS_ALERT = By.xpath("//*[contains(@class,'alert') and contains(@class,'success')]");

    public boolean waitForSuccessMessageContains(String expectedText) {
        WebElement alert = new WebDriverWait(driver, Duration.ofSeconds(20))
                .until(ExpectedConditions.visibilityOfElementLocated(SUCCESS_ALERT));

        String actual = alert.getText().trim().toLowerCase();
        return actual.contains(expectedText.toLowerCase());
    }

    // ---------------- LIST CHECK (PAGINATION FIX) ----------------
    public boolean isQuestionPresentInList(String qText) {
        int maxPages = 15;

        for (int page = 0; page < maxPages; page++) {

            // satır satır ara
            List<WebElement> rows = driver.findElements(TeacherQuestionsLocators.QUESTIONS_TABLE_ROWS);
            for (WebElement row : rows) {
                if (row.getText() != null && row.getText().contains(qText)) {
                    return true;
                }
            }

            // next var mı?
            List<WebElement> nextButtons = driver.findElements(TeacherQuestionsLocators.PAGINATION_NEXT);
            if (nextButtons.isEmpty()) {
                return false;
            }

            // next'e bas ve sayfanın değişmesini bekle
            WebElement firstRowBefore = rows.isEmpty() ? null : rows.get(0);
            nextButtons.get(0).click();

            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
            if (firstRowBefore != null) {
                wait.until(ExpectedConditions.stalenessOf(firstRowBefore));
            } else {
                wait.until(ExpectedConditions.visibilityOfElementLocated(TeacherQuestionsLocators.H1_QUESTIONS));
            }
        }

        return false;
    }

    public boolean waitUntilQuestionAppears(String qText) {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(30));

        wait.until(ExpectedConditions.visibilityOfElementLocated(
                TeacherQuestionsLocators.H1_QUESTIONS
        ));

        return wait.until(d -> isQuestionPresentInList(qText));
    }
    public boolean isValidationErrorShown() {
        String src = driver.getPageSource();
        if (src == null) return false;

        String s = src.toLowerCase();

        // Hem İngilizce hem TR olası validasyon mesajları
        return s.contains("required")
                || s.contains("error")
                || s.contains("please")
                || s.contains("validation")
                || s.contains("zorunlu")
                || s.contains("hata")
                || s.contains("lütfen");
    }

}
