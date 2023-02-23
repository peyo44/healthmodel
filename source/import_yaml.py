import yaml
from yaml import error
import numpy as np
import re
import copy



fichier_conf = 'C:/Users/PROVOST/OneDrive Entreprise/mesa/healthmodel/HAbatch_conf.yml'

def open_yaml_file(fichier):
    try:
        yaml_file = open(fichier)
        dic_yaml = yaml.load(yaml_file, Loader=yaml.FullLoader)
    except error as Exception:
        print(f'Erreur : {Exception}')
        return (-1)
    
    return(dic_yaml)


def process_base_variable(dic_yam_var,base_var_tag='BaseVar',list_tag=["start","stop","step"]):
    dict_copy=dic_yam_var.copy() #attention dic_yam_var est un pointeur 
    for key, value in dict_copy[base_var_tag].items():
        if type(value)==dict:
          for cle  in  list_tag:
            #print(f'cle {cle}')  
            if not cle in value.keys():
                print(f'Erreur Fichier yaml : probleme syntaxe {base_var_tag} {key}')
                return(-1)
            else:
                dict_copy[base_var_tag][key]=[round(x,2)  for x in np.arange(value["start"],
                value["stop"]+value["step"], #le value["step"] permet d'inclure la limite du stop
                value["step"])]
    
    return(dict_copy)

"""
def process_linked_variable(dic_yam_var,base_var_tag='BaseVar',linked_var_tag='LinkedVar'):
    dict_copy=dic_yam_var.copy() #attention dic_yam_var est un pointeur
    l_base_var_link=[]
    for key, value in dict_copy[base_var_tag].items():
        if type(value)==list:
            l_base_var_link.append(key) #on stocke le nom des listes
    
    print(f'list l_base_var_link {l_base_var_link}')
            
    for key, value in dict_copy[linked_var_tag].items():

        for nom_variable in l_base_var_link:
            print (f'recherche nom var {nom_variable}  dans {value}')

            var_chaine=re.match(r'nom_variable',value)
            if var_chaine is not None:
                    operateur=re.match(r"+|-|/|*",value)
                    if operateur is not None:
                        print("Pas opérateur trouvé")
                        nombre=re.findall(r"[0-9.]+",value)
                        if nombre is not None:
                            print("Pas de nombre trouvé")

                            print(var_chaine, operateur , nombre)    

    return()
            #On trouve l'opérateur

            # On trouve la valeur numérique
"""
def build_parameters_set(dict_param,batch_size_max=50,base_var_tag='BaseVar'):
    dict_param_cp=dict_param.copy()
    len_list_limit=batch_size_max

    #Calcul de la longeur max de liste

    for key, val in dict_param_cp[base_var_tag].items():
        if type(val)==list:
            #print(f'key est une liste {key}')
            len_list=len(val)
            if len_list<=len_list_limit:
                len_list_limit=len_list
                #dict_param_cp[base_var_tag][key]=val[:len_list_limit]
    #print(f' len_list_limit : {len_list_limit}')
    #Egalise la taille de toutes les listes

    for key, val in dict_param_cp[base_var_tag].items():
        if type(val)==list:
            
            dict_param_cp[base_var_tag][key]=val[:len_list_limit]


    return(dict_param_cp,len_list_limit)


def f_dic_round(dict_param,round_n,base_var_tag='BaseVar'):

    dict_param_cp=copy.deepcopy(dict_param)
    for key, val in dict_param_cp[base_var_tag].items():
        if type(val)==list:
            
            if len(val)>round_n:
                dict_param_cp[base_var_tag][key]=val[round_n]
                print(f'{key} {val[round_n]}')
            else:
                print('Erreur round_n {round_n} supérieur à {len(val)} ')
    
    return(dict_param_cp)


def f_dic_batch(fichier_conf,batch_size_limit=50,chemin_fic_res='results',suffixe_fic_res="results"):
    l_resultats=[]

    dic_var=open_yaml_file(fichier_conf)
    #print(f'dic_var {dic_var}')
    dic_base_var=process_base_variable(dic_yam_var=dic_var)
    #print(f'base_var {dic_base_var}')
    #dic_linked_var=process_linked_variable(dic_yam_var=dic_var)

    dic_param,len_max=build_parameters_set(dic_base_var,batch_size_max=batch_size_limit)
    #print(f'dic_param {dic_param}')

    for lap in range(len_max):
    #dic_param_cp=dic_param.copy()
    #print(f'tour {lap}')
        dic_res={}
        dic_res['var']=f_dic_round(dict_param=dic_param,round_n=lap)
        dic_res['fichier']=chemin_fic_res+'/'+suffixe_fic_res+'_'+str(lap)+'.csv'
        l_resultats.append(dic_res)
    
    return(l_resultats)


