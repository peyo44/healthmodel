from HAutils.clagent import PatientPatch, HealthAgent
import numpy as np

def pct_ha_by_zone(model):
    dic_nb_zone={
        'W':float(sum([ 1 for agent in model.schedule.agents if ( isinstance(agent,HealthAgent) and agent.zone=='W')])/model.num_agents), #percentage W
        'E':float(sum([ 1 for agent in model.schedule.agents if ( isinstance(agent,HealthAgent) and agent.zone=='E')])/model.num_agents), #percentage E
     }
    return dic_nb_zone


def pct_ha_by_zone_W(model):
    return (pct_ha_by_zone(model)['W'])


def pct_ha_by_zone_E(model):
    return (pct_ha_by_zone(model)['E'])



def average_disposition_by_zone(model,zone):
    agent_disposition = [agent.disposition for agent in model.schedule.agents if isinstance(agent,HealthAgent) and agent.zone==zone]
    if len(agent_disposition)>0:
        return(float(np.mean(agent_disposition)))
    else:
        return(0)

def average_disposition_W(model):
    return(average_disposition_by_zone(model,"W"))

def average_disposition_E(model):
    return(average_disposition_by_zone(model,"E"))


def average_emotional_disposition_by_zone(model,zone):
    agent_disposition = [agent.emotional_disposition for agent in model.schedule.agents if isinstance(agent,HealthAgent) and agent.zone==zone]
    if len(agent_disposition)>0:
        return(float(np.mean(agent_disposition)))
    else:
        return(0)

def average_emotional_disposition_W(model):
    return(average_emotional_disposition_by_zone(model,"W"))

def average_emotional_disposition_E(model):
    return(average_emotional_disposition_by_zone(model,"E"))

        

def average_cognitive_disposition_by_zone(model,zone):
    agent_disposition = [agent.cognitive_disposition for agent in model.schedule.agents if isinstance(agent,HealthAgent) and agent.zone==zone]
    if len(agent_disposition)>0:
        return(float(np.mean(agent_disposition)))
    else:
        return(0)

def average_cognitive_disposition_W(model):
    return(average_cognitive_disposition_by_zone(model,"W"))

def average_cognitive_disposition_E(model):
    return(average_cognitive_disposition_by_zone(model,"E"))




#Fonction de calcul de la disposition moyenne des agents 
def average_disposition(model):
    agent_disposition = [agent.disposition for agent in model.schedule.agents if isinstance(agent,HealthAgent)]
    if len(agent_disposition)>0:
        return(float(np.mean(agent_disposition)))
    else:
        return(0)



def average_emotional_disposition(model):
    agent_disposition = [agent.emotional_disposition for agent in model.schedule.agents if isinstance(agent,HealthAgent)]
    if len(agent_disposition)>0:
        return(float(np.mean(agent_disposition)))
    else:
        return(0)

def average_cognitive_disposition(model):
    agent_disposition = [agent.cognitive_disposition for agent in model.schedule.agents if isinstance(agent,HealthAgent)]
    if len(agent_disposition)>0:
        return(float(np.mean(agent_disposition)))
    else:
        return(0)

#Fonction de calcul du revenu moyen supplémentaire des agents
def average_rs(model):
    agent_rs = [agent.rs for agent in model.schedule.agents if isinstance(agent,HealthAgent)]
    if len(agent_rs)>0:
        return(float(np.mean(agent_rs)))
    else:
        return(0)

#Fonction de calcul du taux de guéris / malade


def  ratio_healthy_total(model):
    #return  ratio healthy
    PatientPatch_list=[ agent for agent in model.schedule.agents if isinstance(agent,PatientPatch)]
    nb_patient=len(PatientPatch_list)
    if nb_patient > 0:
        nb_patient_ill=len([agent for agent in PatientPatch_list if agent.ill==True])
        nb_patient_healthy=len([agent for agent in PatientPatch_list if agent.ill==False])
        return round(float(nb_patient_healthy/nb_patient),2)
    else: 
        return("NA")

def count_agent_by_zone(model,zone):
    list_agent_by_zone=[ agent for agent in model.schedule.agents if isinstance(agent,HealthAgent) and agent.zone==zone]
    return(len(list_agent_by_zone))


def  ratio_healthy_by_zone(model,zone):
        #return  ratio healthy
    PatientPatch_list=[ agent for agent in model.schedule.agents if isinstance(agent,PatientPatch) and agent.zone==zone]
    nb_patient=len(PatientPatch_list)
    if nb_patient > 0:
        nb_patient_ill=len([agent for agent in PatientPatch_list if agent.ill==True])
        nb_patient_healthy=len([agent for agent in PatientPatch_list if agent.ill==False])
        return round(float(nb_patient_healthy/nb_patient),2)
    else:
        return("NA")

def ratio_healthy_W(model):
    return(ratio_healthy_by_zone(model,"W"))

def ratio_healthy_E(model):
    return(ratio_healthy_by_zone(model,"E"))

def  ratio_ill_total(model):
    #return ratio ill 
    PatientPatch_list=[ agent for agent in model.schedule.agents if isinstance(agent,PatientPatch)]
    nb_patient=len(PatientPatch_list)
    if nb_patient >0:
        nb_patient_ill=len([agent for agent in PatientPatch_list if agent.ill==True])
        nb_patient_healthy=len([agent for agent in PatientPatch_list if agent.ill==False])
        return round(float(nb_patient_ill/nb_patient),2)
    else:
        return("NA")

def  ratio_ill_by_zone(model,zone):
    #return ratio ill 
    PatientPatch_list=[ agent for agent in model.schedule.agents if isinstance(agent,PatientPatch) and agent.zone==zone]
    nb_patient=len(PatientPatch_list)
    if nb_patient >0:

        nb_patient_ill=len([agent for agent in PatientPatch_list if agent.ill==True])
        nb_patient_healthy=len([agent for agent in PatientPatch_list if agent.ill==False])
        return round(float(nb_patient_ill/nb_patient),2)
    else:
        return("NA")

def ratio_ill_W(model):
    return(ratio_ill_by_zone(model,"W"))

def ratio_ill_E(model):
    return(ratio_ill_by_zone(model,"E"))