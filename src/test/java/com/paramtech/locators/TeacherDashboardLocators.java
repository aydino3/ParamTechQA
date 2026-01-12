package com.paramtech.locators;

import org.openqa.selenium.By;

public final class TeacherDashboardLocators {

    public static final By PAGE_H1 = By.xpath("//h1[contains(normalize-space(.), 'Teacher Dashboard')]");
    public static final By QUESTIONS_LINK = By.xpath("//div[contains(@class,'dashboard-card text-center') and contains(normalize-space(.), 'Total Questions')]");
    public static final By EXAMS_LINK = By.xpath("//div[contains(@class,'dashboard-card text-center') and contains(normalize-space(.), 'Total Exams')]");
    public static final By ASSIGNMENTS_LINK = By.xpath("//div[contains(@class,'dashboard-card text-center') and contains(normalize-space(.), 'Graded Attempts')]");
}
