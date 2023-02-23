from mesa import Agent
import HAutils.func as func

class PatientPatch(Agent):
    '''
    A patch of Patient that gets  ill at fixed rate and -hopefully- gets treated by a HealthAgent
    '''

    def __init__(self, unique_id, model, ill, severity,remuneration,zone,countdown_init):
        '''
        Creates a new agent PatientPatch

        Args:
            ill : (boolean) Whether the PatientPathc  is sick or not
            countdown: Time for the PatientPatch to become sick again
        '''
        super().__init__(unique_id, model)
        self.ill = self.model.random.choices([True,False],weights=[self.model.Illness_rate,1-self.model.Illness_rate])[0] #Ill  or not depending on Illness_rate
        self.severity=severity #Float [0,1] 
        self.remuneration=remuneration #Integer  {0,1}
        self.zone=zone #East (remuneration==1) or West (remuneration=0)
        self.countdown_init=countdown_init #Integer
        self.countdown=countdown_init #Integer
        self.illness_duration=0
        self.l_awaiting_state=[]
        self.l_patient_record=[]
    
#Affiche les attributs du Patient - a modulariser - fichier de config à prévoir    
    def list_attr(self):

        dic={ "Id":self.unique_id,
        "Position":self.pos,
        "Ill" : self.ill,
        "Severity":str(self.severity),
        "Zone" : self.zone,
        "Countdown" : self.countdown,
        "Remuneration":self.remuneration,
        "Patient_record":self.l_patient_record}

  
        print("--------")
        for k,v in dic.items(): #Affichage du dictionnaire
            print(f'{k} : {v}')
        print("--------\n")

        return dic
   

#PatientPatch.step() defini par la méthode compute_state()
    def step(self):
        self.compute_state()
        

#compute_state() définit 3 attributs de PatientPatch
# Si ill==true on positionne le countdown à countdown_init+1 (pourquoi ??)
# Si ill==false on décrémente le countdown (ok) , ill devient True si countdown=0 
# On repositionne le countdown et on recalcule severity  
    def compute_state(self):
        #np.random.seed(self.model._seed)

        self.l_patient_record.append(self.ill) #Keep track of patient's health
        if (self.ill==True): #ill
            self.countdown=self.countdown_init+1
            self.illness_duration+=1
            self.l_awaiting_state.append(self.illness_duration)
            self.severity=self.model.severity
        if (self.ill==False): #healthy
             
            self.illness_duration=0 #on remet le compteur à zero après avoir stocké 
            self.countdown-=1
            self.severity=0 #Healthy
            if self.countdown==0:
                self.ill=True #redevient malade si plus de crédits temps
                self.countdown=self.countdown_init+1 # Pourquoi

     


