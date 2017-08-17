from flask import Flask, render_template, request
import app.controller as controller
import app.poller as poller
from app.updaters.teamcity_updater import TeamCityUpdater
from app.updaters.flash_updater import FlashUpdater
import os
import pwd
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

def username():
    return pwd.getpwuid(os.geteuid()).pw_name

def log_file_path():
    return '/var/tmp/' + username() + 'trafficlights.log'

log_file = log_file_path()
file_handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=3)
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)
    
app.logger.setLevel(logging.DEBUG)
app.logger.info('Starting traffiglights website')
app.logger.info('Running as user ' + username())

try:
    @app.errorhandler(500)
    def internal_error(exception):
        app.logger.exception(exception)
        return exception, 500
                
    def poweroff():
        for i in range(lights.num_indicators):
            lights.set_indicator(i, controller.Controller.BOTH)

        os.system('sudo poweroff')
    
    lights = controller.Controller(controller.FULLSIZE_V1, app.logger)
    lights.add_input_response(0, poweroff)

    app.logger.info('Creating updaters')
    teamcity_updater = TeamCityUpdater(lights, app.logger)
    flash_updater = FlashUpdater(lights, app.logger, enable_lights=False)

    app.logger.debug('Starting poller')
    poller = poller.Poller(lights, [teamcity_updater, flash_updater], app.logger)
    poller.start()
    
    import app.views.index as index
    import app.views.admin as admin
    import app.views.logs as logs
    import app.views.teamcity as teamcity

except Exception as ex:
    app.logger.exception(ex)
    raise

