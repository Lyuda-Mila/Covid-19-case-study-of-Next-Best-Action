from flask import Flask, request, render_template, session, redirect, g, flash, url_for, make_response
import pandas as pd
import numpy as np

app = Flask(__name__)

parameters_names = {
            'C1 School closing': 4,
            'C2 Workplace closing': 4,
            'C3 Cancel public events': 3,
            'C4 Restrictions on gatherings': 5,
            'C5 Close public transport': 3,
            'C6 Stay at home requirements': 4,
            'C7 Restrictions on internal movement': 3,
            'C8 International travel controls': 5,
            'H1 Public information campaigns': 3
    }

action_rules_cases = pd.read_excel('static/docs/action_rules_cases.xlsx')
action_rules_deaths = pd.read_excel('static/docs/action_rules_deaths.xlsx')
qtable_cases = pd.read_excel('static/docs/qtable_cases.xlsx', converters={'Unnamed: 0':str})
qtable_cases.index = qtable_cases['Unnamed: 0']
qtable_cases = qtable_cases.drop(columns = ['Unnamed: 0'],axis = 1)
qtable_cases = qtable_cases.replace(0.0, np.nan)
qtable_cases = qtable_cases.dropna(axis=0,how='all')
qtable_deaths = pd.read_excel('static/docs/qtable_deaths.xlsx', converters={'Unnamed: 0':str})
qtable_deaths.index = qtable_deaths['Unnamed: 0']
qtable_deaths = qtable_deaths.drop(columns = ['Unnamed: 0'],axis = 1)
qtable_deaths = qtable_deaths.replace(0.0, np.nan)
qtable_deaths = qtable_deaths.dropna(axis=0,how='all')

@app.route('/get_result',methods=['POST'])
def get_result():

    all_input = list(map(str,request.form.values()))
    c1, c2, c3, c4, c5, c6, c7, c8, h1 = [int(x.split('=')[1]) for x in all_input if
                                          str(x) not in ['cases', 'rl', 'action_rules', 'deaths']]
    print(all_input)
    if 'action_rules' in all_input and 'cases' in all_input:
        return get_best_rule_cases(c1, c2, c3, c4, c5, c6, c7, c8, h1)
    elif 'action_rules' in all_input and 'deaths' in all_input:
        return get_best_rule_deaths(c1, c2, c3, c4, c5, c6, c7, c8, h1)
    elif 'rl' in all_input and 'cases' in all_input:
        return get_best_action_rl_cases(c1, c2, c3, c4, c5, c6, c7, c8, h1)
    elif 'rl' in all_input and 'deaths' in all_input:
        return get_best_action_rl_deaths(c1, c2, c3, c4, c5, c6, c7, c8, h1)
    else:
        return input()


