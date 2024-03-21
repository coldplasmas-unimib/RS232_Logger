import PySimpleGUI as sg
from serial.tools import list_ports
# from SerialReader_Ozone import SerialReader, WindowTitle, FileExt, ProbesCount
from SerialReader_Demo import SerialReader, WindowTitle, FileExt, ProbesCount
import Saver
import Plotter
from datetime import datetime, timedelta
import os
import sys
import numpy as np
import threading
# from requests import request

layout = [[ sg.Column( [
    [
        sg.Combo([], key='ports_combo', expand_x=True,
                 size=(50, 10), readonly=True),
        sg.Button('Connect', key="connect_btn"),
        sg.Button('Refresh', key="refresh_btn"),
    ],
    [
        sg.Text("Folder name:"),
        sg.Input(default_text=datetime.now().strftime(
            "%Y%m%d"), enable_events = True, key='foldername')
    ],
    [
        sg.Text("Will save on: ", key='status'),
        sg.Text("", key = 'saved_file')
    ],
    [
        sg.Button('Start saving', key="start_btn", disabled=True),
        sg.Button('Stop saving', key="stop_btn", disabled=True),
        sg.Button('View folder', key="viewfolder_btn"),
        sg.Text("", key = 'blinking_dot')
    ],
    [
        sg.Multiline('Data', size=(50, 10), key='data_text',
                     autoscroll=True, disabled=True)],
    [
        sg.Column( [ [
            sg.Text("Waiting...", font=('Helvetica', 30), key='display_{}'.format(i)),
            sg.Text("", font=('Helvetica', 15), key='udm_{}'.format(i), justification='right'),
        ] for i in range( ProbesCount ) ] )
    ],
    # [
    #     sg.Button('Enable notifier', key="notifier_btn", disabled=False),
    #     sg.Text("t.me/rs232_notifications")
    # ],
    [
        sg.Button('Reset plot', key="reset_btn"),
    ],
    [
        sg.Text("L. Zampieri - 03/2024", font=('Helvetica', 8)),
    ]
] ), sg.Column( [[
    sg.Canvas( key='canvas' )
]] ) ]]

window = sg.Window(title= WindowTitle + ' logger - XP version', layout=layout,margins=(100, 100))
window.finalize()

# Prepare plot
plot = Plotter.Plotter(window['canvas'])
# plot.first_plot()
# plot.figure_controller([],[])
plot.first_draw( ProbesCount )

# Read available COM ports
def refresh_ports():
    ports = list( list_ports.comports() )
    window['ports_combo'].update(values=[p.device for p in ports], value=( ports[0].device if len(ports) > 0 else "" ))
refresh_ports()

# Read cwv
sv = Saver.Saver( FileExt )
window['saved_file'].update( sv.compute_foldername( window['foldername'].get() ) )

sr = SerialReader( sv )

blink_dot = False
# notifier = False

# def notify_on_telegram():
#     threading.Thread(target=notify_on_telegram_worker).start()

# def notify_on_telegram_worker():
#     request('GET','https://api.telegram.org/bot6465337103:AAF_EosxW6iQRntjMH5vxaU_DlCu4ovk85g/sendMessage?chat_id=@rs232_notifications&text=Stabile', timeout=1, verify=False)
#     return

while True:
    event, values = window.read(timeout=100)
    # print( event )

    if event == 'refresh_btn':
        refresh_ports()

    if event == 'connect_btn':
        sr.connect(values['ports_combo'])

        window['connect_btn'].update(disabled=True)
        window['refresh_btn'].update(disabled=True)
        window['ports_combo'].update(disabled=True)
        window['start_btn'].update(disabled=False)

    if event == 'viewfolder_btn':
        sv.ensure_folder_exists( sv.compute_foldername( values['foldername'] ) )
        os.startfile( sv.compute_foldername( values['foldername'] ) )

    # if event == 'notifier_btn':
    #     notifier = True
    #     window['notifier_btn'].update(disabled=True)

    if event == 'foldername':
        window['foldername'].update( Saver.Saver.clean_foldername( values['foldername'] ) )

    if event == 'start_btn':
        window['saved_file'].update( sv.start_saving( values['foldername'] ) )
        window['status'].update( "Saving on: " )

        window['start_btn'].update(disabled=True)
        window['stop_btn'].update(disabled=False)

    if event == 'stop_btn':
        sv.stop_saving()
        window['saved_file'].update( sv.compute_foldername( values['foldername'] ) )
        window['status'].update( "Will save in: ", text_color='white' )
        window['blinking_dot'].update( '' )

        window['start_btn'].update(disabled=False)
        window['stop_btn'].update(disabled=True)


    if event == sg.WIN_CLOSED:
        sr.close()
        break

    if sr.newData:
        window['data_text'].update(
            values['data_text'] + '\n' + sr.makeDisplayableData(sr.getNewData()))
        
        data = sr.getLastData()
        for i in range( ProbesCount ):
            window['display_{}'.format(i)].update( data[i*2+1] )
            window['udm_{}'.format(i)].update( data[i*2+2] )

        plot.update_data( sr.getAllData() )

        # if( notifier ):
        #     # Select data of last 5 minutes:
        #     min_ago_5 = datetime.now() - timedelta( minutes=5 )
        #     deviation = np.ptp( [ d[1] for d in sr.getAllData() if d[0] > min_ago_5 ] )
        #     if( deviation == 0 ):
        #         notifier = False
        #         window['notifier_btn'].update(disabled=False)
        #         notify_on_telegram()

    if sv.is_saving():
        blink_dot = not blink_dot
        window['blinking_dot'].update( 'x' if blink_dot else 'o' )

    if event == 'reset_btn':
        plot.reset( sr.getAllData() )

window.close()
sys.exit()