#!/usr/bin/python3

import cgi
import random
import gammu

LOGIN = 'glmf'
PWD   = 'L1nu><'
TEL   = '0611223344'

def generatePassword(length=6):
    code = ''
    for i in range(length):
        code += str(random.randint(0, 9))
    with open('.code_storage', 'w') as fic:
        fic.write(code)
    return code


def sendSMS(code, phoneNumber):
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()
    if sm.GetSecurityStatus() == 'PIN':
        sm.EnterSecurityCode('PIN', '0000')
    msgToSend = {
            'Text' : 'Votre code de connexion : ' + code,
            'SMSC' : {'Location' : 1},
            'Number' : phoneNumber,
    }
    sm.SendSMS(msgToSend)


if __name__ == '__main__':
    form = cgi.FieldStorage()
    print('Content-type: text/html; charset=utf-8\n')

    access = False
    login = form.getvalue('login')
    pwd = form.getvalue('password')
    code = form.getvalue('code')

    if code is not None:
        with open('.code_storage', 'r') as fic:
            code_sms = fic.read()
        if code == code_sms:
            print('ACCÈS AUTORISÉ')
            access = True
        else:
            print('Erreur dans le code SMS. Retour à la case départ')

    if login == LOGIN and pwd == PWD:
        with open('sms.html', 'r') as fic:
            html = fic.read()
        code_sms = generatePassword()
        sendSMS(code_sms, TEL)
    else:
        if login is not None or pwd is not None:
            print('Identifiants incorrects !')
        with open('index.html', 'r') as fic:
            html = fic.read()

    if not access:
        print(html)
