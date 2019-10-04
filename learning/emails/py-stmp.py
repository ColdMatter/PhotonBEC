
import smtplib
from getpass import getpass

fromAddr = 'photonbec@gmail.com'
pw = getpass('Type password for ' + fromAddr + ' :')
toAddr = raw_input('Type to address :')

#toAddr = 'photonbec@gmail.com'
text = 'hello world'

message = 'From: ' + fromAddr + '\r\nTo: ' + toAddr + ' \r\n\r\n' + text

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.set_debuglevel(1)
server.login(fromAddr, pw)
server.sendmail(fromAddr, toAddr, message)
server.quit()