from time import sleep

from Browser import SupportedBrowsers
from Browser.utils.data_types import KeyAction
from cumulusci.robotframework.CumulusCI import CumulusCI
from cumulusci.robotframework.SalesforceAPI import SalesforceAPI
from robot.api.deco import library
from robot.libraries.BuiltIn import BuiltIn


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QRobot:
    """Initializes the Q Robot Browser"""

    def __init__(self):
        self._builtin = None
        self._cumulusci = None
        self._salesforce_api = None
        self._browser = None

    @property
    def salesforce_api(self):

        """Loads Salesforce API Keywords and methods"""

        if self._salesforce_api is None:
            self._salesforce_api = SalesforceAPI()
        return self._salesforce_api

    @property
    def builtin(self):

        """Loads Builtin Methods"""

        if getattr(self, "_builtin", None) is None:
            self._builtin = BuiltIn()
        return self._builtin

    @property
    def cumulusci(self):

        """Loads Keyword Library for working with CumulusCI from Robot"""

        if getattr(self, "_cumulusci", None) is None:
            self._cumulusci = CumulusCI()
        return self._cumulusci
    
    @property
    def browser(self):

        """Loads Default Browser Instance"""

        if self._browser is None:
            self._browser = self.builtin.get_library_instance("Browser")
        return self._browser

    def _check_for_classic(self):
        """Switch to lightning if we land on a classic page

        This seems to happen randomly, causing tests to fail
        catastrophically. The idea is to detect such a case and
        auto-click the "switch to lightning" link

        """
        try:
            self.browser.get_element("a.switch-to-lightning")
            self.builtin.log(
                "It appears we are on a classic page; attempting to switch to lightning",
                "WARN",
            )
            # just in case there's a modal present we'll try simulating
            # the escape key. Then, click on the switch-to-lightning link
            self.browser.keyboard_key(KeyAction.press, "Escape")
            self.builtin.sleep("1 second")
            self.browser.click("a.switch-to-lightning")
            return True

        except (AssertionError):
            return False 

    def open_q_browser(self, record_video=False):

        """Starts a new browser session with Chromium, performs login and goes to Setup home"""

        # Set Defaults for Browser Instance
        browser = self.builtin.get_variable_value("${BROWSER}", "chrome")
        headless = browser.startswith("headless")
        browser_type = browser[8:] if headless else browser
        browser_type = "chromium" if browser_type == "chrome" else browser_type
        browser_enum = getattr(SupportedBrowsers, browser_type, None)

        # Enable Video Recording (if requested)
        rec=None
        if record_video:
            rec={"dir": "../video"}

        # Open New Browser
        browser_id = self.browser.new_browser(browser=browser_enum, headless=headless)
        context_id = self.browser.new_context(
            viewport={"width": 1920, "height": 1080}, recordVideo=rec
        )
        self.browser.set_browser_timeout("900 seconds")
        sleep(1)

        # Load New Page (Loads with Playwright)
        page_details = self.browser.new_page()

        # Login to the Org
        retries = 0
        while retries < 4:
            try:
                self.browser.go_to(self.cumulusci.login_url(), timeout="120s")
                sleep(1)
                if "lightning" in str(self.browser.get_url()):
                    break
            except Exception as robot_loading_exception:
                print(robot_loading_exception)
                self.browser.take_screenshot()

                # Double Check we have not landed on Classic Layout
                self._check_for_classic()
                
            retries += 1

        if retries >= 3:
            raise Exception("Unable to launch robot. Please try again.")

        # Browse to Setup Page if not there already
        if not str(self.browser.get_url()).endswith("/lightning/setup/SetupOneHome/home"):
            self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/setup/SetupOneHome/home", timeout="120s")

        return browser_id, context_id, page_details

    def close_q_browser(self):

        """Closes All Instances of Browser which have been launched within the session"""

        self.browser.close_browser("ALL")
