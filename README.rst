===================
BW Inventory
===================

This is a simple Python project to take inventory of AkaBlas' belongings.
It currently includes:

.. code-block:: bash

    bwi/  # top level Python package
    ├── bot/  # Functionality to run a Telegram bot to take inventory
    ├── config/  # Configurations for inventory taking and bot
    └── models/  # Pydantic models for inventory items

Installation
============

To install the project, clone the repository and install the dependencies:

.. code-block:: bash

    pip install -r requirements.txt

Usage
=====
To run the bot, execute the following command:

.. code-block:: bash

    python -m bwi.bot