#Définition de la classse HealthAgent
class HealthAgent(Agent):
    
    """An agent with fixed initial skill."""
    def __init__(self, unique_id, model,capacity,emotional_disposition):
        super().__init__(unique_id, model)
        self.capacity = capacity #Capacité de l'agent
        self.rs=0 #RS revenu dependant de son action 
        self.social_envt= 0.5 #Pas utilisé pour le moment
        self.disposition  = self.capacity #Attention !! doit 
        self.acted=False
        self.emotional_disposition=emotional_disposition
        self.cognitive_disposition=self.capacity
        self.peer_contagion=0
        self.envt_impact=0
        self.zone=None
    
    def step(self):
        self.move() # move wherever possible  toward feasable act exclude green&black patches       
        self.set_zone() #assign new zone location
        self.take_action() #if D > F
        self.update_rs() # additional income

        self.compute_envt_impact()
        self.compute_cognitive_disposition() # cognitive = mean(Capacity, RS)
        self.compute_emotional_disposition() # emotional dispo 1/2 * Prev_dispo + 1/2  * Envt_Impact) 
        self.compute_peer_contagion() #
        self.compute_disposition()#Compute Disposition to act

        '''
        self.take_action()
        self.uptdate_parameters
        
        if self.disposition < model.Threshold: #No action undertaken
            return
        elif self.disposition >= model.Threshold:
            self.motivation = self.compute_motivation()
        
        uptdate self parameters
      
        '''
    def list_attr(self):
        dic={ "Id":self.unique_id,
            "Position":self.pos,
            "Capacity" : self.capacity,
            "Zone" : self.zone,
            "Acted" : self.acted,
            "Remuneration":self.rs,
            "Envt_impact":self.envt_impact,
            "Peer_contagion":self.peer_contagion,
            "Gamma":self.compute_gamma(),
            "Cognitive_disposition":self.cognitive_disposition,
            "Emotional_disposition":self.emotional_disposition,
            "Disposition:":self.disposition}

        
  
        print("--------")
        for k,v in dic.items(): #Affichage du dictionnaire
            print(f'{k} : {v}')
        print("--------\n")
        return dic

        #self.capacity = capacity #Capacité de l'agent
        #self.rs=0 #RS revenu dependant de son action 
        #self.acted=False
        #self.emotional_disposition=emotional_disposition
        #self.cognitive_disposition=self.capacity
        #self.peer_contagion=0


    def set_zone(self): #East or West zone
        if  self.pos[0] >= int(self.model.placement_zone["East"]["min_width"]): # agent.pos = (x,y) si x plus grand que la moitié zone rémunérée
                self.zone=self.model.placement_zone["East"]["zone"] #Zone où R=1
        else :
            self.zone=self.model.placement_zone["West"]["zone"] #Zone où R=0 agent.pos = (x,y) si x plus petit que la moitié zone non  rémunérée
        
        return (self.zone)

              


    #HealthAgent.Move() #
    def move(self):
        new_position=None
        #print(f' Position agent {self.pos}')
        first_choice_steps = []
        first_choice_cells=[]
        likely_steps = self.model.grid.get_neighborhood(
            self.pos, 
            moore=True, #Moore neighborhood
            include_center=False)

        likely_cells=[cell_content for cell_content in self.model.grid.iter_cell_list_contents(likely_steps)]
        
        #Liste des agents de la même zone
        agent_position = [ agent.pos for agent in self.model.schedule.agents if (isinstance(agent,HealthAgent)) ]
        #print(f'Liste de la position des agents  {agent_position}')
        agent_cells=[cell_content for cell_content in self.model.grid.iter_cell_list_contents(agent_position)]
        

        a=set(likely_cells) #Construction d'un set 
        b=set(agent_cells) #Construction d'un set

        l_eligible=list(a.difference(b)) #On evite que les agents se marchent sur les pieds
        #print(f' l_eligible {l_eligible} taille{len(l_eligible)}')
        
        if len(l_eligible)==0:
            print(f'Pas de nouvelle position possible pour {self.pos}')


        else: #si l_eligible > 0
            for cell_content in l_eligible: #iteration le contenu des cellules
                #print(f'cell_content {cell_content.pos}')
                if isinstance(cell_content,PatientPatch): #Deplacement sur une cellule patient malade
                    #First option : move toward ill patient and where remuneration is available
                    if (cell_content.ill==True) and (cell_content.remuneration ==1) :
                        #Cells eligible if ill and severity below threshold
                        if (self.disposition - cell_content.severity - self.model.Threshold >0 ): 

                            #first_choice_steps.append(cell_content.pos)
                            first_choice_cells.append(cell_content)
            #
            #If first_choice list is empty, go anywhere in the cell's vicinity
            if len(first_choice_cells)>0 and new_position is None:
                
                
                if self.model.border_porosity is False:
                    first_choice_cells= [cell for cell in first_choice_cells if cell.zone==self.zone ] #On restreint les cellules de déplacement à la même zone 
                    if len(first_choice_cells)>0: #après la selection on vérifie qu'il reste des cellules éligibles
                        new_position = self.random.choice(first_choice_cells)
                        print(f'new_position _first_choice_no_porosity  {new_position.pos}')
                else:
                    new_position = self.random.choice(first_choice_cells)
                    print(f'new_position _first_choice_porosity  {new_position.pos}')


            elif len(first_choice_cells)==0 or new_position is None:
                if self.model.border_porosity is False:
                    l_eligible= [cell for cell in l_eligible if cell.zone==self.zone ] #On restreint les cellules de déplacement à la même zone 
                    if len(l_eligible) > 0: #après la selection on vérifie qu'il reste des cellules éligibles
                        new_position=self.random.choice(l_eligible)
                        print(f'new_position_no_choice_no_porosity {new_position.pos}')
                else:
                    new_position=self.random.choice(l_eligible)
                    print(f'new_position_no_choice_porosity {new_position.pos}')



            #move
            if new_position is not None:
                self.model.grid.move_agent(self, new_position.pos)
                print(f'Deplacement effectue {new_position.pos}')
            else:
                print(f'Pas de nouvelle position possible')


