from time import sleep
from Browser import ElementState, SelectAttribute
from robot.api.deco import library
from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixMulesoftToolingKeywords(QbrixRobotTask):

    """Mulesoft Keywords for Robot"""

    def enable_connected_mule_tool(self):
        """ Enables Data Tool Connected App Settings"""
        iframe_selector = self.shared.iframe_handler()
        self.browser.wait_for_elements_state(f"{iframe_selector} .btn:has-text('Manage Profiles')", ElementState.visible, "15s")
        self.browser.click(f"{iframe_selector} .btn:has-text('Manage Profiles')")
        self.browser.wait_for_elements_state(f"{iframe_selector} h1:text-is('Application Profile Assignment')", ElementState.visible, "15s")
        if not "checked" in self.browser.get_element_states(f"{iframe_selector} tr:has-text('System Administrator') >> input"):
            self.browser.click(f"{iframe_selector} tr:has-text('System Administrator') >> input")
            self.browser.click(f"{iframe_selector} .btn:has-text('Save')")
            sleep(2)
