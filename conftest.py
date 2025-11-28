import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from datetime import datetime
import allure


@pytest.fixture(scope="module")
def driver(request):
    """Provide a maximized Chrome driver and register it on the test node."""
    options = Options()
    # options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    def teardown():
        driver.quit()

    # expose driver to hooks that run after the test
    request.addfinalizer(teardown)
    return driver
    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture screenshot on test failure and report test status."""
    outcome = yield
    rep = outcome.get_result()
    
    # Report test status to Allure
    if rep.when == "call":
        if rep.passed:
            allure.attach(
                f"✓ Test PASSED: {item.name}",
                name="Test Status",
                attachment_type=allure.attachment_type.TEXT
            )
        elif rep.failed:
            driver = item.funcargs.get("driver")
            if driver:
                # Create screenshots directory if it doesn't exist
                screenshots_dir = "screenshots"
                os.makedirs(screenshots_dir, exist_ok=True)
                
                # Take screenshot with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(screenshots_dir, f"failure_{item.name}_{timestamp}.png")
                driver.save_screenshot(screenshot_path)
                print(f"\nScreenshot saved: {screenshot_path}")
                
                # Attach failure info to Allure
                allure.attach(
                    f"✗ Test FAILED: {item.name}\n\nError: {rep.longrepr}",
                    name="Test Failure Details",
                    attachment_type=allure.attachment_type.TEXT
                )