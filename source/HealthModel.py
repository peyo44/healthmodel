#!/usr/bin/env python
# coding: utf-8
# 
# ability to set a distinct number of HA per zone
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import  import_yaml  
import numpy as np
import random
import pandas as pd
import pickle

from HAutils.func import pct_ha_by_zone, pct_ha_by_zone_W, pct_ha_by_zone_E # Fonctions statistiques
from HAutils.func import average_disposition, average_emotional_disposition, average_cognitive_disposition, average_rs # Fonctions statistiques
from HAutils.func import average_disposition_E, average_disposition_W
from HAutils.func import average_emotional_disposition_E, average_emotional_disposition_W
from HAutils.func import average_cognitive_disposition_E, average_cognitive_disposition_W
from HAutils.func  import average_rs # Fonctions statistiques

from HAutils.func import ratio_healthy_total, ratio_ill_total #fonctions statistiques
from HAutils.func import ratio_healthy_W,ratio_healthy_E
from HAutils.func import  ratio_ill_W, ratio_ill_E #fonctions statistiques

from HAutils.clagent import PatientPatch , HealthAgent #Agents

#Définition de la classe PatientPatch (immobile)



#Définition de la classse HealthAgent


class HealthModel(Model):
    #Valeurs par défaut du modèle
    HA_Number=3
    Distribution=0.5
    width=10
    height=10
    Disposition_Threshold=0.1
    #threshold_severity=0.5
    Patient_severity=0.5
    Patient_countdown_init=10
    HA_Capacity=0.6
    HA_Emotional_disposition=0 #Neutre au départ = envt 2 à 3 malades
    Parameter_K=0.5         
    #Parameter_Alpha=0.2
    Illness_rate=0.5
    seed=None
    border_porosity=True
    peer_contagion=False
    gamma_positif=0
    gamma_negatif=-0.1


    """A model with some number of agents."""
    def __init__(self, 
    HA_Number=HA_Number, 
    Distribution=Distribution,
    R_zone=1,
    width=width, 
    height=height,
    Disposition_Threshold=Disposition_Threshold,
    Patient_countdown_init=Patient_countdown_init,

    Patient_severity=Patient_severity,

    HA_Capacity=HA_Capacity,

    Parameter_K=Parameter_K,


    Illness_rate=Illness_rate,

    seed=seed,
    table_envt= { 0:0, 1:0.1, 2:0.25,3:0.35,4:0.25,5:0.0,6:-0.25,7:-0.5,8:-0.77,9:-1.0},
    Border_position=0.5, #Positionnement de la frontière entre R=0 et R=k border=0 R = k partout / border=1 : R= 0 partout
    HA_Emotional_disposition=HA_Emotional_disposition,
    border_porosity=border_porosity,
    peer_contagion=peer_contagion,
    gamma_positif=gamma_positif,
    gamma_negatif=gamma_negatif
 

    
    ): 
    
        super().__init__()
        self.width=width
        self.height=height
        self.num_agents = HA_Number #Total number of agent
        self.distribution=Distribution #Repartition rate of agents per zone
        self.num_agents_E=int(self.distribution*self.num_agents) #Set number of agents on West Zone
        self.num_agents_W=HA_Number-self.num_agents_E  #Set number of agents on East Zone
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.Threshold=Disposition_Threshold
        #self.threshold_severity=threshold_severity
        self.Patient_countdown_init=Patient_countdown_init

        self.severity=Patient_severity
        self.capacity=HA_Capacity
        self.emotional_disposition=HA_Emotional_disposition
        
        self.k=Parameter_K
     
        self.Illness_rate=Illness_rate
        self.R_zone=R_zone
        
        self.table_envt=table_envt
        self.border_position=Border_position
        self.border_porosity=border_porosity
        self.peer_contagion=peer_contagion
        self.gamma_positif=gamma_positif
        self.gamma_negatif=gamma_negatif

        #Seed for numpy random library
        np.random.seed(self._seed)
        self.placement_zone= {"East":{"Income" :True ,
                            "zone": "E" , 
                            "num_agent": self.num_agents_E,
                            "min_width":int(self.grid.width/2), 
                            "max_width":self.grid.width},

                            "West": {"Income" :False,
                            "zone": "W" , 
                            "num_agent": self.num_agents_W,
                            "min_width":0, 
                            "max_width":int(self.grid.width/2)}
                            }

        for  elt_zone in self.placement_zone.items():
            # Create Health Agents
            for i in range(int(elt_zone[1]["num_agent"])):
                #capacity=round(self.random.uniform(self.capacity_lb,self.capacity_ub),2)

                a = HealthAgent(self.next_id(), self,self.capacity,self.emotional_disposition)
                self.schedule.add(a)
            # Add the agent to a random grid cell
                (x,y)=(None,None)
                lap_max=10
                lap=0
                agent_position = [ (agent.pos,agent.zone) for agent in a.model.schedule.agents if (isinstance(agent,HealthAgent))]
                agent_position= [elt[0] for elt in agent_position if elt[1]==elt_zone[1]["zone"]]
                while ( (x,y) in agent_position or (x,y) == (None,None) or lap==lap_max): #while occuppied, retry 
                    x = self.random.randrange(int(elt_zone[1]["min_width"]),int(elt_zone[1]["max_width"])) #int(self.model.width)/2
                    y = self.random.randrange(self.grid.height)
                    lap+=1
                
                if lap==lap_max:
                    print("Unable to set agents positions")
                    exit()

                else : #set agent on grid
                    self.grid.place_agent(a, (x, y))
                    a.zone=a.set_zone() #get zone W or East

        
        # Set Patient Patches properties
        for agent, x, y in self.grid.coord_iter():
            #ill = self.random.choice([True, False])
            ill=True
            severity=self.severity
            
            if x >= int(self.width*self.border_position):
                #remuneration=random.choices((0,1),weights=[100-self.remuneration_part,self.remuneration_part],k=1)[0]
                remuneration=1 ###Right Side Remuneration=1
                zone='E'
            else:
                remuneration=0 ###Left Side Remuneration=0
                zone='W'

            #patient = PatientPatch(self.next_id(), (x, y), self,
            #                       ill, severity)
            patient=PatientPatch(self.next_id(),self,ill,severity,remuneration,zone,Patient_countdown_init)
            self.grid.place_agent(patient, (x, y))
            self.schedule.add(patient)
        
        self.datacollector = DataCollector (
            #model_reporters={"Average_disposition": average_disposition})
            #model_reporters={"Average_disposition": average_disposition ,"Average_rs" : average_rs, "Average_motivation": average_motivation,"Ratio_Ill":ratio_ill_total,"Ratio_Healthy":ratio_healthy_total})
            model_reporters={"Average_disposition": average_disposition,
            "Average_disposition_W": average_disposition_W,
            "Average_disposition_E": average_disposition_E,
        

            
            "Average_emotional" :average_emotional_disposition, 
            "Average_emotional_W" :average_emotional_disposition_W, 
            "Average_emotional_E" :average_emotional_disposition_E, 

            
            "Average_cognitive" :average_cognitive_disposition,
            "Average_cognitive_W" :average_cognitive_disposition_W,
            "Average_cognitive_E" :average_cognitive_disposition_E,

            
            "Ratio_Ill":ratio_ill_total,
            "Ratio_Ill_W":ratio_ill_W,
            "Ratio_Ill_E":ratio_ill_E,

            
            "Ratio_Healthy":ratio_healthy_total,
            "Ratio_Healthy_W":ratio_healthy_W,
            "Ratio_Healthy_E":ratio_healthy_E,

            
            "pct_HA_West":pct_ha_by_zone_W,

            "pct_HA_East":pct_ha_by_zone_E},
            
            tables={"Capacity":["ratio_ill_total", "ratio_ill_West","ratio_ill_East","ratio_healthy_total",
            "ratio_healthy_West","ratio_healthy_East","average_emotional_disposition","average_emotional_West","average_emotional_East","average_cognitive_disposition",
            "average_cognitive_West",
            "average_cognitive_East",
            "average_disposition",
            "average_disposition_West",
            "average_disposition_East",
            "HA_capacity",
            "pct_HA_West",
            "pct_HA_East"] }




        )

    def list_agent_type(self,agent_type):
        list_type_agent=[]
        for agent in self.schedule.agent_buffer(shuffled=True):
            if isinstance(agent,agent_type):
                list_type_agent.append(agent)
        return(list_type_agent)
    
    def step(self):
        
        '''Advance the model by one step. First HealthAgent'''
        for agent in self.list_agent_type(HealthAgent):
            agent.step()
        for agent in self.list_agent_type(PatientPatch):
            agent.step()
        self.datacollector.collect(self)
        self.datacollector.add_table_row("Capacity",
        { 
        "ratio_ill_total": ratio_ill_total(self),
        "ratio_ill_West": ratio_ill_W(self),
        "ratio_ill_East": ratio_ill_E(self),

        "ratio_healthy_total": ratio_healthy_total(self),
        "ratio_healthy_West": ratio_healthy_W(self),
        "ratio_healthy_East": ratio_healthy_E(self),

        "average_emotional_disposition": average_emotional_disposition(self),
        "average_emotional_West": average_emotional_disposition_W(self),
        "average_emotional_East": average_emotional_disposition_E(self),

        "average_cognitive_disposition": average_cognitive_disposition(self),
        "average_cognitive_West": average_cognitive_disposition_W(self),
        "average_cognitive_East": average_cognitive_disposition_E(self),


        "average_disposition":    average_disposition(self),
        "average_disposition_West": average_disposition_W(self),
        "average_disposition_East": average_disposition_E(self),



        "HA_capacity": self.capacity,
        "pct_HA_West":pct_ha_by_zone_W(self),
        "pct_HA_East":pct_ha_by_zone_E(self)
        
         }, ignore_missing=True)
        
         
        self.schedule.steps+=1




