import PySimpleGUI as sg
from serial.tools import list_ports
from SerialReader_Pfeiffer import SerialReader
import Saver
import Plotter
from datetime import datetime
import os
import sys

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
        sg.Text("Waiting...", font=('Helvetica', 30), key='display'),
        sg.Text("", font=('Helvetica', 15), key='udm', justification='right'),
    ],
    [
        sg.Text("L. Zampieri - 10/2023", font=('Helvetica', 8)),
    ]
] ), sg.Column( [[
    sg.Canvas( key='canvas' )
]] ) ]]

window = sg.Window(title='Pfeiffer logger - XP version', layout=layout,margins=(100, 100))
window.finalize()

# Prepare plot
plot = Plotter.Plotter(window['canvas'])
# plot.first_plot()
# plot.figure_controller([],[])
plot.first_draw()

# Read available COM ports
def refresh_ports():
    ports = list( list_ports.comports() )
    window['ports_combo'].update(values=[p.device for p in ports], value=( ports[0].device if len(ports) > 0 else "" ))
refresh_ports()

# Read cwv
sv = Saver.Saver()
window['saved_file'].update( sv.compute_foldername( window['foldername'].get() ) )

sr = SerialReader( sv )

blink_dot = False

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
        os.startfile( sv.compute_foldername( values['foldername'] ) )

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
        
        _, data, udm = sr.getLastData()
        window['display'].update( data )
        window['udm'].update( udm )

        plot.update_data( sr.getAllData() )

    if sv.is_saving():
        blink_dot = not blink_dot
        window['blinking_dot'].update( 'x' if blink_dot else 'o' )

window.close()
sys.exit()