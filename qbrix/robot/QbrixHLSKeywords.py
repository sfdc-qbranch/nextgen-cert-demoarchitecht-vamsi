from time import sleep
from Browser import ElementState
from robot.api.deco import library
from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixHLSKeywords(QbrixRobotTask):

    """Shared Keywords for HLS"""

    def enable_care_plans(self):
        """
        Enables Care Plans for HLS
        """
        self.shared.go_to_setup_admin_page("CarePlanSettings/home")
        self.browser.wait_for_elements_state("p:text-is('Care Plans')", ElementState.visible, '30s')
        checked = "checked" in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 1)")
        if not checked:
            toggle_switch = self.browser.get_element(
                ":nth-match(label:has-text('Disabled'), 1)")
            self.browser.click(toggle_switch)
            sleep(1)

    def enable_assessments(self):
        """
        Enables Assessments for HLS
        """
        self.shared.go_to_setup_admin_page("AssessmentSettings/home")
        self.browser.wait_for_elements_state("h3:text-is('Guest User Assessments')", ElementState.visible, '30s')
        checked = "checked" in self.browser.get_element_states(".toggle:has-text('Disabled')")
        if not checked:
            self.browser.click(".toggle:has-text('Disabled')")
            sleep(5)
            self.browser.wait_for_elements_state("button:has-text('Turn On')", ElementState.visible, '30s')
            self.browser.click("button:has-text('Turn On')")
            sleep(5)

    def enable_care_plans_grantmaking(self):
        """
        Enables Care Plans Grantmaking for HLS
        """
        self.shared.go_to_setup_admin_page("CarePlanSettings/home")
        self.browser.wait_for_elements_state("p:text-is('Care Plans')", ElementState.visible, '30s')
        checked = "checked" in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 1)")
        if not checked:
            toggle_switch = self.browser.get_element(
                ":nth-match(label:has-text('Disabled'), 1)")
            self.browser.click(toggle_switch)
            sleep(1)

        checked2 = "checked" in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 2)")
        if not checked2:
            toggle_switch = self.browser.get_element(
                ":nth-match(label:has-text('Disabled'), 2)")
            self.browser.click(toggle_switch)
            sleep(2)
            if "visible" in self.browser.get_element_states("button:has-text('Enable')"):
                self.shared.click_button_with_text("Enable")
                sleep(5)
