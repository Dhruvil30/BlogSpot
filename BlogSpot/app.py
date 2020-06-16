from flask import Flask,render_template,request,session
import sqlite3


# Class for all the database operations
class database_operations:


	# Getting user list at the time of login for furture operations
	def get_users_list(self):

		username = []

		# User list for login users
		con = sqlite3.connect("templates/data_book.db")
		c = con.cursor()
		c.execute("SELECT username FROM users")
		attributes = c.fetchall()
		con.close()

		for user_data in attributes:
			username.append(user_data[0])

		# Storing the userlist for further operations
		session['user_list'] = username


	# To see user list for admin
	def get_user_list_for_display(self):

		user_list = []

		# User list for admin
		con = sqlite3.connect("templates/data_book.db")
		c = con.cursor()
		c.execute("SELECT username FROM users")
		attributes = c.fetchall()
		con.close()

		for user_data in attributes:
			user_list.append(user_data[0])

		return user_list


	# Check the password of user
	def check_if_password_is_right(self,usrname,password):

		attributes = []

		con = sqlite3.connect("templates/data_book.db")
		c = con.cursor()
		c.execute("SELECT password FROM users WHERE username = '" + usrname + "'")
		attributes = c.fetchone()
		con.close()

		if password == attributes[0]:
			return True
		else:
			return False


	# Insert users details in users table
	def insert_into_database_new_user(self,usrname,pwd):

		con = sqlite3.connect('templates/data_book.db')
		c = con.cursor()
		c.execute("INSERT INTO users VALUES (:username,:password)",
				{
					'username' : usrname,
					'password' : pwd
				}
			)
		con.commit()
		con.close()


	# Delete username from database
	def delete_user_from_database(self,usrname):

		con = sqlite3.connect('templates/data_book.db')
		c = con.cursor()
		c.execute("DELETE FROM users WHERE username = '" + usrname + "'")
		con.commit()
		con.close()


	# Register user in the database
	def insert_into_database(self,usrname,pwd):
		
		# Make entry of user in database 
		self.insert_into_database_new_user(usrname,pwd)

		# Make table for user's posts
		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute(" CREATE TABLE " + usrname + "(subject text,content text, PRIMARY KEY (subject))")
		con.commit()
		con.close()


	# Edit the user details form database
	def edit_from_database(self,usrname,pwd):

		# Create table with new username in users database
		self.insert_into_database_new_user(usrname,pwd)

		# Renaming the posts table name to new username
		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute("ALTER TABLE " + session['user'] + " RENAME TO " + usrname)
		con.commit()
		con.close()

		# Deleting old username from database
		self.delete_user_from_database(session['user'])

		# Updating session variables as per new username and removing old usernames
		session['user_list'].remove(session['user'])
		session['user'] = usrname
		session['user_list'].append(session['user'])


	# Delete the user form database
	def delete_from_database(self,usrname):

		# Dalete entry of user form database
		self.delete_user_from_database(usrname)

		# Delete table of user's posts
		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute("DROP TABLE '" + usrname + "';")
		con.commit()
		con.close()


	# Add the post of user to database
	def add_post(self,usrname,post_sub,post_con):

		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute("INSERT INTO " + usrname +" VALUES (:subject,:content)",
				{
					'subject' : post_sub,
					'content' : post_con
				}
			)
		con.commit()
		con.close()
		return True


	# Check if the subject exsits in the database to display
	def get_subject_list(self,user):

		sub_list = []

		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute("SELECT subject FROM '" + user + "'")
		subjects = c.fetchall()
		con.close()

		for subject in subjects:
			sub_list.append(subject[0])

		# Storing the userlist for further operations
		session['sub_list'] = sub_list


	# Show the posts of a perticular user
	def show_posts(self,usrname):
		
		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute("SELECT * FROM '" + usrname + "'")
		posts = c.fetchall()
		con.close()
		return posts


	# Show the posts by the subject
	def show_posts_by_sub(self,sub_name,usrname):

		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute("SELECT * FROM '" + usrname + "' WHERE subject = '" + sub_name + "'")
		posts = c.fetchall()
		con.close()
		return posts


	# Checking if the post entered exists or not
	def check_if_post_exists(self,del_sub,name):

		posts = []

		con = sqlite3.connect("templates/data_post.db")
		c = con.cursor()
		c.execute("SELECT subject FROM '" + name + "'")
		attributes = c.fetchall()
		con.close()

		for post in attributes:
			posts.append(post[0])

		if del_sub in posts:
			return True
		else:
			return False

	# Checking if searched user has any post or not
	def check_if_any_post(self,search_name):

		con = sqlite3.connect("templates/data_post.db")
		c = con.cursor()
		c.execute("SELECT subject FROM '" + search_name + "'")
		attributes = c.fetchall()
		con.close()

		if attributes == []:
			return False
		else:
			return True

	# Delete the post from the database
	def delete_post(self,del_sub,name):

		con = sqlite3.connect('templates/data_post.db')
		c = con.cursor()
		c.execute("DELETE FROM '" + name + "' WHERE subject = '" + del_sub + "'")
		con.commit()
		con.close()


