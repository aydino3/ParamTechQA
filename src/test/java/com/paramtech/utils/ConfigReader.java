package com.paramtech.utils;

import java.io.InputStream;
import java.util.Properties;

public final class ConfigReader {

    private static final Properties PROPS = new Properties();

    static {
        try (InputStream is = ConfigReader.class.getClassLoader()
                .getResourceAsStream("config/test.properties")) {
            if (is == null) {
                throw new RuntimeException("config/test.properties isn't found. (src/test/resources/config/test.properties)");
            }
            PROPS.load(is);
        } catch (Exception e) {
            throw new RuntimeException("test.properties isn't read", e);
        }
    }

    private ConfigReader() {}

    /**
     * Compatibility alias.
     * Some classes use ConfigReader.getProperty(key) style.
     */
    public static String getProperty(String key) {
        return get(key, "");
    }

    /**
     * Compatibility alias with default value.
     */
    public static String getProperty(String key, String defaultValue) {
        return get(key, defaultValue);
    }

    /**
     * Convenience overload.
     */
    public static String get(String key) {
        return get(key, "");
    }

    public static String get(String key, String defaultValue) {
        String v = System.getProperty(key);
        if (v != null && !v.isBlank()) return v.trim();

        v = PROPS.getProperty(key);
        return (v == null || v.isBlank()) ? defaultValue : v.trim();
    }
}
