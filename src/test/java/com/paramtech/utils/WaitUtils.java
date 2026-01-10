package com.paramtech.utils;

import org.openqa.selenium.*;
import org.openqa.selenium.interactions.Actions;
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

    /**
     * Robust click:
     * 1) scrollIntoView(center)
     * 2) wait clickable
     * 3) normal click
     * 4) Actions click
     * 5) JS click (fallback)
     */
    public void click(By locator) {
        WebDriver driver = waitDriver();

        // presence -> scroll
        WebElement el = wait.until(ExpectedConditions.presenceOfElementLocated(locator));
        scrollIntoViewCenter(driver, el);

        // kısa pause (animation/transition)
        sleep(150);

        // clickable -> click dene
        el = clickable(locator);

        try {
            el.click();
            return;
        } catch (ElementNotInteractableException ignored) {}

        // Actions ile dene
        try {
            new Actions(driver).moveToElement(el).pause(Duration.ofMillis(150)).click().perform();
            return;
        } catch (WebDriverException ignored) {}

        // JS click fallback
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", el);
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

    public static WebElement waitForVisibility(WebDriver driver, By locator) {
        int timeout = Integer.parseInt(ConfigReader.get("timeoutSeconds", "20"));
        WebDriverWait w = new WebDriverWait(driver, Duration.ofSeconds(timeout));
        return w.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    public static void waitForPageToLoad(WebDriver driver, long timeoutSeconds) {
        new WebDriverWait(driver, Duration.ofSeconds(timeoutSeconds))
                .until(d -> ((JavascriptExecutor) d)
                        .executeScript("return document.readyState")
                        .equals("complete"));
    }

    /**
     * Static robust click helper (istersen bazı yerlerde direkt driver ile çağır)
     */
    public static void click(WebDriver driver, By locator) {
        int timeout = Integer.parseInt(ConfigReader.get("timeoutSeconds", "20"));
        WebDriverWait w = new WebDriverWait(driver, Duration.ofSeconds(timeout));
        WaitUtils u = new WaitUtils(w);
        u.click(locator);
    }

    // -------------------- internal helpers --------------------

    private WebDriver waitDriver() {
        // WebDriverWait içinden driver’ı almak için reflection’a girmiyoruz.
        // Selenium 4'te WebDriverWait, FluentWait'ten gelir ama driver field erişimi yok.
        // Bu yüzden "clickable(locator)" üzerinden driver çekiyoruz:
        // element.getWrappedDriver yok; en temiz yol:
        // -> clickable(locator) çağırmadan önce presence element alırken driver gerekli
        // Burada hack yapmayalım: driver’ı scroll için element üzerinden değil, JS executor ile alacağız:
        // wait.until(...) zaten driver ile çalışıyor, ama driver’ı direkt vermez.
        // O yüzden aşağıdaki pratik yöntem: ConfigReader’da driver tutulmuyor.
        // En mantıklısı: WaitUtils oluşturulurken driver’ı da ver.
        // AMA senin mevcut yapını bozmadan: scroll kısmını clickable elementten sonra yapacağız.
        // Bu methodu kullanmak için DriverFactory gibi global erişimin varsa onu kullan.
        // Aşağıdaki satırı kendi projendeki driver erişimine göre düzenle:
        return com.paramtech.driver.DriverFactory.getDriver();
    }

    private void scrollIntoViewCenter(WebDriver driver, WebElement el) {
        try {
            ((JavascriptExecutor) driver).executeScript(
                    "arguments[0].scrollIntoView({block:'center', inline:'center'});", el
            );
        } catch (JavascriptException ignored) {}
    }

    private void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException ignored) {}
    }
}
