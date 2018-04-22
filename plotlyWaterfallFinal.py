import plotly
plotly.tools.set_credentials_file(username='AukiJuanDiaz', api_key='nGLV1fHOIB1UuzeW0rpk')

'''
This file triggers the generation of a waterfall diagramm
Eight input parameters are needed  as int:
TotalPassengersStranded,
Walking,
AlternativeHVVPotential,
AlternativeHVVActual,
BikeSharingPotential,
BikeSharingActual,
CarSharingPotential,
CarSharingActual
'''

'''
Help for those, where Python does not find directly the installed plotly
* Open a nex Python Shell, preferable 3.6
import sys
sys.path.append('<directory, where this file is>')
import <name of this file>
'''

import plotly.plotly as py
import plotly.graph_objs as go

def calculateWaterfall(TotalPassengersStranded, Walking, AlternativeHVVPotential, AlternativeHVVActual, BikeSharingPotential, BikeSharingActual, CarSharingPotential, CarSharingActual):

    # Calculations:
    blankUnderWalking = TotalPassengersStranded - Walking
    heightIntermediate1 = blankUnderWalking
    blankUnderAlternativeHVVPotential = heightIntermediate1 - AlternativeHVVPotential
    blankUnderAlternativeHVVActual = heightIntermediate1 - AlternativeHVVActual
    heightIntermediate2 = blankUnderAlternativeHVVActual
    
    blankUnderBikeSharingPotential = heightIntermediate2 - BikeSharingPotential
    blankUnderBikeSharingActual = heightIntermediate2 - BikeSharingActual
    heightIntermediate3 = blankUnderBikeSharingActual
    
    blankUnderCarSharingPotential = heightIntermediate3 - CarSharingPotential
    blankUnderCarSharingActual = heightIntermediate3 - CarSharingActual

    passengersRemaining = heightIntermediate3 - CarSharingActual
    
    x_data = ['Passengers<br>at Station',
              'Walk to<br>Destination',
              'Intermediate<br>Result',
              'Alternative HVV<br>Routing Potential',
              'Alternative HVV<br>Routing Actual',
              'Intermediate<br> Result ',
              'Bike Sharing<br>Potential',
              'Bike Sharing<br>Actual',
              'Intermediate<br>  Result  ',
              'Mobility Sharing<br>Potential',
              'Mobility Sharing<br>Actual',
              'Remaining<br>Passengers']
    # y_data = [textTotalPassengersStranded, textAlternativeHVV, 0, 0, 0, 0, 0, 0, 0, 0] #height of textes in columns
    # text = [str(TotalPassengersStranded), str(AlternativeHVV), '', '', '', '', '', '', '', ''] #textes in colums

    # Base without color
    trace0 = go.Bar(
        x=x_data,
        y=[0, blankUnderWalking, 0, blankUnderAlternativeHVVPotential, blankUnderAlternativeHVVActual, 0, blankUnderBikeSharingPotential, blankUnderBikeSharingActual, 0, blankUnderCarSharingPotential, blankUnderCarSharingActual, 0],
        marker=dict(
            color='rgba(1,1,1, 0.0)',
        )
    )
    # Passengers at beginning and remaining at end
    trace1 = go.Bar(
        x=x_data,
        y=[TotalPassengersStranded, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, passengersRemaining],
        marker=dict(
            color='rgba(95, 95, 102, 0.7)',
            line=dict(
                color='rgba(95, 95, 102, 1.0)',
                width=2,
            )
        )
    )

    # Passengers intermediate results 
    trace1b = go.Bar(
        x=x_data,
        y=[0, 0, heightIntermediate1, 0, 0, heightIntermediate2, 0, 0, heightIntermediate3, 0, 0, 0],
        marker=dict(
            color='rgba(161, 161, 163, 0.5)',
            line=dict(
                color='rgba(161, 161, 163, 1.0)',
                width=2,
            )
        )
    )
    
    
    # Bike Sharing Actual
    trace2 = go.Bar(
        x=x_data,
        y=[0, 0, 0, 0, 0, 0, 0, BikeSharingActual, 0, 0, 0, 0],
        marker=dict(
            color='rgba(141, 10, 25, 0.7)',
            line=dict(
                color='rgba(141, 10, 25, 1.0)',
                width=2,
            )
        )
    )

    # Bike Sharing Potential
    trace2b = go.Bar(
        x=x_data,
        y=[0, 0, 0, 0, 0, 0, BikeSharingPotential, 0, 0, 0, 0, 0],
        marker=dict(
            color='rgba(219, 64, 82, 0.5)',
            line=dict(
                color='rgba(219, 64, 82, 1.0)',
                width=2,
            )
        )
    )
    
    # Car Sharing Actual
    trace3 = go.Bar(
        x=x_data,
        y=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, CarSharingActual, 0],
        marker=dict(
            color='rgba(11, 121, 52, 0.7)',
            line=dict(
                color='rgba(11, 121, 52, 1.0)',
                width=2,
            )
        )
    )
    # Car Sharing Potential
    trace3b = go.Bar(
        x=x_data,
        y=[0, 0, 0, 0, 0, 0, 0, 0, 0, CarSharingPotential, 0, 0],
        marker=dict(
            color='rgba(50, 171, 96, 0.5)',
            line=dict(
                color='rgba(50, 171, 96, 1.0)',
                width=2,
            )
        )
    )
    
    # Walking
    trace4 = go.Bar(
        x=x_data,
        y=[0, Walking, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        marker=dict(
            color='rgba(255, 241, 17, 0.5)', #yellow
            line=dict(
                color='rgba(255, 241, 17, 1.0)',
                width=2,
            )
        )
    )

    # HVV Potential
    trace5 = go.Bar(
        x=x_data,
        y=[0, 0, 0, AlternativeHVVPotential, 0, 0, 0, 0, 0, 0, 0, 0],
        marker=dict(
            color='rgba(16, 87, 208, 0.5)', #light blue
            line=dict(
                color='rgba(16, 87, 208, 1.0)',
                width=2,
            )
        )
    )

    # HVV Actual
    trace5b = go.Bar(
        x=x_data,
        y=[0, 0, 0, 0, AlternativeHVVActual, 0, 0, 0, 0, 0, 0, 0],
        marker=dict(
            color='rgba(7, 47, 116, 0.7)', #dark blue
            line=dict(
                color='rgba(7, 47, 116, 1.0)',
                width=2,
            )
        )
    )
    

    
    data = [trace0, trace1, trace1b, trace2, trace2b, trace3, trace3b, trace4, trace5, trace5b]
    layout = go.Layout(
        title='Traffic Guide',
        barmode='stack',
        paper_bgcolor='rgba(245, 246, 249, 1)',
        plot_bgcolor='rgba(245, 246, 249, 1)',
        showlegend=False
    )

    '''
    annotations = []

    for i in range(0, 9):
        annotations.append(dict(x=x_data[i], y=y_data[i], text=text[i],
                                      font=dict(family='Arial', size=18,
                                      color='rgba(245, 246, 249, 1)'),
                                      showarrow=False,))
        layout['annotations'] = annotations
    '''
    
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='waterfall-bar-profit')


calculateWaterfall(800,300,200,150,150,40,200,100)
