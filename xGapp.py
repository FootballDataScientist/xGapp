"""
# My first app
"""

import streamlit as st
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup, Comment
import requests
import seaborn as sns
import os

#functions
def sim_goals_from_individual_xG(xg1, xg2, n_simulations, seed = None):
    '''
    This is a simulation based on individual xG probability and uniform distribution for individual shots
    '''
    if seed != None:
        np.random.seed(seed)
    n1 = len(xg1)
    n2 = len(xg2)    
    
    # Step 1: create random samples:
    rand_chance1 = np.random.rand(n_simulations, n1) # random numbers from uniform distribution between zero and 1 of the shape sim_n x n1
    rand_chance2 = np.random.rand(n_simulations, n2) # random numbers from uniform distribution between zero and 1 of the shape sim_n x n2

    # Step 2: count goals
    goals1 = np.sum(rand_chance1 < xg1, axis = 1)
    goals2 = np.sum(rand_chance2 < xg2, axis = 1)
    return (goals1, goals2)

def sim_goals_from_total_xG(xg_total1, xg_total2, n_simulations, seed = None):
    '''
    This is a simulation based on Poisson distribution
    '''
    if seed != None:
        np.random.seed(seed)
    goals1 = np.random.poisson(xg_total1, n_simulations)
    goals2 = np.random.poisson(xg_total2, n_simulations)
    return (goals1, goals2)


    xpts_h = ( sum(goals_h>goals_a)*3 + sum(goals_h==goals_a)*1 ) / n_simulations
    xpts_a = ( sum(goals_h<goals_a)*3 + sum(goals_h==goals_a)*1 ) / n_simulations

def convert_simulated_goals_to_results(goals: tuple):
    '''
    This function converts simulated goals to:
    - xPTS
    - win probability
    - draws, wins and losses
    - goals mean and standard deviation
    '''
    goals1 = goals[0]
    goals2 = goals[1]
    
    sim_mean_goals1 = goals1.mean()
    sim_mean_goals2 = goals2.mean()
    sim_std_goals1 = goals1.std()
    sim_std_goals2 = goals2.std()
    
    # step3: convert it to draws, wins and expectex points
    draws = (goals1 == goals2)
    win1 = (goals1 > goals2)
    win2 = (goals1 < goals2)
    sim_points1 = np.mean(win1*3+draws*1)
    sim_points2 = np.mean(win2*3+draws*1)
    
    return({"goals1": goals1,
            "goals2": goals2,
            "sim_mean_goals1": sim_mean_goals1,
            "sim_mean_goals2": sim_mean_goals2,
            "sim_std_goals1": sim_std_goals1,
            "sim_std_goals2": sim_std_goals2,
            "draws": draws,
            "win1": win1,
            "win2": win2,
            "draw_pct": draws.mean(),
            "win1_pct": win1.mean(),
            "win2_pct": win2.mean(),
            "sim_points1": sim_points1,
            "sim_points2": sim_points2
           })

# Function 4: collect data from FBREF url
def collect_fbref_shots(url: str):
    if len(url)>0:
        def try_caption(a):
            try:
                return(a.find('caption').get_text())
            except:
                return('None')

        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            tables = soup.find_all('table')
            table_names = [try_caption(tab) for tab in tables]
            pandas_tables = pd.read_html(url)
            shots_table = [pandas_tables[i] for i in range(len(table_names)) if table_names[i] == 'Shots Table'][0]
            shots_table.columns = [f'{x[0]} {x[1]}' if "Unnamed" not in x[0] else x[1] for x in shots_table.columns]
            shots_table = shots_table[~shots_table.Player.isnull()][['Minute', 'Player', 'Squad', 'xG', 'Outcome']]
        except:
            shots_table = 'There is no shots available in this link'
    return(shots_table)

    st.write('You want to analyze ', url, ' game')

    st.write(shots_table)
# function 5: extract teams and xg lists
def take_xG_from_df(df):
    team1 = df.Squad[0]
    xG1 = list(df[df.Squad == team1].xG)
    team2 = df[df.Squad != team1].Squad.unique()[0]
    xG2 = list(df[df.Squad == team2].xG)
    
    return({'team1': team1,
            'xG1': xG1,
            'team2': team2,
            'xG2': xG2
            })

#function 6: random shots xG
def random_shots(xg_total, N_shots):
  shots = list(np.maximum(
      np.round(np.diff( np.concatenate( (np.array([0]),
                  np.sort(np.random.uniform(0.01, xg_total, N_shots-1))
                                          )
                                        )
                        ),2), [0.01]
                    )
  )
  shots.append(round(xg_total-np.sum(shots),2))
  return(shots)

