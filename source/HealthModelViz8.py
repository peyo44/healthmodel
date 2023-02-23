from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
# If MoneyModel.py is where your code is:
#from HealthModel import PatientPatch,HealthAgent, HealthModel
from HealthModel import  HealthModel

from HAutils.clagent import PatientPatch , HealthAgent #Agents

from mesa.visualization.UserParam import UserSettableParameter
import asyncio
#import nest_asyncio
import numpy as np
#nest_asyncio.apply()
from mesa.visualization.ModularVisualization import VisualizationElement
import argparse


parser = argparse.ArgumentParser(description="Fire a Health Model Simulation",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-wi", "--width", default=16, help="grid width (int)")
parser.add_argument("-he", "--height", default=8,help="grid  height (int)")
args = parser.parse_args()


class HistogramModule(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["HistogramModule.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        l_time_to_wait = [agent.illness_duration for agent in model.schedule.agents if  isinstance(agent,PatientPatch)]
        #agent_flatten_list = [item for agent_list in l_time_to_wait for item in agent_list]
        #hist = np.histogram(l_time_to_wait, bins=self.bins)[0]
        return [int(x) for x in hist]


def health_agent_portrayal(agent):
    if agent is None:
        print("none")
        return

    portrayal = {}

    if type(agent) is HealthAgent:
        portrayal["Shape"] = "circle"
        
        # https://icons8.com/web-app/433/sheep
        portrayal["r"] = 0.81156
        portrayal["Layer"] = 1
        #portrayal["text"]="HA"
        portrayal["Filled"]="true"


        if agent.zone=='E':#Remuneration
            portrayal["Color"]="red"
            #portrayal["text"]="E"

        elif agent.zone=='W': #Pas de remuneration
            portrayal["Color"]="#B43E36"
            #portrayal["text"]="W"







    elif type(agent) is PatientPatch:
        if agent.ill and agent.remuneration==1:
            portrayal["Color"] = "Blue"
            portrayal["Filled"]="true"
            #portrayal["text"]="E"


        elif agent.ill and agent.remuneration==0:
            portrayal["Color"] = "#3B72EA" #light blue
            portrayal["Filled"]="false"
            #portrayal["text"]="W"


        elif agent.ill==False and agent.remuneration==1:
            portrayal["Color"] = "Green"
            portrayal["Filled"]="true"
            #portrayal["text"]="E"

        elif agent.ill==False and agent.remuneration==0:
            portrayal["Color"] = "#548C5F" #light green
            portrayal["Filled"]="false"
            #portrayal["text"]="E"



            
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        #portrayal["text"] = "Patient"
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5

    return portrayal
#value=123, min_value=10, max_value=200, step=0.1)


model_params = {
    
                "HA_Number": UserSettableParameter('slider', 'Health Agent Number', value=8,min_value=1,max_value=40,step=1),
                #Pour la V2
                "Distribution" : UserSettableParameter('slider', 'Distribution of Health Agents  by  Area W/E', value=0.5,min_value=0,max_value=1,step=0.05),
                #"HA_Capacity": UserSettableParameter('number', 'HA\'s Capacity', value=0.6,min_value=0,max_value=1,step=0.1),
                "HA_Capacity": UserSettableParameter('choice', 'HA\'s Capacity', value=0.6,choices=[0.4,0.6,0.8]),

                
                "Disposition_Threshold": UserSettableParameter('slider', 'Disposition threshold', value=0.2, min_value=0,max_value=1, step=0.1),
                #Pour la V2
                
                #"threshold_feasability": UserSettableParameter('slider', 'Feasability Threshold', value=0.5,min_value=0, max_value=1,step=0.05),
                "Patient_severity": UserSettableParameter('choice', 'Patient Severity Parameter', value=0.25,choices=[0.25,0.5,0.75]),
                #"Patient_Sigma_severity": UserSettableParameter('number', 'Severity Sigma Parameter', value=0.05),
                
                "Patient_countdown_init": UserSettableParameter('slider', 'Healthy  state cycle  duration', value=3, min_value=1,max_value=20,step=1),
        
                "Parameter_K":  UserSettableParameter('slider', 'Constant k ', value=1, min_value=1,max_value=1,step=0.05),#fixed
                "Illness_rate": UserSettableParameter('slider', 'Illness rate', value=0.5, min_value=0,max_value=1,step=0.05),
                #"GridSize" :UserSettableParameter('slider', 'Grid Size', value=20, min_value=10,max_value=50,step=1), 

                "border_porosity":UserSettableParameter('checkbox', 'Porosity', value=True),
                "peer_contagion":UserSettableParameter('checkbox', 'Peer_contagion', value=False),
                "width":int(args.width),
                "height":int(args.height),
                "gamma_positif":0,
                "gamma_negatif":-0.1 


               }





chart_element1 = ChartModule([{"Label": "Average_disposition", "Color": "#AA0000"},
                             {"Label": "Average_emotional", "Color": "#666666"},
                            {"Label": "Average_cognitive", "Color": "#BBAA33"}])
chart_element2=ChartModule([{"Label" : "Ratio_Ill","Color": "red"},
                            {"Label" : "Ratio_Healthy","Color": "green"}])       

chart_element3=ChartModule([{"Label" : "Average_disposition_W","Color": "red"},
                            {"Label" : "Averge_disposition_E","Color": "green"}])  

chart_element4=ChartModule([{"Label" : "Average_emotional_W","Color": "red"},
                            {"Label" : "Average_emotional_E","Color": "green"}])


chart_element5=ChartModule([{"Label" : "Average_cognitive_W","Color": "red"},
                            {"Label" : "Average_cognitive_E","Color": "green"}])

chart_element6=ChartModule([{"Label" : "Ratio_Ill_W","Color": "red"},
                            {"Label" : "Ratio_Ill_E","Color": "green"}])  




#grid = CanvasGrid(health_agent_portrayal, 10, 10, 500, 500)
grid = CanvasGrid(health_agent_portrayal, model_params["width"],model_params["height"], 500, 500)
#grid = CanvasGrid(health_agent_portrayal, model_params["GridSize"],model_params["GridSize"], 500, 500)
#histogram = HistogramModule(list(range(10)), 200, 500)

#server = ModularServer(HealthModel,[grid,chart_element1,chart_element2,histogram],'Health Model',model_params)
server = ModularServer(HealthModel,[grid,chart_element1,chart_element2,chart_element3,chart_element4,chart_element5,chart_element6],'Health Model',model_params)

server.port = 8521 # The default
server.launch()