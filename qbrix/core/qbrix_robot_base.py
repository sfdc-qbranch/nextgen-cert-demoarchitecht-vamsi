from robot.libraries.BuiltIn import BuiltIn
from cumulusci.robotframework.SalesforceAPI import SalesforceAPI
from cumulusci.robotframework.CumulusCI import CumulusCI
from qbrix.robot.QbrixSharedKeywords import QbrixSharedKeywords


class QBrixRobotLibrary():

    """Base Library for Q Robot Keyword Libraries"""

    def __init__(self):
        self._builtin = None
        self._cumulusci = None
        self._salesforceapi = None
        self._browser = None

    @property
    def salesforceapi(self):

        """Loads Salesforce API Keywords and methods"""

        if self._salesforceapi is None:
            self._salesforceapi = SalesforceAPI()
        return self._salesforceapi

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


class QbrixRobotTask(QBrixRobotLibrary):

    """Base Class For Q Brix Robot Keyword Libraries"""

    def __init__(self):
        super().__init__()
        self._shared = None
    
    @property
    def shared(self):

        """Loads Q Robot Shared Keywords and Methods"""

        if self._shared is None:
            self._shared = QbrixSharedKeywords()
        return self._shared
