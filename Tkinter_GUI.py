from tkinter import *
from pathlib import Path
from PIL import ImageTk, Image
from tkinter import messagebox
import sqlite3

from Viewer import *
from Editor import *
	

class Gui(DbAccess):
	root=Tk()
	root.title('Sign in!')
	root.geometry("430x450")
	#root.iconbitmap('@my_icon.xbm')

	database = "contact_data.db"
	my_db = Path(database)
	

	def __init__(self):
		if not self.my_db.is_file():
			conn = sqlite3.connect(self.database)
			c = conn.cursor()
			c.execute("""CREATE TABLE contact_data (
							first_name text,
							last_name text,
							email text,
							phone text,
							birthday text
							)""")
		self.viewer = Viewer(self)
		self.editor = Editor()

	def create_labels(self,window):
		'''
		This function creates the contact labels in the selected window
		'''
		self.f_name_label = Label(window, text="First Name")
		self.l_name_label = Label(window, text="Last Name")
		self.email_label = Label(window, text="Email")
		self.phone_label = Label(window, text="Phone number")
		self.birthday_label = Label(window, text="Birthday")
		
		self.f_name_label.grid(row=0, column=0, pady=(10,0))
		self.l_name_label.grid(row=1, column=0)
		self.email_label.grid(row=2, column=0)
		self.phone_label.grid(row=3, column=0)
		self.birthday_label.grid(row=4, column=0)


	def create_textboxes(self, window, data=None):
		'''
		This function creates the contact textboxes in the selected window
		'''
		
		self.f_name = Entry(window, width=30)
		self.l_name = Entry(window, width=30)
		self.email = Entry(window, width=30)
		self.phone = Entry(window, width=30)
		self.birthday = Entry(window, width=30)
		
		if data:
			self.f_name.insert(0, data[0])
			self.l_name.insert(0, data[1])
			self.email.insert(0, data[2])
			self.phone.insert(0, data[3])
			self.birthday.insert(0, data[4])
		
		self.f_name.grid(row=0, column=1,padx=20,pady=(10,0)) # Tupel in pady: only 10 to the top
		self.l_name.grid(row=1, column=1,padx=20)
		self.email.grid(row=2, column=1,padx=20)
		self.phone.grid(row=3, column=1,padx=20)
		self.birthday.grid(row=4, column=1,padx=20)

	def submit(self):
		'''
		This function submits new data to the database
		It sends the contact data to the database
		'''
		c, conn = self.connect_to_db()
		
		c.execute("INSERT INTO contact_data VALUES (:f_name, :l_name, :email, :phone, :birthday)",
							{
								'f_name': self.f_name.get(),
								'l_name': self.l_name.get(),
								'email': self.email.get(),
								'phone': self.phone.get(),
								'birthday': self.birthday.get()
							}
				)
				
		# Clear textboxes
		self.f_name.delete(0,END)
		self.l_name.delete(0,END)
		self.email.delete(0,END)
		self.phone.delete(0,END)
		self.birthday.delete(0,END)
		
		self.disconnect_to_db(conn)

	def delete(self):
		'''
		This function deletes a selected record in the database
		The record is selected with its oid
		'''
		c, conn = self.connect_to_db()
		
		number_of_records = len(c.execute("SELECT *, oid FROM contact_data").fetchall())
		sel_id = self.check_id(number_of_records)
		if sel_id == "false":
			return
		
		c.execute("DELETE from contact_data WHERE oid = " + sel_id)

		self.select_box.delete(0,END)
		self.disconnect_to_db(conn)


	def update(self,window=None):
		'''
		This function saves changes of editing records
		'''
		c, conn = self.connect_to_db()
		record_id = self.select_box.get()
		
		c.execute(""" UPDATE contact_data 
		              SET first_name = :first, 
											last_name = :last,
											email = :email,
											phone = :phone,
											birthday = :birthday
									WHERE oid = :oid """,
			{	'first': self.f_name_editor.get(),
				'last': self.l_name_editor.get(),
				'email': self.email_editor.get(),
				'phone': self.phone_editor.get(),
				'birthday': self.birthday_editor.get(),
				'oid': record_id # necessary	
			})
		window.destroy()
		self.disconnect_to_db(conn)

	def make_window(self):
		# Create a LabelFrame
		# labels and textboxes to enter data
		# submit button and show records button
		self.data_frame = LabelFrame(self.root, text="Contact Data", padx=2, pady=10)
		self.data_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5) # padding outside
		self.create_labels(self.data_frame)
		self.create_textboxes(self.data_frame)

		self.submit_btn = Button(self.data_frame, text="Add Record To Database", command=self.submit)
		self.submit_btn.grid(row=5, column=0, columnspan=2, pady=(20,0), padx=10, ipadx=100)

		self.query_btn = Button(self.data_frame,text="Show Records", command=lambda: self.viewer.make_window())
		self.query_btn.grid(row=6, column=0, columnspan=2, pady=(5,5), padx=10, ipadx=135)

		# Create a LabelFrame
		# select label and box
		# edit button and delete button

		self.select_frame = LabelFrame(self.root, text="Edit Data", padx=2, pady=10)
		self.select_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5) # padding outside

		self.select_box_label = Label(self.select_frame, text="Select ID")
		self.select_box_label.grid(row=0, column=0)
		self.select_box = Entry(self.select_frame, width=30)
		self.select_box.grid(row=0, column=1)

		self.edit_btn = Button(self.select_frame,text="Edit Record", command=lambda: self.editor.make_window(self.select_box.get()))
		self.edit_btn.grid(row=1, column=0, columnspan=2, pady=(20,0), padx=10, ipadx=145)

		self.delete_btn = Button(self.select_frame,text="Delete Record", command=self.delete)
		self.delete_btn.grid(row=2, column=0, columnspan=2, pady=(5,5), padx=10, ipadx=135)

		# Statusbar at bottom of root window
		#status = Label(root, text="myStatus", relief=SUNKEN, anchor=E)
		#status.grid(row=13,column=0,columnspan=2, sticky=W+E)

	def run(self):
		self.root.mainloop()				
	
if __name__ == "__main__":
	g = Gui()
	g.make_window()
	g.run()