app = Flask(__name__)

#secret key for session variables
app.secret_key = "sdf5sdf1sadfd5v2sdd5as6dsddf1asd"  


# Load the login page
@app.route('/')
def login_page():
	return render_template("login_page.html")


# Login page
@app.route('/form_login', methods = ['GET','POST'])
def login_acc():

	db_op = database_operations()
	db_op.get_users_list()

	# Clicks on login button
	if 'login_button' in request.form:

		# Getting the data of entries
		usrname = request.form['username']
		pwd = request.form['password']

		# Entries are empty
		if usrname == '' or pwd == '':
			return render_template("login_page.html", status = 'Please enter username and password')

		else:
			db_op_login = database_operations()

			# Username is not registered
			if usrname not in session['user_list']:
				return render_template("login_page.html", status = 'Username not registerd')
			else:
				# Password is wrong
				if db_op_login.check_if_password_is_right(usrname,pwd) == False:
					return render_template("login_page.html", status = 'Invalid password')
				else:
					# Login of valid user
					session["user"] = usrname
					return render_template("main_page.html", name = session["user"])

	# Click on register button
	elif 'register_button' in request.form:
		return render_template("register_page.html")

	# Click on delete button
	elif 'delete_button' in request.form:
		return render_template("delete_page.html")

	# Click on admin button
	elif 'admin_button' in request.form:
		return render_template("admin_login.html")


# Admin login page
@app.route('/form_admin_login', methods = ['POST','GET'])
def admin_login():
	
	admin_pwd = request.form['password']

	# Password not entered
	if admin_pwd == '':
		return render_template("admin_login.html", status = 'Enter the password')

	else:
		# Valid admin
		if admin_pwd == '96257400':
			return render_template("admin.html")
		# Password wrong
		else:
			return render_template("admin_login.html", status = 'Password is wrong')


# Admin page
@app.route('/form_admin', methods = ['POST','GET'])
def admin():

	usrname = request.form['username']

	# Display users button
	if 'display_users_button' in request.form:
		db_op_admin = database_operations()
		users = db_op_admin.get_user_list_for_display()
		return render_template('admin.html', users = users)

	# Delete users button
	elif 'delete_user_button' in request.form:

		# Username entry is empty
		if usrname == '':
			return render_template('admin.html', status = 'Enter the username')

		else:
			db_op_admin = database_operations()
			db_op_admin.get_users_list()

			# User is not registered
			if usrname not in session['user_list']:
				return render_template('admin.html', status = 'User not registered')
			# Deleting the users account
			else:
				db_op_admin.delete_from_database(usrname)
				return render_template('admin.html', status = 'Account Deleted')

	# Logout button
	elif 'logout_button' in request.form:
		return render_template('login_page.html', status = 'Logged Out')


# Register page
@app.route('/form_register', methods = ['POST','GET'])
def register_acc():

	# Getting entries from page
	usrname = request.form['username']
	pwd = request.form['password']
	con_pwd = request.form['con_password']

	db_op_register = database_operations()

	# User already exists
	if usrname in session['user_list']:
		return render_template("register_page.html", status = 'User already Registered') 

	# User name entry is empty
	elif usrname == '':
		return render_template("register_page.html", status = 'Please enter username')

	else:
		# Password is not entered
		if pwd == '':
			return render_template("register_page.html", status = 'Please enter password')
		else:
			# User successfully registered
			if pwd == con_pwd:
				db_op_register.insert_into_database(usrname,pwd)
				return render_template("login_page.html", status = 'User Registerd')
			# Passeord do not match
			else:
				return render_template("register_page.html", status = 'Password do not match')


# Delete page
@app.route('/form_delete', methods = ['POST','GET'])
def delete_acc():

	# Getting entries from page
	usrname = request.form['username']
	pwd = request.form['password']

	# Password not entered
	if pwd == '':
		return render_template("delete_page.html", status = 'Please enter password')
	else:
		db_op_delete = database_operations() 

		# User is not registered with entry name
		if usrname not in session['user_list']:
			return render_template("delete_page.html", status = 'No user registered using this name')
		else:
			# Password is wrong
			if db_op_delete.check_if_password_is_right(usrname,pwd) == False:
				return render_template("delete_page.html", status = 'Password is wrong')
			# Account successfully deleted
			else:
				db_op_delete.delete_from_database(usrname)
				return render_template("login_page.html", status = 'Account deleted')