if __name__=='__main__':

    import argparse
    import os.path

    '''
    def render(model):
        l_time_to_wait = [agent.l_awaiting_state for agent in model.schedule.agents if  isinstance(agent,PatientPatch)]
        #agent_flatten_list = [item for agent_list in l_time_to_wait for item in agent_list]
        hist = np.histogram(l_time_to_wait, bins=10)[0]
        return hist
    '''
    parser = argparse.ArgumentParser(description="Fire a Health Model Simulation",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--output", default="results", help="Output Directory")
    parser.add_argument("-c", "--config", default="conf/HAbatch_conf.yml",help="Configuration File")
    args = parser.parse_args()
    






    l_df=[]
    chemin_fic_res=args.output

    if not  os.path.isdir(chemin_fic_res):
        print(f'{chemin_fic_res} does not exist')
        exit(1)


    fichier_conf_yml=args.config

    try :
        with open(fichier_conf_yml) as f_obj:
            contents = f_obj.read()
    except  FileNotFoundError as E:
    
        msg = "Sorry, the file "+ fichier_conf_yml + "does not exist."
        raise(f'{msg}') # 
        

    l_batch_param=import_yaml.f_dic_batch(fichier_conf=fichier_conf_yml,
    batch_size_limit=50,
    chemin_fic_res=chemin_fic_res,
    suffixe_fic_res="results")
    df_params=pd.DataFrame()


    
    for  lap  in range(len(l_batch_param)):
        

        print(l_batch_param[lap]['var']['BaseVar'])

        
        model=HealthModel(HA_Number=l_batch_param[lap]['var']['BaseVar']['HA_Number'],
        seed=l_batch_param[lap]['var']['BaseVar']['seed'],
        HA_Capacity=l_batch_param[lap]['var']['BaseVar']['HA_Capacity'],
        Disposition_Threshold=l_batch_param[lap]['var']['BaseVar']['Disposition_Threshold'],
        HA_Emotional_disposition=l_batch_param[lap]['var']['BaseVar']['HA_Emotional_disposition'],
        
        Patient_severity=l_batch_param[lap]['var']['BaseVar']['Patient_severity'],
        Patient_countdown_init=l_batch_param[lap]['var']['BaseVar']['Patient_countdown_init'],
        Parameter_K=l_batch_param[lap]['var']['BaseVar']['Parameter_K'],

        Illness_rate=l_batch_param[lap]['var']['BaseVar']['Illness_rate'],
        Border_position=l_batch_param[lap]['var']['BaseVar']['Border_position'])


            
        

        EPOCH=l_batch_param[lap]['var']['BaseVar']['EPOCH']
        print(f'EPOCH {EPOCH}')
        
        for i in range(EPOCH):
            model.step()

        l_df.append(model.datacollector.get_table_dataframe("Capacity"))

        df=pd.concat(l_df)
        #Envoi du des données dans le fichier Paramètres
        df.to_csv(l_batch_param[lap]['fichier'])
        l_df=[]

        new_row={"HA_number":model.num_agents,
        "seed":model._seed,
        "HA_Capacity":model.capacity,
        "HA_Emotional_init":model.emotional_disposition,
        "Disposition_Threshold":model.Threshold,
        "Patient_severity":model.severity,
        "Patient_countdown_init":model.Patient_countdown_init,
        "Parameter_K":model.k,
        "Illness_rate":model.Illness_rate,
        "Border_position":model.border_position
        }
        print(f'new_row :{new_row}')

        df_params = df_params.append(new_row, ignore_index=True)
        print(df_params)  
        df_params.to_csv(chemin_fic_res+'/'+'parametres.csv')