##################################################################################
with st.sidebar:
    try:
        st.image("/mount/src/xgapp/Logo2.PNG")
    except:
        st.image("./Logo2.PNG")
    finally:
        pass
        
    st.markdown("_Instrukcje_: Co mogę tu zrobić?")
    st.markdown("Jesteś w aplikacji, która umożliwia testowanie, analizę i zrozumienie w jaki sposób różnego rodzaju sytuacje bramkowe przekładają się na oczekiwane punkty (xPTS), prawdopodobieństwo zwycięstwa, a także prawdopodobieństwo konkretnych wyników.")
    mode = st.radio(
    "Co chcesz zrobić?",
    ["***Potestować wymyślone xG indywidualnych strzałów***", "***Sprawdzić konkretny mecz***"],
    captions = ("Możesz podać konkretne wartości xG lub wylosować je, możesz też podać wartość sumaryczną z całego meczu, a otrzymasz (mniej precyzyjne) wyniki z uproszcoznego modelu", 
                "Znajdź link konkretnego meczu na stronie [fbref.com](fbref.com) i przeanalizuj rzeczywiste xG pojedynczych strzałów.")
    )
    st.divider()
    st.header("autor: O Futbolu Statystycznie")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("[facebook](https://www.facebook.com/ofutbolustatystycznie/)")
        try:
            st.image("/mount/src/xgapp/Facebook_Logo_Primary.png")
        except:
            st.image("./Facebook_Logo_Primary.png")

    with col2:
        st.subheader("[X/Twitter](https://twitter.com/OFutboluStat)")
        try:
            st.image("/mount/src/xgapp/X-logo-black.png")
        except:
            st.image("./X-logo-black.png")


# koniec sidebara
    

# główna część
st.title("Aplikacja do analizy xG i xPTS")
st.header(":grey[WERSJA BETA]")

if 'generated_shots_team1' not in st.session_state:
    st.session_state['generated_shots_team1'] = None

if 'generated_shots_team2' not in st.session_state:
    st.session_state['generated_shots_team2'] = None

