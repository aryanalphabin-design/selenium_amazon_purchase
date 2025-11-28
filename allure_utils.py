import allure
import traceback

def allure_step(name, driver=None):
    def wrapper(func):
        def inner(*args, **kwargs):
            try:
                with allure.step(name):
                    return func(*args, **kwargs)
            except Exception as e:
                # Attach screenshot if driver provided
                if driver:
                    allure.attach(
                        driver.get_screenshot_as_png(),
                        name="Screenshot",
                        attachment_type=allure.attachment_type.PNG
                    )
                    allure.attach(
                        driver.page_source,
                        name="Page Source",
                        attachment_type=allure.attachment_type.HTML
                    )
                
                # Attach traceback
                allure.attach(
                    traceback.format_exc(),
                    name="Error Trace",
                    attachment_type=allure.attachment_type.TEXT
                )
                raise e
        return inner
    return wrapper