#HealthAgent.take_action : action si disposition suffisante et PatientPatch.ill==true
    def take_action(self):
        
        for agent in self.model.grid.get_cell_list_contents(self.pos): #look at the content of cell
            if isinstance(agent,PatientPatch):
                
                severity=agent.severity
                patient=agent
                patient_loop=True
                print(f'Patient target : {patient.unique_id} {patient.pos}')
                patient.list_attr()

                #print("severity %s " % (severity)
            if isinstance(agent,HealthAgent):
                disposition=agent.disposition
                ha_loop=True
                print(f'Agent acteur HA : {agent.unique_id} {self.pos}')

                self.list_attr()

            
        action_to_be = disposition - severity - self.model.Threshold
        print(f' Energie Action :   {action_to_be} on pos {agent.pos}')

        if ((disposition - severity) > self.model.Threshold):
            patient.ill=False #HealthAgent took action
            self.acted=True
        else:
            self.acted=False
        print(f'Action prise : {self.acted} on pos {agent.pos}')
        print("\n\n")

    def update_rs(self):
        for agent in self.model.grid.get_cell_list_contents(self.pos): #look at the content of cell
            if isinstance(agent,PatientPatch):
                    patient=agent
            if isinstance(agent,HealthAgent):
                if (self.acted==True): #it's been healed
                    rs_tag=True
                else:
                    rs_tag=False
                    
        if (rs_tag==True):
                #self.rs=patient.remuneration*self.model.k
                self.rs=patient.remuneration #Si patient.zone="W" remuneration=0 sinon Si patient.zone="E" remuneration=1 
        else:
                self.rs=0

#HealthAgent.uptdate_rs()  
#Ok a priori   vérifier que k est défini avant    
    def compute_cognitive_disposition(self):
        if self.acted==True:
                    self.cognitive_disposition=(self.capacity+ self.rs)/2
        else:
            self.cognitive_disposition=self.capacity
        
        self.cognitive_disposition=min(self.cognitive_disposition,1)
        self.cognitive_disposition=max(self.cognitive_disposition,0)


    def compute_envt_impact(self): #Fonction qui calcule l'impact emotionnel de l'environnement sur l'agent à partir de la table table_envt
        l_neighbors = self.model.grid.get_neighbors(self.pos, moore=True,include_center=True)
        sum_ill=0
        for patient  in l_neighbors:
            if isinstance(patient,PatientPatch):
                if patient.ill==True:
                    sum_ill+=1
        self.envt_impact=self.model.table_envt[sum_ill]
        return(sum_ill,self.model.table_envt[sum_ill])



    def compute_emotional_disposition(self):
      

     
        #print("2nde partie motivation : %s " % str((1-self.model.alpha)*(self.disposition - mean_feasabilty)))
        #self.emotional_disposition=(1/2)*self.emotional_disposition + (1/2)* envt_impact # Mauvaise formule car emotional_disposition ne fait que descendre
        self.emotional_disposition=self.emotional_disposition +  self.envt_impact # Mauvaise formule car emotional_disposition ne fait que descendre
        self.emotional_disposition=min(self.emotional_disposition,1)
        self.emotional_disposition=max(self.emotional_disposition,0)

    def compute_peer_contagion(self):
        nb_agent=func.count_agent_by_zone(self.model,self.zone)
        print(f'nb_agent zone {self.zone} : {nb_agent}')
        if nb_agent >= 1:
            self.peer_contagion=(nb_agent -1)*func.average_disposition_by_zone(self.model,self.zone)/nb_agent #On enlève l'impact de l'agent lui-même

    def compute_gamma(self):

        if self.zone=="W":
            gamma=self.model.gamma_negatif # jealousy impact
        elif self.zone=="E":
            gamma=self.model.gamma_positif
        return(gamma)    

    def compute_disposition(self):
        
        #total disposition =  affective + deliberative
        #self.deliberative=(self.rs+self.capacity)/2
        #self.affective=(self.motivation+self.social_envt)/2
        if self.model.peer_contagion is False:
            #ici self.disposition représente la disposition individuelle
            self.disposition=0.5*(self.cognitive_disposition+self.emotional_disposition)
            self.disposition=max(self.disposition,0)
            self.disposition=min(self.disposition,1)
        else:
            gamma=self.compute_gamma()

            #ici self.disposition est la disposition totale = 2/3 disposition individuelle et 1/3 contagion par les pairs (peer influenced disposition)
            self.emotional_disposition=(1+gamma)*(self.emotional_disposition)# perceived inequity

            self.disposition=(1/3)*(self.cognitive_disposition + self.emotional_disposition + self.peer_contagion)
            self.disposition=max(self.disposition,0)
            self.disposition=min(self.disposition,1)

                
        
        '''
        patient_vicinity=get_neigbors_patient_state()

        if l_neighbors_state[i]==0: #0 not solved
            if arr_patient[x,y]>t_feas: #not solvable
                motivation-=0.5/len(l_neighbors)
        if l_neighbors_state[i]==1: #healed, solved
            motivation+=0.5/len(l_neighbors)
        print("Motivation : %f , iter :%d " % (motivation,i))
        i+=1
        '''