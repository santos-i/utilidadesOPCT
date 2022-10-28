'''
Rotina criada para atualizar os arquivos xmlcon dos CTDS SBE-37SM.

Para o correto funcionamento é necessário salvar os seguintes arquivos numa única pasta:
    - xmlcon dos respectivos ctds a serem atualizados
    - o próprio script, rs.
    - os parâmetros dos ctds salvos em diferentes arquivos txt
    nomeados com seus respectivos nº de série.**

** O conteúdo do txt deve ser retirado da última página do certficado da unimetro. ex:

                        SBE37SM-RS232 V 3.1 15895
                        temperature: 15-10-22
                        TA0 = 2.210512e-05
                        TA1 = 2.784614e-04
                        TA2 = -2.519399e-06
                        TA3 = 1.622164e-07
                        conductivity: 15-10-22
                        G = -1.000832e+00
                        H = 1.000000e+00
                        I = -8.991192e-04
                        J = 8.232707e-05
                        CPCOR = -9.570000e-08
                        CTCOR = 3.250000e-06
                        WBOTC = -2.976251e-08
                        pressure S/N 10291624, range = 5076 psia 15-10-22
                        PA0 = 1.098158e+00
                        PA1 = 1.742736e-02
                        PA2 = -7.822178e-10
                        PTCA0 = 5.248023e+05
                        PTCA1 = 8.442620e+00
                        PTCA2 = -2.493921e-01
                        PTCB0 = 2.359763e+01
                        PTCB1 = 1.925000e-03
                        PTCB2 = 0.000000e+00
                        PTEMPA0 = -6.918837e+01
                        PTEMPA1 = 5.115338e-02
                        PTEMPA2 = -5.776850e-07
                        POFFSET = 8.720000e-02
                        --- fim do certificado ---


Exemplo dos arquivos:
    'xmlcon_generator.py'
    '15895.txt'
    'SBE37SM-RS232_03715895_2022_08_07.xmlcon'


O xmlcon atualizado será criado no diretorio './saida/NOME_DO_ARQUIVO'
'''


import glob
import re
from datetime import datetime as dt


# Coeficientes que são nomeados de forma diferente 
# entre o certificado e o xmlcon do equipamento.
certificate_x_xmlcon = {
    'TA0': 'A0',
    'TA1': 'A1',
    'TA2': 'A2',
    'TA3': 'A3',
    'CPCOR': 'CPcor',
    'CTCOR': 'CTcor',
} 

txt_files = glob.glob('*.txt')

for file in txt_files:
    SN = file.split('.txt')[0]  
    
    file = open(file, 'r')

    coefficients = {}
    dates = []

    for line in file.readlines():
        if 'conductivity' in line or 'temperature' in line:
            temp = line.split(':')
            sensor, date = temp[0].strip(), temp[1].strip()
            # formata a data para o padrão do xmlcon
            date = dt.strptime(date, '%d-%m-%y')
            dates.append(date)  # adiciona à lista dates o 
                                # objeto datetime para comparação futura
            sensor_date = date.strftime('%d%b%y') # transforma para o padrão do xmlcon
            coefficients[sensor] = sensor_date

        elif 'pressure' in line:
            date = line.split('psia ')[-1].strip()
            date = dt.strptime(date, '%d-%m-%y')
            dates.append(date)  # adiciona à lista dates o 
                                # objeto datetime para comparação futura
            sensor_date = date.strftime('%d%b%y') # transforma para o padrão do xmlcon
            coefficients['calibrationDataPressure'] = sensor_date

        else:
            try:
                coef, value = line.split('=')
                coefficients[coef.strip()] = value.strip()
            except:
                pass

    # obtem o nome do arquivo xmlcon de acordo com o SN informado no .txt 
    xmlcon_file = glob.glob(f'SBE37SM-RS232_037{SN}*')[0]

    with open(xmlcon_file, 'r') as f:
        xmlcon = f.read()


    for coef, value in coefficients.items():
        # compara e atualiza os coeficientes que são 
        # diferentes entre o certificado e o xmlcon
        if coef in certificate_x_xmlcon.keys():
            coef = certificate_x_xmlcon[coef]

        xmlcon = re.sub(
                    f'<{coef}>.*<', # padrão buscado  *velho 
                    f'<{coef}>{value}<', # padrão *novo
                    xmlcon # objeto modificado
                )

        # Offset de pressão é o unico que aparece no
        # comando ds do CTD.
        if coef == 'POFFSET':
            xmlcon = re.sub(
                re.findall('<Offset>.*<',xmlcon)[-1], # padrão buscado *velho
                f'<Offset>{value}<', # padrão *novo
                xmlcon, # objeto modificado
            )

        if coef == 'calibrationDataPressure':
            xmlcon = re.sub(
                re.findall('<CalibrationDate>.*<',xmlcon)[-1], # padrão buscado *velho
                f'<CalibrationDate>{value}<', # padrão *novo
                xmlcon, # objeto modificado
            )
        
        if coef == 'conductivity':
            xmlcon = re.sub(
                re.findall('<CalibrationDate>.*<',xmlcon)[1], # padrão buscado *velho
                f'<CalibrationDate>{value}<', # padrão *novo
                xmlcon, # objeto modificado
            )

        if coef == 'temperature':
            xmlcon = re.sub(
                re.findall('<CalibrationDate>.*<',xmlcon)[0], # padrão buscado *velho
                f'<CalibrationDate>{value}<', # padrão *novo
                xmlcon, # objeto modificado
            )
    # novo formato de data para o nome do xmlcon
    new_date = sorted(dates)[0].strftime('%Y_%m_%d')
    
    with open(f'saida/SBE37SM-RS232_037{SN}_{new_date}.xmlcon', 'w+') as x:
        x.writelines(xmlcon)
