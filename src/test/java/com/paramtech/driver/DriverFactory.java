package com.paramtech.driver;

import com.paramtech.utils.ConfigReader;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

public final class DriverFactory {

    private static final ThreadLocal<WebDriver> TL_DRIVER = new ThreadLocal<>();
    private static final ThreadLocal<Path> TL_PROFILE_DIR = new ThreadLocal<>();

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

        // ✅ Her testte temiz profil (en kritik kısım)
        try {
            Path tmpProfile = Files.createTempDirectory("selenium-chrome-profile-");
            TL_PROFILE_DIR.set(tmpProfile);
            options.addArguments("--user-data-dir=" + tmpProfile.toAbsolutePath());
            options.addArguments("--profile-directory=Default");
        } catch (IOException e) {
            throw new RuntimeException("Failed to create temp Chrome profile dir", e);
        }

        // ✅ Password Manager / Leak Detection / Breach uyarısını kapat (PREF + FEATURE + ARG)
        Map<String, Object> prefs = new HashMap<>();
        prefs.put("credentials_enable_service", false);
        prefs.put("profile.password_manager_enabled", false);

        // Leak detection ayarları (Chrome sürümüne göre isim değişebiliyor diye ikisini de kapatıyoruz)
        prefs.put("profile.password_manager_leak_detection", false);
        prefs.put("profile.password_manager_leak_detection_enabled", false);

        // (Gerekirse) SafeBrowsing kapat — leak detection bunun üzerinden çalışabiliyor
        prefs.put("safebrowsing.enabled", false);

        // Bildirimleri kapat (opsiyonel)
        prefs.put("profile.default_content_setting_values.notifications", 2);

        options.setExperimentalOption("prefs", prefs);

        // Chrome feature flag’leri (opsiyonel ama ekledim)
        options.addArguments("--disable-features=PasswordLeakDetection,PasswordManagerOnboarding");

        // Eski Chrome’larda işe yarayan ek flag (zararsız)
        options.addArguments("--disable-save-password-bubble");

        // İlk açılış saçmalıkları
        options.addArguments("--no-first-run");
        options.addArguments("--no-default-browser-check");

        // Genel stabilite
        options.addArguments("--disable-gpu");
        options.addArguments("--disable-dev-shm-usage");

        if (headless) {
            options.addArguments("--headless=new");
            options.addArguments("--window-size=1920,1080");
        } else {
            options.addArguments("--start-maximized");
        }

        TL_DRIVER.set(new ChromeDriver(options));
    }

    public static void quitDriver() {
        try {
            WebDriver d = TL_DRIVER.get();
            if (d != null) d.quit();
        } finally {
            TL_DRIVER.remove();

            // temp profile temizle
            Path dir = TL_PROFILE_DIR.get();
            TL_PROFILE_DIR.remove();
            if (dir != null) {
                try {
                    // basit temizlik: klasör boş değilse sorun çıkabilir, ama çoğu durumda yeterli
                    Files.walk(dir)
                            .sorted((a, b) -> b.compareTo(a))
                            .forEach(p -> {
                                try { Files.deleteIfExists(p); } catch (IOException ignored) {}
                            });
                } catch (IOException ignored) {}
            }
        }
    }
}
