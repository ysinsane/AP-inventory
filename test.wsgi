
activate_this = 'c:/flasktest/venv/Scripts/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

import site
import sys

prev_sys_path = list(sys.path)

site.addsitedir('c:/flasktest/venv/Scripts/Lib/site-packages')

new_sys_path = []

			
for item in list(sys.path):
	if item not in prev_sys_path:
		new_sys_path.append(item)
		sys.path.remove(item)
		sys.path[:0] = new_sys_path
		

sys.path.insert(0,"C:/flasktest")


from manage import app as application