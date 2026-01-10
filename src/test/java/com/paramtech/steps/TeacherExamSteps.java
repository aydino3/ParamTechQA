package com.paramtech.steps;

import com.paramtech.driver.DriverFactory;
import com.paramtech.pages.TeacherExamsPage;
import com.paramtech.utils.TestContext;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.jupiter.api.Assertions;

import java.util.UUID;

public class TeacherExamSteps {

    private TeacherExamsPage page() {
        return new TeacherExamsPage(DriverFactory.getDriver());
    }

    @When("I create a new exam")
    public void iCreateANewExam() {
        String title = "Auto Exam " + UUID.randomUUID();
        TestContext.put("lastExamTitle", title);

        TeacherExamsPage p = page();
        p.openList();
        p.openNewExam();
        p.createExam(title, "Created by automated test", "30", "1", "after_end");

    }

    @Then("I should see the new exam in the exams list")
    public void iShouldSeeNewExamInList() {
        String title = TestContext.get("lastExamTitle", String.class);
        TeacherExamsPage p = page();
        p.openList();
        Assertions.assertTrue(p.isExamPresentInList(title), "Expected exam to be present in list: " + title);
    }

    @When("I try to create an exam without a title")
    public void iTryCreateExamWithoutTitle() {
        TeacherExamsPage p = page();
        p.openList();
        p.openNewExam();
        p.createExam("", "", "30", "1", "after_end");
    }

    @Then("I should see an exam validation error")
    public void iShouldSeeExamValidationError() {
        TeacherExamsPage p = page();
        Assertions.assertFalse(p.isOnExamsList(), "Expected to NOT be on exams list when validation fails");
    }
}
