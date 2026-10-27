import os, threading, uvicorn
from dotenv import load_dotenv
load_dotenv()
if __name__=='__main__':
    # Development sign-in must never be reachable on a public interface.
    dev_auth = os.getenv('DEV_AUTH', 'false').lower() == 'true'
    host = os.getenv('HOST', '127.0.0.1')
    if dev_auth and host not in ('127.0.0.1', 'localhost', '::1'):
        raise SystemExit('ОШИБКА: DEV_AUTH=true разрешён только с HOST=127.0.0.1')
    uvicorn.run('app.main:app',host=host,port=int(os.getenv('PORT','8000')))