def get_best_rule_cases(c1,c2,c3,c4,c5,c6,c7,c8,h1):
    c1_init = action_rules_cases['c1_init']
    c2_init = action_rules_cases['c2_init']
    c3_init = action_rules_cases['c3_init']
    c4_init = action_rules_cases['c4_init']
    c5_init = action_rules_cases['c5_init']
    c6_init = action_rules_cases['c6_init']
    c7_init = action_rules_cases['c7_init']
    c8_init = action_rules_cases['c8_init']
    h1_init = action_rules_cases['h1_init']
    difference = []
    for i in range(action_rules_cases.shape[0]):
        d = 0
        if c1_init[i] != -1:
            d = d + abs(c1_init[i] - c1)
        else:
            d = d + 1
        if c2_init[i] != -1:
            d = d + abs(c2_init[i] - c2)
        else:
            d = d + 1
        if c3_init[i] != -1:
            d = d + abs(c3_init[i] - c3)
        else:
            d = d + 1
        if c4_init[i] != -1:
            d = d + abs(c4_init[i] - c4)
        else:
            d = d + 1
        if c5_init[i] != -1:
            d = d + abs(c5_init[i] - c5)
        else:
            d = d + 1
        if c6_init[i] != -1:
            d = d + abs(c6_init[i] - c6)
        else:
            d = d + 1
        if c7_init[i] != -1:
            d = d + abs(c7_init[i] - c7)
        else:
            d = d + 1
        if c8_init[i] != -1:
            d = d + abs(c8_init[i] - c8)
        else:
            d = d + 1
        if h1_init[i] != -1:
            d = d + abs(h1_init[i] - h1)
        else:
            d = d + 1
        difference.append(d)
    min_d = min(difference)
    action_rules_cases_mindiff = action_rules_cases[difference == min_d].sort_values(by='confidence',
                                                                                     ascending=False)
    max_conf = action_rules_cases_mindiff['confidence'].max()
    best_rule = action_rules_cases_mindiff[action_rules_cases_mindiff['confidence'] == max_conf]
    closest_state_list = [best_rule.replace(-1, 'empty')['c1_init'].values[0], \
               best_rule.replace(-1, 'empty')['c2_init'].values[0], \
               best_rule.replace(-1, 'empty')['c3_init'].values[0], \
               best_rule.replace(-1, 'empty')['c4_init'].values[0], \
               best_rule.replace(-1, 'empty')['c5_init'].values[0], \
               best_rule.replace(-1, 'empty')['c6_init'].values[0], \
               best_rule.replace(-1, 'empty')['c7_init'].values[0], \
               best_rule.replace(-1, 'empty')['c8_init'].values[0], \
               best_rule.replace(-1, 'empty')['h1_init'].values[0]]
    res = []
    res.append(closest_state_list)
    best_rule_list = []
    if best_rule['c1_next'].values[0] == -1 :
        res_el = best_rule.replace(-1, 'empty')['c1_init'].values[0]
    else:
        res_el = str(best_rule['c1_init'].values[0]) + ' -> ' + str(best_rule['c1_next'].values[0])
    best_rule_list.append(res_el)
    if  best_rule['c2_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c2_init'].values[0]
    else:
        res_el = str(best_rule['c2_init'].values[0]) + ' -> ' + str(best_rule['c2_next'].values[0])
    best_rule_list.append(res_el)
    if  best_rule['c3_next'].values[0]== -1:
        res_el = best_rule.replace(-1, 'empty')['c3_init'].values[0]
    else:
        res_el = str(best_rule['c3_init'].values[0]) + ' -> ' + str(best_rule['c3_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c4_next'].values[0]== -1:
        res_el = best_rule.replace(-1, 'empty')['c4_init'].values[0]
    else:
        res_el = str(best_rule['c4_init'].values[0]) + ' -> ' + str(best_rule['c4_next'].values[0])
    best_rule_list.append(res_el)
    if  best_rule['c5_next'].values[0]== -1:
        res_el = best_rule.replace(-1, 'empty')['c5_init'].values[0]
    else:
        res_el = str(best_rule['c5_init'].values[0]) + ' -> ' + str(best_rule['c5_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c6_next'].values[0]== -1:
        res_el = best_rule.replace(-1, 'empty')['c6_init'].values[0]
    else:
        res_el = str(best_rule['c6_init'].values[0]) + ' -> ' + str(best_rule['c6_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c7_next'].values[0] == -1 :
        res_el = best_rule.replace(-1, 'empty')['c7_init'].values[0]
    else:
        res_el = str(best_rule['c7_init'].values[0]) + ' -> ' + str(best_rule['c7_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c8_next'].values[0]== -1:
        res_el = best_rule.replace(-1, 'empty')['c8_init'].values[0]
    else:
        res_el = str(best_rule['c8_init'].values[0]) + ' -> ' + str(best_rule['c8_next'].values[0])
    best_rule_list.append(res_el)
    if  best_rule['h1_next'].values[0]== -1:
        res_el = best_rule.replace(-1, 'empty')['h1_init'].values[0]
    else:
        res_el = str(best_rule['h1_init'].values[0]) + ' -> ' + str(best_rule['h1_next'].values[0])
    best_rule_list.append(res_el)
    res.append(best_rule_list)
    res.append('W'+ best_rule['pretty_rule'].values[0][ best_rule['pretty_rule'].values[0].find('with support')+1:-1])
    return render_template('input_var.html',\
                           best_rule_res=res,\
                           input = ([int(x.split('=')[1]) for x in list(map(str,request.form.values())) if
                                          str(x) not in ['cases', 'rl', 'action_rules', 'deaths']]),\
                           parameters_names=parameters_names,\
                           show_res=1)


#find the best rule to decrease deaths

def get_best_rule_deaths(c1,c2,c3,c4,c5,c6,c7,c8,h1):
    c1_init = action_rules_deaths['c1_init']
    c2_init = action_rules_deaths['c2_init']
    c3_init = action_rules_deaths['c3_init']
    c4_init = action_rules_deaths['c4_init']
    c5_init = action_rules_deaths['c5_init']
    c6_init = action_rules_deaths['c6_init']
    c7_init = action_rules_deaths['c7_init']
    c8_init = action_rules_deaths['c8_init']
    h1_init = action_rules_deaths['h1_init']
    difference = []
    for i in range(action_rules_deaths.shape[0]):
        d = 0
        if c1_init[i] != -1:
            d = d + abs(c1_init[i] - c1)
        else:
            d = d + 1
        if c2_init[i] != -1:
            d = d + abs(c2_init[i] - c2)
        else:
            d = d + 1
        if c3_init[i] != -1:
            d = d + abs(c3_init[i] - c3)
        else:
            d = d + 1
        if c4_init[i] != -1:
            d = d + abs(c4_init[i] - c4)
        else:
            d = d + 1
        if c5_init[i] != -1:
            d = d + abs(c5_init[i] - c5)
        else:
            d = d + 1
        if c6_init[i] != -1:
            d = d + abs(c6_init[i] - c6)
        else:
            d = d + 1
        if c7_init[i] != -1:
            d = d + abs(c7_init[i] - c7)
        else:
            d = d + 1
        if c8_init[i] != -1:
            d = d + abs(c8_init[i] - c8)
        else:
            d = d + 1
        if h1_init[i] != -1:
            d = d + abs(h1_init[i] - h1)
        else:
            d = d + 1
        difference.append(d)
    min_d = min(difference)
    action_rules_deaths_mindiff = action_rules_deaths[difference == min_d].sort_values(by='confidence',
                                                                                       ascending=False)
    max_conf = action_rules_deaths_mindiff['confidence'].max()
    best_rule = action_rules_deaths_mindiff[action_rules_deaths_mindiff['confidence'] == max_conf]
    closest_state_list = [best_rule.replace(-1, 'empty')['c1_init'].values[0], \
                         best_rule.replace(-1, 'empty')['c2_init'].values[0], \
                         best_rule.replace(-1, 'empty')['c3_init'].values[0], \
                         best_rule.replace(-1, 'empty')['c4_init'].values[0], \
                         best_rule.replace(-1, 'empty')['c5_init'].values[0], \
                         best_rule.replace(-1, 'empty')['c6_init'].values[0], \
                         best_rule.replace(-1, 'empty')['c7_init'].values[0], \
                         best_rule.replace(-1, 'empty')['c8_init'].values[0], \
                         best_rule.replace(-1, 'empty')['h1_init'].values[0]]
    res = []
    res.append(closest_state_list)
    best_rule_list = []
    if best_rule['c1_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c1_init'].values[0]
    else:
        res_el = str(best_rule['c1_init'].values[0]) + ' -> ' + str(best_rule['c1_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c2_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c2_init'].values[0]
    else:
        res_el = str(best_rule['c2_init'].values[0]) + ' -> ' + str(best_rule['c2_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c3_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c3_init'].values[0]
    else:
        res_el = str(best_rule['c3_init'].values[0]) + ' -> ' + str(best_rule['c3_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c4_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c4_init'].values[0]
    else:
        res_el = str(best_rule['c4_init'].values[0]) + ' -> ' + str(best_rule['c4_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c5_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c5_init'].values[0]
    else:
        res_el = str(best_rule['c5_init'].values[0]) + ' -> ' + str(best_rule['c5_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c6_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c6_init'].values[0]
    else:
        res_el = str(best_rule['c6_init'].values[0]) + ' -> ' + str(best_rule['c6_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c7_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c7_init'].values[0]
    else:
        res_el = str(best_rule['c7_init'].values[0]) + ' -> ' + str(best_rule['c7_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['c8_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['c8_init'].values[0]
    else:
        res_el = str(best_rule['c8_init'].values[0]) + ' -> ' + str(best_rule['c8_next'].values[0])
    best_rule_list.append(res_el)
    if best_rule['h1_next'].values[0] == -1:
        res_el = best_rule.replace(-1, 'empty')['h1_init'].values[0]
    else:
        res_el = str(best_rule['h1_init'].values[0]) + ' -> ' + str(best_rule['h1_next'].values[0])
    best_rule_list.append(res_el)
    res.append(best_rule_list)
    res.append('W' + best_rule['pretty_rule'].values[0][best_rule['pretty_rule'].values[0].find('with support') + 1:-1])
    return render_template('input_var.html', \
                           best_rule_res=res, \
                           input=([int(x.split('=')[1]) for x in list(map(str,request.form.values())) if
                                          str(x) not in ['cases', 'rl', 'action_rules', 'deaths']]), \
                           parameters_names=parameters_names,\
                           show_res=1)


def get_best_action_rl_cases(с1,c2,c3,c4,c5,c6,c7,c8,h1):
    st = str(с1) + str(c2) + str(c3) + str(c4) + str(c5) + str(c6) + str(c7) + str(c8) + str(h1)
    difference = []
    if st in qtable_cases.index:
        max_reward = qtable_cases.loc[st, :].max()
        next_action = qtable_cases.loc[st, :][qtable_cases.loc[st, :] == max_reward].index.values[0]
        next_action_list = []
        closest_state = st
        for i in range(0, 9):
            if closest_state[i] == next_action[i]:
                res_el = next_action[i]
            else:
                res_el = str(closest_state[i]) + ' -> ' + str(next_action[i])
            next_action_list.append(res_el)
        res = []
        closest_state_list = [с1,c2,c3,c4,c5,c6,c7,c8,h1]
        res.append(closest_state_list)
        res.append(next_action_list)
        res.append('With expected reward = {}'.format(max_reward))
    else:
        for i in range(len(qtable_cases.index)):
            d = 0
            d = d + abs(int(qtable_cases.index[i][0]) - с1)
            d = d + abs(int(qtable_cases.index[i][1]) - c2)
            d = d + abs(int(qtable_cases.index[i][2]) - c3)
            d = d + abs(int(qtable_cases.index[i][3]) - c4)
            d = d + abs(int(qtable_cases.index[i][4]) - c5)
            d = d + abs(int(qtable_cases.index[i][5]) - c6)
            d = d + abs(int(qtable_cases.index[i][6]) - c7)
            d = d + abs(int(qtable_cases.index[i][7]) - c8)
            d = d + abs(int(qtable_cases.index[i][8]) - h1)
            difference.append(d)
        min_d = min(difference)
        cond = pd.DataFrame(difference)[0] == min_d
        cond.index = qtable_cases.index
        qtable_cases_mindiff = qtable_cases[cond]
        max_reward = qtable_cases_mindiff.max().max()
        next_action = qtable_cases_mindiff.max()[qtable_cases_mindiff.max() == max_reward].index[0]
        closest_state = \
        qtable_cases_mindiff.loc[:, next_action][qtable_cases_mindiff.loc[:, next_action] == max_reward].index[0]
        next_action_list = []
        for i in range(0,9):
            if closest_state[i]==next_action[i]:
                res_el = next_action[i]
            else:
                res_el = str(closest_state[i]) + ' -> ' + str(next_action[i])
            next_action_list.append(res_el)
        closest_state_list = [closest_state[0], closest_state[1], closest_state[2], closest_state[3], closest_state[4],closest_state[5], closest_state[6], closest_state[7], closest_state[8]]
        res = []
        res.append(closest_state_list)
        res.append(next_action_list)
        res.append('With expected reward = {}'.format(max_reward))
    return render_template('input_var.html',\
                           best_rule_res=res,\
                           input=([int(x.split('=')[1]) for x in list(map(str,request.form.values())) if
                                          str(x) not in ['cases', 'rl', 'action_rules', 'deaths']]), \
                           parameters_names=parameters_names,\
                           show_res=1)


def get_best_action_rl_deaths(c1,c2,c3,c4,c5,c6,c7,c8,h1):
    st = str(c1) + str(c2) + str(c3) + str(c4) + str(c5) + str(c6) + str(c7) + str(c8) + str(h1)
    difference = []
    if st in qtable_deaths.index:
        max_reward = qtable_deaths.loc[st, :].max()
        next_action = qtable_deaths.loc[st, :][qtable_deaths.loc[st, :] == max_reward].index.values[0]
        next_action_list = []
        closest_state = st
        for i in range(0, 9):
            if closest_state[i] == next_action[i]:
                res_el = next_action[i]
            else:
                res_el = str(closest_state[i]) + ' -> ' + str(next_action[i])
            next_action_list.append(res_el)
        res = []
        closest_state_list = [c1, c2, c3, c4, c5, c6, c7, c8, h1]
        res.append(closest_state_list)
        res.append(next_action_list)
        res.append('With expected reward = {}'.format(max_reward))
    else:
        for i in range(len(qtable_deaths.index)):
            d = 0
            d = d + abs(int(qtable_deaths.index[i][0]) - c1)
            d = d + abs(int(qtable_deaths.index[i][1]) - c2)
            d = d + abs(int(qtable_deaths.index[i][2]) - c3)
            d = d + abs(int(qtable_deaths.index[i][3]) - c4)
            d = d + abs(int(qtable_deaths.index[i][4]) - c5)
            d = d + abs(int(qtable_deaths.index[i][5]) - c6)
            d = d + abs(int(qtable_deaths.index[i][6]) - c7)
            d = d + abs(int(qtable_deaths.index[i][7]) - c8)
            d = d + abs(int(qtable_deaths.index[i][8]) - h1)
            difference.append(d)
        min_d = min(difference)
        cond = pd.DataFrame(difference)[0] == min_d
        cond.index = qtable_deaths.index
        qtable_deaths_mindiff = qtable_deaths[cond]
        max_reward = qtable_deaths_mindiff.max().max()
        next_action = qtable_deaths_mindiff.max()[qtable_deaths_mindiff.max() == max_reward].index[0]
        closest_state = \
        qtable_deaths_mindiff.loc[:, next_action][qtable_deaths_mindiff.loc[:, next_action] == max_reward].index[0]
        next_action_list = []
        for i in range(0, 9):
            if closest_state[i] == next_action[i]:
                res_el = next_action[i]
            else:
                res_el = str(closest_state[i]) + ' -> ' + str(next_action[i])
            next_action_list.append(res_el)
        closest_state_list = [closest_state[0], closest_state[1], closest_state[2], closest_state[3], closest_state[4],
                              closest_state[5], closest_state[6], closest_state[7], closest_state[8]]
        res = []
        res.append(closest_state_list)
        res.append(next_action_list)
        res.append('With expected reward = {}'.format(max_reward))
    return render_template('input_var.html', \
                           best_rule_res=res, \
                           input=([int(x.split('=')[1]) for x in list(map(str,request.form.values())) if
                                          str(x) not in ['cases', 'rl', 'action_rules', 'deaths']]), \
                           parameters_names=parameters_names,\
                           show_res=1)


@app.route('/models')
def input():

    return render_template('input_var.html', parameters_names=parameters_names)

@app.route('/')
def main():
    return render_template('main.html', parameters_names=parameters_names)

if __name__ == '__main__':
    app.run()
