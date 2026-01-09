package com.paramtech.utils;

import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class WaitUtils {

    private final WebDriverWait wait;

    public WaitUtils(WebDriverWait wait) {
        this.wait = wait;
    }

    public WebElement visible(By locator) {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    public WebElement clickable(By locator) {
        return wait.until(ExpectedConditions.elementToBeClickable(locator));
    }

    public void click(By locator) {
        clickable(locator).click();
    }

    public void type(By locator, String text) {
        WebElement el = visible(locator);
        el.clear();
        el.sendKeys(text);
    }

    public void pressEnter(By locator) {
        visible(locator).sendKeys(Keys.ENTER);
    }

    // -------------------- Static helpers (compatibility) --------------------

    /**
     * Compatibility helper used by some step classes.
     * Waits until the element located by {@code locator} is visible.
     */
    public static WebElement waitForVisibility(WebDriver driver, By locator) {
        int timeout = Integer.parseInt(ConfigReader.get("timeoutSeconds", "20"));
        WebDriverWait w = new WebDriverWait(driver, Duration.ofSeconds(timeout));
        return w.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }
}
