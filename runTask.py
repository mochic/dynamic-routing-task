# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 10:48:22 2021

@author: svc_ccg
"""

import argparse
import json
import os
import subprocess
import requests
import uuid


env = 'DynamicRoutingTaskDev'

parser = argparse.ArgumentParser()
parser.add_argument('params')
parser.add_argument('-o')

args = parser.parse_args()

paramsPath = args.params
paramsDir = os.path.dirname(paramsPath)

with open(paramsPath,'r') as f:
    params = json.load(f)

def get_task_script(output_dir):
    output_dir = uuid.uuid4().hex
    p = subprocess.Popen([
        "git",
        "clone",
        "https://github.com/mochic/dynamic-routing-task.git",
        "&&",
        "git",
        "checkout",
        "production",
        output_dir,
    ], shell=True)
    status_code = p.wait()
    
    if status_code != 0:
        raise Exception("Non-zero exit for checkout: %s" % status_code)
    
    task_script_path = os.path.join(output_dir, "taskScript.py")
    if not os.path.exists(task_script_path):
        raise Exception("Task script not found at expected path: %s" % task_script_path)
    
    return task_script_path


if 'rigName' not in params:
    import time
    import uuid
    import ConfigParser
    from camstim.zro.agent import CAMSTIM_CONFIG_PATH, OUTPUT_DIR
    from camstim.misc import CAMSTIM_CONFIG
    
    params['userName'] = params['user_id']
    params['subjectName'] = params['mouse_id']
    
    taskName = os.path.splitext(os.path.basename(params['taskScript']))[0]
    params['startTime'] = time.strftime('%Y%m%d_%H%M%S',time.localtime())
    params['savePath'] = os.path.join(OUTPUT_DIR,taskName + '_' + params['subjectName'] + '_' + params['startTime'] + '.hdf5')
    foraging_id = uuid.uuid4()
    params['sessionId'] = foraging_id.hex
    params['limsUpload'] = True
    params['configPath'] = CAMSTIM_CONFIG_PATH
    
    config = ConfigParser.ConfigParser()
    config.read(CAMSTIM_CONFIG_PATH)
    params['rotaryEncoderSerialPort'] = eval(config.get('DigitalEncoder','serial_device'))
    params['behavNidaqDevice'] = eval(config.get('Behavior','nidevice'))
    params['rewardLines'] = eval(config.get('Reward','reward_lines'))
    params['lickLines'] = eval(config.get('Licksensing','lick_lines'))
    
    params['computerName'] = os.environ['aibs_comp_id']
    params['rigName'] = os.environ['aibs_rig_id']
    
    waterCalibration = CAMSTIM_CONFIG['shared']['water_calibration'][params['computerName']]
    params['waterCalibrationSlope'] = waterCalibration['slope']
    params['waterCalibrationIntercept'] = waterCalibration['intercept']
    
    soundCalibration = CAMSTIM_CONFIG['sound_calibration']
    params['soundCalibrationFit'] = [soundCalibration[param] for param in 'abc']
    
    paramsPath = os.path.join(paramsDir,'taskParams.json')
    with open(paramsPath,'w') as f:
        json.dump(params,f)


toRun = ('"C:\\Program Files\\AIBS_MPE\\SetVol\\SetVol.exe" unmute 100' + '\n' +
         'call activate ' + env + '\n' +
         'python ' + '"' + params['taskScript'] + '" ' + '"' + paramsPath + '"')

batFile = os.path.join(paramsDir,'toRun.bat')

with open(batFile,'w') as f:
    f.write(toRun)
    
p = subprocess.Popen([batFile])
p.wait()


if 'limsUpload' in params and params['limsUpload']:
    from shutil import copyfile
    from camstim.lims import LimsInterface, write_behavior_trigger_file
    
    lims = LimsInterface()
    triggerDir = lims.get_trigger_dir(params['subjectName'])
    incomingDir = os.path.dirname(triggerDir.rstrip('/'))
    outputFileName = os.path.basename(params['savePath'])
    outputPath = os.path.join(incomingDir,outputFileName)
    triggerFileName = os.path.splitext(outputFileName)[0] + '.bt'
    triggerPath = os.path.join(triggerDir,triggerFileName)
    copyfile(params['savePath'],outputPath)
    write_behavior_trigger_file(triggerPath,params['subjectName'],params['sessionId'],params['userName'],outputPath) 
    print(outputPath)  
    print(triggerPath)

    import imp
    mtrain_uploader = imp.load_source('mtrain_uploader', '//allen/programs/mindscope/workgroups/dynamicrouting/DynamicRoutingTask/dynamicrouting_behavior_session_mtrain_upload.py')
    mtrain_uploader.add_behavior_session_to_mtrain_upload_queue(filename=outputFileName, foraging_id=str(foraging_id))