*** Settings ***

# CORE ROBOT LIBRARIES
Library     Browser
Library     Collections
Library     OperatingSystem
Library     String

# CUMULUSCI INTEGRATION LIBRARY
Library     cumulusci.robotframework.CumulusCI    ${org}

# CORE Q ROBOT
Library     QRobot.py
Library     QbrixSharedKeywords.py
Library     QbrixValidationKeywords.py

# CORE - Q BRANCH
Library     QbrixToolingKeywords.py

# PRODUCT - SHARED PLATFORM LIBRARIES
Library     QbrixCMS.py
Library     QbrixEinsteinKeywords.py
Library     QbrixSchedulerKeywords.py
Library     QbrixSurveysKeywords.py

# PRODUCT - MARKETING
Library     QbrixMarketingKeywords.py

# PRODUCT - SALES CLOUD
Library     QbrixSalesCloudKeywords.py

# PRODUCT - SERVICE CLOUD AND SFS
Library     QbrixServiceKeywords.py
Library     QbrixFieldServiceKeywords.py
Library     QbrixVraKeywords.py

# INDUSTRY - COMMERCE CLOUD
Library     QbrixB2BKeywords.py

# INDUSTRY - FINS
Library     QbrixFINSKeywords.py

# INDUSTRY - MFG
Library     QbrixManufacturingKeywords.py

# INDUSTRY - NET ZERO CLOUD
Library     QbrixNetZeroKeywords.py

# INDUSTRY - NON PROFIT CLOUD (NGO)
Library     QbrixNGOKeywords.py

# INDUSTRY - Healthcare Cloud
Library     QbrixHLSKeywords.py

# INDUSTRY - OmniStudio
Library     QbrixDPAKeywords.py

# MULESOFT - Connected app
Library     QbrixMulesoftToolingKeywords.py








