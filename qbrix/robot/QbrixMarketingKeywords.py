from time import sleep
from Browser import ElementState, SelectAttribute
from robot.api.deco import library
from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixMarketingKeywords(QbrixRobotTask):

    """Marketing Cloud Keywords for Robot"""

    def enable_pardot_setting(self):
        """ Enables Pardot Setting"""
        self.shared.go_to_setup_admin_page("PardotSetupAssistant/home")
        self.browser.wait_for_elements_state("div:text-is('B2B Marketing Setup Assistant')", ElementState.visible,
                                             '15s')
        self.browser.click(".slds-button:has-text('Send Your First Email')")
        self.browser.wait_for_elements_state(
            "span:text-is('Complete the required steps to send your first Account Engagement email.')", ElementState.visible,
            '15s')
        checked = "checked" in self.browser.get_element_states(":nth-match(span.slds-checkbox_faux,1)")
        if not checked:
            self.browser.click(":nth-match(span.slds-checkbox_faux,1)")
            sleep(1)

    def enable_pardot_app(self):
        """ Enables Pardot Connected App Settings"""
        self.shared.go_to_setup_admin_page("ConnectedApplication/home")
        self.browser.click("iframe >>> a:text-is('b2bma_canvas')")
        sleep(5)
        self.browser.click("iframe >>> .btn:has-text('Edit Policies')")
        sleep(5)
        self.browser.select_options_by("iframe >>> #userpolicy", SelectAttribute.text,
                                       "Admin approved users are pre-authorized")
        sleep(4)
        self.browser.click("iframe >>> .btn:has-text('Save')")
        sleep(1)

    def create_pardot_template(self):
        """ Enables Pardot Connected App Settings"""
        self.browser.go_to(f"{self.cumulusci.org.instance_url}/lightning/o/EmailTemplate/home")
        self.browser.wait_for_elements_state("a:has-text('New Email Template')", ElementState.visible, '30s')
        self.browser.click("a:has-text('All Email Templates')")
        sleep(5)
        visible = "visible" in self.browser.get_element_states(
            ".slds-table:has-text('Annual Customer Conference Invitation')")
        if not visible:
            self.browser.click("a:has-text('New Email Template')")
            self.browser.wait_for_elements_state("h2:has-text('New Email Template')", ElementState.visible, '30s')
            self.browser.fill_text(".forcePageBlockItem:has-text('Email Template Name') >> input",
                                   "Annual Customer Conference Invitation")
            self.browser.fill_text(".forcePageBlockItem:has-text('Description') >> input",
                                   "Pardot - Annual Customer Conference Invitation")
            self.browser.fill_text(".forcePageBlockItem:has-text('Subject') >> input",
                                   "Join us for our annual conference")
            self.browser.click("button[title='Save']")
            sleep(5)

    def enable_territory_management(self):
        """ Enables Maps Territory Planning Settings"""
        self.shared.go_to_setup_admin_page("Territory2Settings/home")
        sleep(5)
        visible = "visible" in self.browser.get_element_states(":nth-match(iframe,1) >>> button:has-text('Enable Enterprise Territory Management')")
        if visible:
            button_to_click = self.browser.get_element(":nth-match(iframe,1) >>> button:has-text('Enable Enterprise Territory Management')")
            self.browser.click(button_to_click)
            sleep(1)
