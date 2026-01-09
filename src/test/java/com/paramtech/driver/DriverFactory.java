package com.paramtech.driver;

import com.paramtech.utils.ConfigReader;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public final class DriverFactory {

    private static final ThreadLocal<WebDriver> TL_DRIVER = new ThreadLocal<>();

    private DriverFactory() {}

    public static WebDriver getDriver() {
        return TL_DRIVER.get();
    }

    public static void initDriver() {
        if (TL_DRIVER.get() != null) return;

        String browser = ConfigReader.get("browser", "chrome").toLowerCase();
        boolean headless = Boolean.parseBoolean(ConfigReader.get("headless", "false"));

        if (!"chrome".equals(browser)) {
            throw new IllegalArgumentException("For now, only chrome supported. browser=" + browser);
        }

        WebDriverManager.chromedriver().setup();

        ChromeOptions options = new ChromeOptions();
        if (headless) options.addArguments("--headless=new");
        options.addArguments("--start-maximized");

        TL_DRIVER.set(new ChromeDriver(options));
    }

    public static void quitDriver() {
        try {
            WebDriver d = TL_DRIVER.get();
            if (d != null) d.quit();
        } finally {
            TL_DRIVER.remove();
        }
    }
}
