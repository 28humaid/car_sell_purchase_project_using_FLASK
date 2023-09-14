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
        cursorVar2.execute("""select * from `car_to_purchase` left join `transaction_table` on `car_to_purchase`.`c_no`=`transaction_table`.`car_number` where `transaction_table`.`now_available`=1""")
        carDetails=cursorVar2.fetchall()
        return render_template('cars_list.html',carDetails=carDetails)
        # return carDetails
    else:
        return redirect('/')

@app.route('/addACarToSell')
def addCarFunc():
    if 'currentUser' in session:
        return render_template('addACar.html')
    else:
        return redirect('/')
@app.route('/afterAddingCar',methods=['POST'])
def aacFunc():
    if 'currentUser' in session:
        seller_id=activeUser[0][0]
        c_name=request.form.get('carname')
        c_no=request.form.get('carno')
        color=request.form.get('color')
        registration_no=request.form.get('registerno')
        distance_travelled=request.form.get('distance_travelled')
        image_link=request.form.get('image_link')
        price=request.form.get('price')
        cursor1=conVar.cursor()
        cursor1.execute("""insert into `transaction_table`(`car_number`,`buyer_id`,`seller_serial_no`,`now_available`) values('{}','NULL','{}','1')""".format(c_no,seller_id))
        conVar.commit()
        cursor2=conVar.cursor()
        cursor2.execute("""insert into `car_to_purchase`(`c_name`,`c_no`,`color`,`registration_no`,`distance_travelled`,`image_link`,`price`) values('{}','{}','{}','{}','{}','{}','{}')""".format(c_name,c_no,color,registration_no,distance_travelled,image_link,price))
        conVar.commit()
        return redirect('/home')
    else:
        return redirect('/')
@app.route('/updatePersonalDetail')
def updFunc():
    if 'currentUser' in session:
        return render_template('updatePersonalDetail.html',activeUser=activeUser)
    else:
        return redirect('/')
@app.route('/afterUserDetailupdate',methods=['POST'])
def auFunc():
    if 'currentUser' in session:
        verify_no_check=activeUser[0][2]
        verify_id=request.form.get('verify_id')
        verify_no=request.form.get('verify_no')
        name=request.form.get('name')
        mob_no=request.form.get('mob_no')
        address=request.form.get('address')
        password=request.form.get('password')
        cursor1=conVar.cursor()
        cursor1.execute("""update `allusers` set `verify_id`='{}',`verify_no`='{}',`name`='{}',`mob_no`='{}',`address`='{}',`password`='{}' where `verify_no`='{}'""".format(verify_id,verify_no,name,mob_no,address,password,verify_no_check))
        conVar.commit()
        return redirect('/home')
    else:
        return redirect('/')
######################################## FOR PURCHASING A CAR ###############
@app.route('/purchaseCar',methods=['POST'])
def pacFunc():
    if 'currentUser' in session:
        buyer_id=activeUser[0][0]
        c_no=request.form.get('c_no')
        cursor1=conVar.cursor()
        cursor1.execute("""update `transaction_table` set `buyer_id`='{}',`now_available`='{}' where `car_number`='{}'""".format(buyer_id,0,c_no))
        conVar.commit()
        #yha pr sbka join krke details nikalni hai so that receipt mei display krwa skein.....
        #  select b.name as seller_name,a.name as buyer_name,t.car_number,c.c_name,c.registration_no from transaction_table t inner join allusers a on t.buyer_id=a.user_id inner join car_to_purchase c on t.car_number=c.c_no inner join allusers b on t.seller_serial_no=b.user_id;
        #cursor2=conVar.cursor()
        return render_template('purchaseAcar.html')
    else:
        return redirect('/')

if __name__=="__main__":
    app.run(debug=True)