# Main page
@app.route('/form_main', methods = ['POST','GET'])
def main_page():

	# Click on post button
	if 'post_button' in request.form:
		return render_template("post_status.html")

	# Click on logout button
	elif 'logout_button' in request.form:
		# Poping out session variables to none
		session.pop('user',None)
		session.pop('user_list', None)
		return render_template("login_page.html", status = 'Logged Out')

	#Click on edit button
	elif 'edit_button' in request.form:
		return render_template("edit_profile.html")

	# Click on search button
	elif 'search_button' in request.form:

		# Getting the entry of search bar
		search_bar = request.form['search_bar']

		# Name in the search bar is empty
		if search_bar == '':
			return render_template("main_page.html", name = session["user"], status = 'Please enter name in search box')
		else:
			db_op_main = database_operations()

			post_list = []

			# Getting ths user list from the database
			if search_bar in session['user_list']:
				if db_op_main.check_if_any_post(search_bar) == True:
					post_list = db_op_main.show_posts(search_bar)

			sub_dir = {}

			# Getting the subjects list from the database
			for user in session['user_list']:
				db_op_main.get_subject_list(user)
				# User has any post that match serach bar entry
				if search_bar in session['sub_list'] :
					sub_list = db_op_main.show_posts_by_sub(search_bar,user)
					sub_dir.update({user:sub_list})

			# No user or subjects found in database
			if post_list == [] and sub_dir == {}:
				status = "No Posts Found"
			# User or subject exists in the database
			else:
				status = ""

			# Passing the arguments in the page
			return render_template("main_page.html", name = session["user"], search_name = search_bar, 
				posts = post_list, sub_dir = sub_dir, status = status)


#Edit page
@app.route('/form_edit', methods = ['POST','GET'])
def edit_profile():

	edit_usrname = request.form['username']
	edit_password = request.form['password']

	# Click on update button
	if 'update_button' in request.form:

		# Username or password not entered
		if edit_usrname == '' or edit_password == '':
			return render_template("edit_profile.html", status = 'Enter the details')
		else:
			# User with same name exists
			if edit_usrname in session['user_list']:
				return render_template("edit_profile.html", status = 'User with this name already exists')
			else:
				db_op_edit = database_operations()
				db_op_edit.edit_from_database(edit_usrname,edit_password)
				return render_template("main_page.html", name = session["user"], status = 'Data updated') 


# Button that directs to main page
@app.route('/form_goto_main', methods = ['POST','GET'])
def goto_main():

	# Click on main page button
	if 'goto_main_button' in request.form:
		return render_template("main_page.html", name = session["user"])


#Button that directs to login page
@app.route('/form_goto_login_page', methods = ['POST','GET'])
def goto_login_page():

	# Click on login page button
	if 'login_button' in request.form:
		return render_template("login_page.html")
 

# Add post page
@app.route('/form_add_post', methods = ['POST','GET'])
def add_post():

	# Getting the entries
	post_sub = request.form['post_subject']
	post_con = request.form['post_content']

	# Entries are empty
	if post_sub == '' or post_con == '':
		return render_template("post_status.html", status = 'Please enter the name of the post')
	else:
		# Post button clicked
		if 'add_post_button' in request.form:

			# Getting username using session variable 
			usrname = session['user']
			db_op_add_post = database_operations()
		
			# Post added successfully to database
			if db_op_add_post.add_post(usrname,post_sub,post_con) == True:
				return render_template("main_page.html", name = session["user"], status = 'Post added')
			# Subject already exists in the database
			else:
				return render_template("post_status.html", status = 'This subject already exists')


# Delete post page
@app.route('/form_delete_post', methods = ['POST','GET'])
def delete_post():

	# Getting the entry
	del_sub = request.form['delete_post']

	# Entry is empty
	if del_sub == '':
		return render_template("post_status.html", status = 'Please enter the name of the post')

	else:
		# Click on delete post button
		if 'delete_post_button' in request.form:
			db_op_delete_post = database_operations()

			# Post deleted successfully
			if db_op_delete_post.check_if_post_exists(del_sub,session["user"]) == True:
				db_op_delete_post.delete_post(del_sub,session["user"])
				return render_template("main_page.html", name = session["user"], status = 'Post Deleted')
			# Subject don't exixts in the database
			else:
				return render_template("post_status.html", status = 'Subject do not exists')


# Start of program
if __name__ == "__main__":
	app.run(debug = True)