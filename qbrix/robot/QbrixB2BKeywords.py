from time import sleep
from Browser import ElementState
from robot.api.deco import library
from qbrix.core.qbrix_robot_base import QbrixRobotTask


@library(scope='GLOBAL', auto_keywords=True, doc_format='reST')
class QbrixB2BKeywords(QbrixRobotTask):
    """Commerce Cloud Keywords"""

    def get_store_id(self, store_name: str):
        """
        Gets the Store Id for a given Store Name
            Args:
                store_name (str): The name of the store
                
            Returns:
                (str) Store Id Value if found, else None
        """

        if store_name is None:
            raise ValueError("Profile Name must be specified")

        results = self.salesforceapi.soql_query(f"SELECT Id from WebStore where Name = '{store_name}' LIMIT 1")

        if results["totalSize"] == 1:
            return results["records"][0]["Id"]

        return None

    def start_reindex(self, store_name):

        """
        Starts the Reindex for a given store
        
        Args:
            store_name (str): The name of the store
        """

        index_button_selector = ":nth-match(button.slds-button:text-is('Rebuild Index'):visible, 1)"
        index_confirmation_selector = ":nth-match(button.slds-button:text-is('Rebuild'):visible, 1)"

        # Go To Index Page
        store_id = self.get_store_id(store_name)
        if store_id:
            self.browser.go_to(
                f"{self.cumulusci.org.instance_url}/lightning/page/commerceSearch?lightning__webStoreId={store_id}&ws=%2Flightning%2Fr%2FWebStore%2F{store_id}%2Fview")
            self.browser.wait_for_elements_state(index_button_selector, ElementState.visible, '10s')
            if "enabled" in self.browser.get_element_states(index_button_selector):
                self.browser.click(index_button_selector)
                sleep(2)
                self.browser.click(index_confirmation_selector)
                sleep(2)

    def enable_b2b2c_for_sdo(self, store_name):

        """
        Enables integrations for a given Store Name
        
        Args:
            store_name (str): The name of the store.
        """

        # Go To Tax Page and enable Tax Integration
        integration_button_selector = ":nth-match(button.slds-button:text-is('Link Integration'):visible, 1)"
        dialog_row_selector = "tr.slds-hint-parent:has-text('Standard Tax') >> label.slds-checkbox_faux"
        next_button_selector = "div.modal-footer >> button.nextButton:text-is('Next'):visible"
        confirm_button_selector = "div.modal-footer >> button.nextButton:text-is('Confirm'):visible"

        store_id = self.get_store_id(store_name)
        if store_id:
            self.browser.go_to(
                f"{self.cumulusci.org.instance_url}/lightning/page/storeDetail?lightning__webStoreId={store_id}&ws=%2Flightning%2Fr%2FWebStore%2F{store_id}%2Fview&storeDetail__selectedTab=store_tax")
            self.browser.wait_for_elements_state(integration_button_selector, ElementState.visible, '15s')
            self.browser.click(integration_button_selector)
            sleep(2)
            self.browser.click(dialog_row_selector)
            self.browser.click(next_button_selector)
            sleep(2)
            self.browser.click(confirm_button_selector)

            # Go To Shipping Calculation Page and Apply Integration
            self.browser.go_to(
                f"{self.cumulusci.org.instance_url}/lightning/page/storeDetail?lightning__webStoreId={store_id}&ws=%2Flightning%2Fr%2FWebStore%2F{store_id}%2Fview&storeDetail__selectedTab=store_shipping")
            self.browser.wait_for_elements_state(integration_button_selector, ElementState.visible, '15s')
            self.browser.click(integration_button_selector)
            sleep(2)

            # Go To Card Payment Gateway Page and Apply Integration
            self.browser.go_to(
                f"{self.cumulusci.org.instance_url}/lightning/page/storeDetail?lightning__webStoreId={store_id}&ws=%2Flightning%2Fr%2FWebStore%2F{store_id}%2Fview&storeDetail__selectedTab=store_payment")
            self.browser.wait_for_elements_state(integration_button_selector, ElementState.visible, '15s')
            self.browser.click(integration_button_selector)
            sleep(2)

        sleep(5)
