package com.paramtech.utils;

import java.util.HashMap;
import java.util.Map;

public final class TestContext {
    private static final ThreadLocal<Map<String, Object>> CTX = ThreadLocal.withInitial(HashMap::new);

    private TestContext() {}

    public static void put(String key, Object value) {
        CTX.get().put(key, value);
    }

    @SuppressWarnings("unchecked")
    public static <T> T get(String key, Class<T> clazz) {
        Object value = CTX.get().get(key);
        if (value == null) return null;
        return (T) value;
    }

    public static void clear() {
        CTX.get().clear();
    }
}
