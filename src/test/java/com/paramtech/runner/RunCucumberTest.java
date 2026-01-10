package com.paramtech.runner;

import org.junit.platform.suite.api.ConfigurationParameter;
import org.junit.platform.suite.api.IncludeEngines;
import org.junit.platform.suite.api.SelectClasspathResource;
import org.junit.platform.suite.api.Suite;

import static io.cucumber.junit.platform.engine.Constants.GLUE_PROPERTY_NAME;
import static io.cucumber.junit.platform.engine.Constants.FILTER_TAGS_PROPERTY_NAME;

@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features") // veya "features/exam_system"
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "com.paramtech.steps,com.paramtech.hooks")
@ConfigurationParameter(key = FILTER_TAGS_PROPERTY_NAME, value = "@ui")
public class RunCucumberTest { }