if mode == "***Potestować wymyślone xG indywidualnych strzałów***":
    option = st.selectbox(
            'W jaki sposób chcesz wprowadzić xG dla obu drużyn?',
            ( 'Wylosować', 'Lista wartości xG oddzielonych spacjami', 'Sumaryczne xG z meczu'))
    
    if option == 'Wylosować':
        xg_generator_button = st.button('Wygeneruj xG', help = "Po naciśnięciu wygenerowane zostanie xG według poniższej specyfikacji", key = 'Wygeneruj')

    mode1_col1, mode1_col2 = st.columns(2)
    with mode1_col1:
        team1 = st.text_input("Możesz podać nazwę pierwszej drużyny, żeby łatwiej się analizowało",
                        'Drużyna 1')
        
        #Tworzę UI
        if option == 'Wylosować':
            if len(team1)>0:
                team1_str = f' - **{team1}**'
            else:
                team1_str = '.'
            xg_total1 = st.number_input(f'Podaj sumaryczne xG z całego meczu dla pierwszej z drużyn{team1_str}',
                            min_value = 0.0, max_value = 10.0, value = 1.35, step = 0.01,
                            key = "xgtotal1_los"
                            )
            N_shots1 = st.number_input(f'Ile chcesz strzałów?',
                            min_value = 0, max_value = int(xg_total1*100), value = 10, step = 1,
                            key = "nshots1"
                            )
            metod1 = st.selectbox(
                'Czy chcesz wylosować xG czy podzielić po równo na wybraną liczbę strzałów?',
            ( 'Wylosować', 'Podzielić równo'), key='metod1')
            if xg_generator_button:
                if metod1 == 'Wylosować':
                    shots_team1 = random_shots(xg_total1, N_shots1)
                elif metod1 == 'Podzielić równo':
                    shots_team1 = [round(xg,3) for xg in [xg_total1/N_shots1]*N_shots1]

                st.session_state['generated_shots_team1'] = shots_team1
            if st.session_state['generated_shots_team1']:    
                st.text("Otrzymane xG")
                st.markdown(" ".join([str(xg) for xg in st.session_state['generated_shots_team1']]))
        elif option == 'Lista wartości xG oddzielonych spacjami':
            shots_team1_txt = st.text_input("""Wpisz xG poszczególnych strzałów oddzielając je spacją.""",
                        '0,01 0,12 0,17 0,37 0,02 0,11 0,34', key = 'xGlist1')
            shots_team1 = [float(xG.replace(',', '.')) for xG in shots_team1_txt.split(' ')]
            xg_total1 = np.round(np.sum(shots_team1),3)
        elif option == 'Sumaryczne xG z meczu':
            if len(team1)>0:
                team1_str = f' - **{team1}**'
            else:
                team1_str = '.'
            xg_total1 = st.number_input(f'Podaj sumaryczne xG z całego meczu dla pierwszej z drużyn{team1_str}',
                            min_value = 0.0, max_value = 10.0, value = 1.35, step = 0.01,
                            key = "xgtotal1"
                            )

    with mode1_col2:
        team2 = st.text_input("Możesz podać nazwę drugiej drużyny, żeby łatwiej się analizowało",
                        'Drużyna 2')
        #Tworzę UI
        if option == 'Wylosować':
            if len(team2)>0:
                team2_str = f' - **{team2}**'
            else:
                team2_str = '.'
            xg_total2 = st.number_input(f'Podaj sumaryczne xG z całego meczu dla drugiej z drużyn{team2_str}',
                            min_value = 0.0, max_value = 10.0, value = 1.07, step = 0.01,
                            key = "xgtotal2_los"
                            )
            N_shots2 = st.number_input(f'Ile chcesz strzałów?',
                            min_value = 0, max_value = int(xg_total2*100), value = 10, step = 1,
                            key = "nshots2"
                            )
            metod2 = st.selectbox(
                'Czy chcesz wylosować xG czy podzielić po równo na wybraną liczbę strzałów?',
            ( 'Wylosować', 'Podzielić równo'), key='metod2')
            if xg_generator_button:
                if metod2 == 'Wylosować':
                    shots_team2 = random_shots(xg_total2, N_shots2)
                elif metod2 == 'Podzielić równo':
                    shots_team2 = [round(xg,3) for xg in [xg_total2/N_shots2]*N_shots2]
                st.session_state['generated_shots_team2'] = shots_team2
            if st.session_state['generated_shots_team2']: 
                st.text("Otrzymane xG")
                st.markdown(" ".join([str(xg) for xg in st.session_state['generated_shots_team2']]))
        elif option == 'Lista wartości xG oddzielonych spacjami':
            shots_team2_txt = st.text_input("""Wpisz xG poszczególnych strzałów oddzielając je spacją.""",
                        '0,03 0,76 0,15 0,25 0,03 0,02 0,11 0,34', key = 'xGlist2')
            shots_team2 = [float(xG.replace(',', '.')) for xG in shots_team2_txt.split(' ')]
            xg_total2 = np.round(np.sum(shots_team2),3)

        elif option == 'Sumaryczne xG z meczu':
            if len(team2)>0:
                team2_str = f' - **{team2}**'
            else:
                team2_str = '.'
            xg_total2 = st.number_input(f'Podaj sumaryczne xG z całego meczu dla drugiej z drużyn{team2_str}',
                            min_value = 0.0, max_value = 10.0, value = 1.07, step = 0.01,
                            key = "xgtotal2"
                           )
    st.divider()       


elif mode == "***Sprawdzić konkretny mecz***":
    
    # UI
    url = st.text_input("""Podaj link do meczu ze strony FBREF.com z ligi angielskiej, włoskiej, hiszpańskiej, niemieckiej, francuskiej, portugalskiej lub holenderskiej""",
                        'Wklej link tutaj')
            
#execution
    if 'fbref' in url:
        try:
            option = 'fbref'
            data_load_state = st.text('Pobieranie danych...') #UI
            fbref_data = collect_fbref_shots(url)
            st_Write("shots collected")

            xg_dict = take_xG_from_df(fbref_data)

            team1 = xg_dict['team1']
            shots_team1 = xg_dict['xG1']
            xg_total1 = np.round(np.sum(shots_team1),3)

            team2 = xg_dict['team2']
            shots_team2 = xg_dict['xG2']
            xg_total2 = np.round(np.sum(shots_team2),3)
            
            #UI
            data_load_state.text('Pobieranie danych... zakończone')
            header = f"Poniżej historia strzałów z tego meczu, za fbref.com"
            st.write(header)
            #edit_button = st.checkbox('Modyfikuj dane', value = False, help = "Po włączeniu tej opcji, dane mogą być zmieniane. Wyłączenie powraca do oryginalnych danych z meczu")
            #if edit_button:
            #    st.data_editor(fbref_data, num_rows = "dynamic")
            #else:
            #    st.dataframe(fbref_data)
            st.dataframe(fbref_data)

        
        except:
            pass
    else:
        pass
    st.divider()
# właściwa symulacja:
N_simulations = st.number_input('Liczba powtórzeń w symulacji', min_value=1000, max_value=1000000, value=100000, key ="nsim")

