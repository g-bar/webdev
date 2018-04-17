#verify.py
import re
user =  re.compile("^[a-zA-Z0-9_-]{3,20}$")
password = re.compile("^.{3,20}$")
email = re.compile("^[\S]+@[\S]+.[\S]+$")


def verify_user(s):
    return user.match(s)
    
def verify_pass(p1):
    return password.match(p1)
        
def verify_email(s):
    return email.match(s)

    
if __name__ == "__main__":
    print verify_user('invalid user')
    print verify_pass('1sadf')
    print verify_email('thisisanemail@email.com')