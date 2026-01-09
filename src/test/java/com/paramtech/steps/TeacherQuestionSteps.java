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
        p.openList();
        p.openNewQuestion();
        p.createMultipleChoiceQuestion(
                qText,
                "Option A",
                "Option B",
                "Option C",
                "Option D",
                "A",
                "automation"
        );
        Assertions.assertTrue(p.isOnQuestionsList(), "Expected to be back on questions list after creation");
    }

    @When("I create a new true/false question")
    public void iCreateNewTrueFalseQuestion() {
        String qText = "Auto TF " + UUID.randomUUID();
        TestContext.put("lastQuestionText", qText);

        TeacherQuestionsPage p = page();
        p.openList();
        p.openNewQuestion();
        p.createTrueFalseQuestion(qText, "true", "automation");
        Assertions.assertTrue(p.isOnQuestionsList(), "Expected to be back on questions list after creation");
    }

    @Then("I should see the new question in the questions list")
    public void iShouldSeeTheNewQuestionInTheList() {
        String qText = TestContext.get("lastQuestionText", String.class);
        TeacherQuestionsPage p = page();
        p.openList();
        Assertions.assertTrue(p.isQuestionPresentInList(qText), "Expected question to be present in list: " + qText);
    }

    @When("I try to create a question without question text")
    public void iTryToCreateQuestionWithoutText() {
        TeacherQuestionsPage p = page();
        p.openList();
        p.openNewQuestion();

        // Leave question_text empty
        p.createMultipleChoiceQuestion(
                "",
                "Option A",
                "Option B",
                "Option C",
                "Option D",
                "A",
                "automation"
        );
    }

    @Then("I should see a question validation error")
    public void iShouldSeeQuestionValidationError() {
        // Depending on HTML validation/server-side validation, we may stay on form or show alert.
        // The most stable assertion: we should NOT land on questions list.
        TeacherQuestionsPage p = page();
        Assertions.assertFalse(p.isOnQuestionsList(), "Expected to NOT be on list when validation fails");
    }
}
