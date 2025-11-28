import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

keyword = "smartphone charger"


def log_assertion(condition, message):
    """Helper to log assertion results to Allure"""
    status = "✓ PASSED" if condition else "✗ FAILED"
    allure.attach(f"{status}: {message}", "Assertion Result", allure.attachment_type.TEXT)
    assert condition, message

@allure.title("Amazon purchase flow with full-step assertion visibility")
def test_amazon_purchase_flow(driver):
    wait = WebDriverWait(driver, 10)

    with allure.step("1. Open Amazon homepage"):
        driver.get("https://www.amazon.in")
        # Wait for search box to be present (better than time.sleep)
        wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        current_url = driver.current_url.lower()
        allure.attach(f"Current URL: {current_url}", "URL Check", allure.attachment_type.TEXT)
        log_assertion("amazon" in current_url, "Amazon homepage opened successfully")

    with allure.step("2. Search for product"):
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        log_assertion(search_box.is_displayed(), "Search box is visible")
        search_box.send_keys(keyword, Keys.ENTER)
        # Wait for search results to load (better than time.sleep)
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        ))
        search_url = driver.current_url.lower()
        allure.attach(f"Search URL: {search_url}", "Search Results", allure.attachment_type.TEXT)
        log_assertion("s?k=" in search_url, f"Search results loaded for '{keyword}'")

    with allure.step("3. Click first product result"):
        first_result = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")
        ))
        log_assertion(first_result.is_displayed(), "First product result is visible")
        first_result.find_element(By.TAG_NAME, "a").click()
        # Wait for new window to open
        wait.until(lambda driver: len(driver.window_handles) > 1)

    with allure.step("4. Switch to product page"):
        driver.switch_to.window(driver.window_handles[-1])
        # Wait for product page to load
        wait.until(EC.presence_of_element_located((By.ID, "add-to-cart-button")))
        product_url = driver.current_url.lower()
        allure.attach(f"Product URL: {product_url}", "Product Page", allure.attachment_type.TEXT)
        log_assertion("amazon" in product_url, "Product page opened successfully")

    with allure.step("5. Add product to cart"):
        add_to_cart = wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-button")))
        log_assertion(add_to_cart.is_displayed(), "Add to Cart button is visible")
        add_to_cart.click()
        # Wait for success message or cart to update
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Added') or contains(text(), 'cart')]")
        ))
        allure.attach("Product added to cart successfully", "Action Status", allure.attachment_type.TEXT)

    with allure.step("6. Open cart page"):
        cart_btn = wait.until(EC.element_to_be_clickable((By.ID, "nav-cart")))
        cart_btn.click()
        # Wait for cart page to load
        wait.until(EC.url_contains("cart"))
        cart_url = driver.current_url.lower()
        allure.attach(f"Cart URL: {cart_url}", "Cart Page", allure.attachment_type.TEXT)
        log_assertion("cart" in cart_url, "Cart page opened successfully")

    with allure.step("7. Validate cart contains at least 1 item"):
        cart_items = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.sc-list-item")
        ))
        item_count = len(cart_items)
        allure.attach(f"Cart Items Count: {item_count}", "Cart Validation", allure.attachment_type.TEXT)
        log_assertion(item_count > 0, f"Cart contains {item_count} item(s)")
