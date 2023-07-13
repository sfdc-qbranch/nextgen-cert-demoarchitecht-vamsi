from time import sleep

from Browser import ElementState
from robot.api.deco import library

from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixNGOKeywords(QbrixRobotTask):

    """Shared Keywords for NGO"""

    def enable_program_benefits(self):
        """
        Enables Program and Benefit Management Settings for NGO Cloud
        """
        self.shared.go_to_setup_admin_page("BenefitManagementSettings/home")
        self.browser.wait_for_elements_state("p:text-is('Program and Benefit Management')", ElementState.visible, '30s')
        checked = "checked" in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 1)")
        checked2 = "checked" in self.browser.get_element_states(
            ":nth-match(label:has-text('Disabled'), 2)")
        if not checked:
            toggle_switch = self.browser.get_element(
                ":nth-match(label:has-text('Disabled'), 1)")
            self.browser.click(toggle_switch)
            sleep(1)
        if not checked2:
            toggle_switch2 = self.browser.get_element(
                ":nth-match(label:has-text('Disabled'), 2)")
            self.browser.click(toggle_switch2)