sim_button = st.button('Zrób symulację', help = "Po naciśnięciu zrobiona zostanie symulacja oczekiwanych punktów i wyników")
if sim_button:
    if option == 'Wylosować':
        simulation_state = st.text('Symulacja...')
        goals_ind = sim_goals_from_individual_xG(xg1 = st.session_state['generated_shots_team1'], xg2 = st.session_state['generated_shots_team2'], 
                                                n_simulations = N_simulations)
        simulation = convert_simulated_goals_to_results(goals_ind)
        simulation_state.text(f'Symulacja... zakończona - {N_simulations} powtórzeń')
    elif option in ['Lista wartości xG oddzielonych spacjami', 'fbref']:
        simulation_state = st.text('Symulacja...')
        goals_ind = sim_goals_from_individual_xG(xg1 = shots_team1, xg2 = shots_team2, 
                                                    n_simulations = N_simulations)
        simulation = convert_simulated_goals_to_results(goals_ind)
        simulation_state.text(f'Symulacja... zakończona - {N_simulations} powtórzeń')
            
    elif option == 'Sumaryczne xG z meczu':
    
        simulation_state = st.text('Symulacja...')
        goals_total = sim_goals_from_total_xG(xg_total1 = xg_total1, xg_total2 = xg_total2, 
                                              n_simulations = N_simulations)
        simulation = convert_simulated_goals_to_results(goals_total)
        simulation_state.text(f'Symulacja... zakończona - {N_simulations} powtórzeń')
            
    df = pd.DataFrame({team1:simulation['goals1'],
                    team2:simulation['goals2']
                    })
            
    tab1, tab2 = st.tabs(["Wyniki symulacji", "Prawdopodobieństwa poszczególnych wyników"])

    with tab1:
        try:
            # Dodaję komentarz
            if option == 'Wylosować':
                pass
            elif option == 'fbref':
                pass
            elif option == 'Lista wartości xG oddzielonych spacjami':
                pass
            elif option == 'Sumaryczne xG z meczu':
                st.markdown('**UWAGA!**: :red[Symulacje oczekiwanych punktów i prawdopodobieństw wyników na podstawie sumarycznego xG nie są tak poprawne i dokładne jak na podstawie indywidualnych strzałów.]')
        except:
            pass        
        option1_col1, option1_col2, option1_col3 = st.columns(3) 
        with option1_col1:
            st.markdown("Drużyna:")
            st.markdown("Oczekiwane punkty (xPTS):")
            st.markdown("Prawdopodobieństwo wygranej:")
            st.markdown("Prawdopodobieństwo remisu:")
            st.markdown("Prawdopodobieństwo porażki:")
            st.markdown("Suma xG:")
            st.markdown("Średnia bramek:")
            st.markdown("Odchylenie standardowe liczby bramek:")
        with option1_col2:
            st.markdown(f'{team1}')
            st.markdown(f'{round(simulation["sim_points1"],2)}')
            st.markdown(f'{round(simulation["win1_pct"]*100,2)}%')
            st.markdown(f'{round(simulation["draw_pct"]*100,2)}%')
            st.markdown(f'{round(simulation["win2_pct"]*100,2)}%')
            st.markdown(f'{round(xg_total1,2)}')
            st.markdown(f'{round(simulation["sim_mean_goals1"],2)}')
            st.markdown(f'{round(simulation["sim_std_goals1"],3)}')
        with option1_col3:
            st.markdown(f'{team2}')
            st.markdown(f'{round(simulation["sim_points2"],2)}')
            st.markdown(f'{round(simulation["win2_pct"]*100,2)}%')
            st.markdown(f'{round(simulation["draw_pct"]*100,2)}%')
            st.markdown(f'{round(simulation["win1_pct"]*100,2)}%')
            st.markdown(f'{round(xg_total2,2)}')
            st.markdown(f'{round(simulation["sim_mean_goals2"],2)}')
            st.markdown(f'{round(simulation["sim_std_goals2"],3)}')
    with tab2:
                
        # create better heatmaps: https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
        from matplotlib import pyplot as plt
        plot = sns.heatmap(pd.crosstab(df[team1], df[team2])/N_simulations, 
                                annot = True,
                                fmt = ".2%",
                                cmap = 'viridis', 
                                robust = True)
        plt.title('Prawdopodobieństwa poszczególnych wyników')
        plt.ylabel(f'{team1} - gole')
        plt.xlabel(f'{team2} - gole')
        Ymax = np.max(df[team1])
        plt.ylim(0,Ymax)
        st.pyplot(plot.get_figure())