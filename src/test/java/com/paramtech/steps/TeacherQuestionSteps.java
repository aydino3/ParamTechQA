package com.paramtech.steps;

import com.paramtech.driver.DriverFactory;
import com.paramtech.pages.TeacherQuestionsPage;
import com.paramtech.utils.TestContext;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.jupiter.api.Assertions;

import java.util.UUID;

public class TeacherQuestionSteps {

    private TeacherQuestionsPage page() {
        return new TeacherQuestionsPage(DriverFactory.getDriver());
    }

    @When("I create a new multiple-choice question")
    public void iCreateNewMultipleChoiceQuestion() {
        String qText = "Auto MCQ " + UUID.randomUUID();
        TestContext.put("lastQuestionText", qText);

        TeacherQuestionsPage p = page();
        p.openNewQuestion();

        p.createMultipleChoiceQuestion(
                qText,
                "Auto body for: " + qText,
                "Option A",
                "Option B",
                "Option C",
                "Option D",
                "Option E",
                "A",
                "automation"
        );
    }

    @When("I create a new true||false question")
    public void iCreateANewTrueFalseQuestion() {
        String qText = "Auto TF " + UUID.randomUUID();
        TestContext.put("lastQuestionText", qText);

        TeacherQuestionsPage p = page();
        p.openNewQuestion();

        p.createTrueFalseQuestion(qText, true, "automation");

    }

    @Then("I should see the new question in the questions list")
    public void iShouldSeeTheNewQuestionInTheList() {
        String qText = TestContext.get("lastQuestionText", String.class);

        TeacherQuestionsPage p = page();
        p.openListSearch(qText);

        org.openqa.selenium.support.ui.WebDriverWait wait =
                new org.openqa.selenium.support.ui.WebDriverWait(DriverFactory.getDriver(), java.time.Duration.ofSeconds(30));

        Boolean found = wait.until(d -> d.getPageSource().toLowerCase().contains(qText.toLowerCase()));

        Assertions.assertTrue(found, "Expected question to be present in list: " + qText);
    }


    @When("I try to create a question without a question text")
    public void iTryToCreateQuestionWithoutText() {
        TeacherQuestionsPage p = page();
        p.openNewQuestion();

        p.createMultipleChoiceQuestion(
                "",
                "",
                "Option A",
                "Option B",
                "Option C",
                "Option D",
                "Option E",
                "A",
                "automation"
        );
    }

    @Then("I should see a question validation error")
    public void iShouldSeeQuestionValidationError() {
        TeacherQuestionsPage p = page();

        String url = DriverFactory.getDriver().getCurrentUrl().toLowerCase();

        Assertions.assertTrue(
                url.contains("/teacher/questions/new"),
                "Expected to stay on New Question page when validation fails, but URL was: " + url
        );

        Assertions.assertTrue(
                p.isValidationErrorShown(),
                "Expected some validation message to be shown (required/error/please...)"
        );
    }
}
