from flask import Flask,render_template,request,redirect,session,flash

#redirect is used for calling that function that call home page in render_template in the case of login

#session is a dictionary

#saare functions ka naam alag hona chahiye

import mysql.connector
import os
app=Flask(__name__)
#ye ek special key hai jo, jb tk server mei hai aur user k paas wo as a cookie hai...tb tk session chalega
app.secret_key=os.urandom(24)

conVar=mysql.connector.connect(host='localhost',user='root',password='',database='car_resale_database')

@app.route('/')
def login():
    #this if else is to prevent home page se waps login page pr jaane k liye...untill logout na hojaye
    if 'currentUser' in session:
        return redirect('/home')
    else:    
        return render_template('login.html')

@app.route('/signup')
def signup():
    if 'currentUser' in session:
        return redirect('/home')
    else:
        return render_template('signup.html')

#simply ek variable to display name of active user on home page

@app.route('/home')
def homepage():
    #home page mei editing session bnane k baad krni hai
    if 'currentUser' in session:
        return render_template('home.html',activeUser=activeUser)
    else:
        #redirect changes the url...render_template sirf webpage badal deta hai...url change nhi krta hai
        return redirect('/')
        #return render_template('login.html')

@app.route('/login_validation',methods=['POST'])
def log_validation():
    name=request.form.get('name')
    mobile=request.form.get('mobile')
    password=request.form.get('password')
    cursorVar=conVar.cursor()
    cursorVar.execute("""select * from `allusers` where `name` like '{}' and `mob_no` like '{}' and `password` like '{}' """.format(name,mobile,password))
    #jo bhi result ayega list ki form mei hoga (list of list)....to usko fetch kr lenge..as under
    userDetail=cursorVar.fetchall()
    if len(userDetail)>0:
        session['currentUser']=userDetail[0][0]
        global activeUser
        activeUser=userDetail
        #userDetail is a list...therefore activeUser will also be a list...MIND IT....list of list
        #activeUser se sara kaam lo ab feedback, purchase, sell, edit ! 
        #url lo change kr dega ye...log_validation ki jagh home likha hua ayega 
        return redirect('/home')
        #return render_template('home.html')
    else:
        flash('Check your credentials and try again.','danger')
        return redirect('/')

#ek aur decorator bnayenge jo sign up krne k baad details ko database mei daalega aur fir uske return mei jo chaho wo page render krwa dena preferably home page.
@app.route('/user_addition',methods=['POST'])
def addUser():
    v_id=request.form.get('v_id')
    v_id_no=request.form.get('v_id_no')
    userName=request.form.get('name')
    userMob=request.form.get('mob')
    address=request.form.get('address')
    userPassword=request.form.get('password')

    cursorVar=conVar.cursor()
    cursorVar.execute("""insert into `allusers`(`user_id`,`verify_id`,`verify_no`,`name`,`mob_no`,`address`,`password`) values(NULL,'{}','{}','{}','{}','{}','{}')""".format(v_id,v_id_no,userName,userMob,address,userPassword))
    #COMMIT KRNA BOHT ZAROORI HAI
    conVar.commit()
    flash('Registered successfully. Login to continue.','info')
    return redirect('/')

@app.route('/feedbackpage')
def feedbackFunc():
    if 'currentUser' in session:
        return render_template('feedback.html',activeUser=activeUser)
    else:
        return redirect('/')

@app.route('/afterfeedback',methods=['POST'])
def afterfeedbackFunc():
    if 'currentUser' in session:
        name=request.form.get('name')
        feedback=request.form.get('feedback')
        ratings=request.form.get('ratings')
        s_no=activeUser[0][0]
        cursorVar2=conVar.cursor()
        cursorVar2.execute("""insert into `feedback_table`(`user_name`,`feedback`,`ratings`,`s_no`) values('{}','{}','{}','{}')""".format(name,feedback,ratings,s_no))
        conVar.commit()
        flash('feedback recorded successfully !','success')
        return redirect('/home')
    else:
        return redirect('/')

@app.route('/customerReview')
def crfunc():
    if 'currentUser' in session:
        cursor1=conVar.cursor()
        cursor1.execute("""select * from `feedback_table`""")
        reviewDetails=cursor1.fetchall()
        return render_template('customerReviews.html',reviewDetails=reviewDetails)
    else:
        return redirect('/')

@app.route('/aboutUs')
def aboutUsFunc():
    if 'currentUser' in session:
        return render_template('aboutUs.html')
    else:
        return redirect('/')

@app.route('/logout')
def logout_func():
    session.pop('currentUser')
    #session ek dictionary hai...usme eklauta element hai currentUser usi ko delete kr do! sara maamla hi khtm
    activeUser=[]
    return redirect('/')
################################################FOR DISPLAYING CARS####################
@app.route('/listOfCars')
def listOfcars():
    if 'currentUser' in session:
        cursorVar2=conVar.cursor()
        cursorVar2.execute("""select * from `car_to_purchase`""")
        carDetails=cursorVar2.fetchall()
        return render_template('cars_list.html',carDetails=carDetails)
        # return carDetails
    else:
        return redirect('/')

@app.route('/addACarToSell')
def addCarFunc():
    return '....'

if __name__=="__main__":
    app.run(debug=True)