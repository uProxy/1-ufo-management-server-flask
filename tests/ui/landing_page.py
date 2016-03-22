"""Landing page module for testing."""

from selenium.webdriver.common.by import By

from layout import UfOPageLayout

class LandingPage(UfOPageLayout):

  """Home page action methods and locators."""

  # pylint: disable=too-few-public-methods

  TITLE = (By.TAG_NAME, 'h2')
  INSTRUCTION = (By.TAG_NAME, 'h4')
