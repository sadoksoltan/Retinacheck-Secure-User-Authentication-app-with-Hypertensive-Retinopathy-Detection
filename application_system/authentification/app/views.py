from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from authentification import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from . token import generateToken
from django.core.files.storage import FileSystemStorage
import re
from keras.models import Sequential, model_from_json,model_from_yaml
import cv2
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from math import sqrt 
from tensorflow import Graph
import tensorflow as tf
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import views as auth_views
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _
import uuid
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth import authenticate,login,logout
from .helpers import send_forget_password_mail

model_graph = tf.Graph()
with model_graph.as_default():
    tf_session = tf.compat.v1.Session()
    with tf_session.as_default():
        model = load_model('./models/HRD.h5')
# Create your views here.
def home(request, *args, **kwargs):
    return render(request, 'app/index.html')
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2'] 
        if User.objects.filter(username=username):
            messages.error(request, 'Le nom d\'utilisateur est déjà utilisé, veuillez en choisir un autre.')
            return redirect('register')
        if User.objects.filter(email=email):
            messages.error(request, 'Cette adresse e-mail est déjà associée à un compte.')
            return redirect('register')
        if len(username)>10:
            messages.error(request,'Le nom d\'utilisateur doit comporter moins de 10 caractères.')
        if len(username)<5:
            messages.error(request, 'Le nom d\'utilisateur doit comporter au moins 5 caractères.')
            return redirect('register')
        if not username.isalnum():
            messages.error(request, 'Le nom d\'utilisateur doit être alphanumérique.')
            return redirect('register')
        if password != password2:
            messages.error(request,  'Les mots de passe ne correspondent pas.')  
            return redirect('register')  
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            messages.error(request, 'L\'adresse e-mail n\'est pas valide,\nveuillez entrer une adresse e-mail valide.')
            return redirect('register')
           
        my_user = User.objects.create_user(username, email, password)
        my_user.first_name =firstname
        my_user.last_name = lastname
        my_user.is_active = False
        my_user.save()
        profile_obj = Profile.objects.create(user = my_user )
        messages.success(request, 'Votre compte a été créé avec succès. Nous vous avons envoyé un e-mail pour confirmer votre adresse e-mail.\n\nVous devez confirmer votre compte pour l\'activer.')
        # send email when account has been created successfully
        subject = "Bienvenue sur l'application de  Sadok"
        message = "Bienvenue " + my_user.first_name + " " + my_user.last_name + "\nMerci d'avoir choisi le site Retina Check.\nPour vous connecter,vous devez confirmer votre adresse e-mail.\nMerci\n\n\nSadok Soltan"
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)
        #confirmation
        current_site = get_current_site(request) 
        email_suject = "Confirmez votre adresse e-mail - Sadok Admin"
        messageConfirm = render_to_string("emailConfimation.html", {
            'name': my_user.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generateToken.make_token(my_user)
        })   

        
        email = EmailMessage(
            email_suject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [my_user.email]
        )

        email.fail_silently = False
        email.send()    
        return redirect('login_view')
    return render(request, 'app/register.html')

from django.core.exceptions import ObjectDoesNotExist

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            my_user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            return redirect('login_view')
        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, 'app/ret.html', {"firstname":firstname})
        elif my_user.is_active == False:
            messages.error(request, 'Vous n\'avez pas confirmé votre adresse e-mail.\nVeuillez le faire pour activer votre compte.')  
            return redirect('login_view')  
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            return redirect('login_view') 
    return render(request, 'app/login.html')  
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous êtes déconnecté avec succès !')
    return redirect('home')
def ret(request):
    context={'a':1}
    return render(request,'app/ret.html',context)
def predictImage(request):
    print (request)
    print (request.POST.dict())
    fileObj=request.FILES['filePath']
    fs=FileSystemStorage()
    filePathName=fs.save(fileObj.name,fileObj)
    filePathName=fs.url(filePathName)
    img = '.'+ filePathName
    img = cv2.imread(img)
    r,imageGreen,b = cv2.split(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img_clahe = clahe.apply(img[:,:,1])
    model = load_model('./models/HRD.h5')
    kernel = np.ones((31,31))/961
    imgavg = cv2.filter2D(img_clahe,-1,kernel)
    hist = cv2.calcHist([img_clahe],[0],None,[256],[0,256])
    maxVal = -1
    maxLoc = [(0,0)]
    for x in range(imgavg.shape[0]):
        for y in range(imgavg.shape[1]):
            #print(x,y)
            if imgavg[x][y] >= maxVal:
                maxVal = imgavg[x][y]
                maxLoc[0] = (y,x) 
    loc = len(maxLoc)
    imgtemp = imgavg.copy()
    cv2.circle(imgtemp,maxLoc[loc-1],5,(0),-1)
    thresh, imgthresh = cv2.threshold(imgavg,180,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(imgthresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img_clahe, contours, contourIdx=-1, color=0, thickness=1)  
    length = len(contours[0])
    radius = 0
    for i in range(length):
        radius = radius + sqrt((contours[0][i][0][0]-maxLoc[0][0])**2 + (contours[0][i][0][0]-maxLoc[0][0])**2)
    radius = int(radius/length)
    imgtemp2 = imgavg.copy()
    cv2.circle(imgtemp2,maxLoc[loc-1],int(radius),(0),2)
    ROIrad = radius*4
    mask = np.zeros((imgthresh.shape[0],imgthresh.shape[1]), dtype=np.uint8)
    cv2.circle(mask,maxLoc[loc-1],ROIrad,(255),-1)
    img_roi = cv2.bitwise_and(img, img, mask=mask)
    patch_size=27
    patches = []
    patches_copy=[]
    for i in range(0, img_clahe.shape[0]-patch_size, patch_size):
        for j in range(0, img_clahe.shape[1]-patch_size, patch_size):
            patch = img_clahe[i:i+patch_size, j:j+patch_size]
            patch = patch.reshape(-1)
            patches.append(patch)
            patches_copy.append(patch)
      
    patches = np.array(patches)
    patches = patches.astype('float32') / 255.0
    tf.config.experimental_run_functions_eagerly(True)
    predictions = model.predict(patches)
    tf.config.experimental_run_functions_eagerly(False)
    vessel_patches_copy = []
    for i, patch in enumerate(patches_copy):
        if np.max(predictions[i]) == 1.0:
            patch = patch.reshape((patch_size, patch_size))
            vessel_patches_copy.append(patch)
    vessel_patches = np.array(vessel_patches_copy)
    vessel_patches = vessel_patches.astype('float32') / 255.0
    patch_size=27
    binary_image = np.zeros_like(img_clahe)
    test= np.zeros_like(img_roi)
    idx = 0
    for i in range(0, img_clahe.shape[0]-patch_size, patch_size):
        for j in range(0, img_clahe.shape[1]-patch_size, patch_size):
            if predictions[idx][1] > predictions[idx][0]:
                binary_image[i:i+patch_size, j:j+patch_size] = 255
            idx += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
    overlay = cv2.addWeighted(img, 0.5, cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR), 0.5, 0)
    clahe = cv2.createCLAHE(clipLimit = 2.0, tileGridSize = (8,8))
    imageEqualized = clahe.apply(imageGreen)
    imageInv2 = 255 - imageEqualized
    imageInv = clahe.apply(imageInv2)
    b, g, r = cv2.split(overlay)
    mean_intensity = np.mean(g[mask > 0])*0.50
    artery_mask = np.logical_and(mask, g > mean_intensity)
    vein_mask = np.logical_and(mask, g <= mean_intensity)
    arteryDist = cv2.distanceTransform( artery_mask.astype(np.uint8) * 255,cv2.DIST_L1, cv2.DIST_MASK_PRECISE)
    veinDist = cv2.distanceTransform( vein_mask.astype(np.uint8) * 255,cv2.DIST_L1, cv2.DIST_MASK_PRECISE)
    venuole = []
    arteriole = []
    for x in range(veinDist.shape[0]):
        for y in range( veinDist.shape[1]):
            if  veinDist[x][y] > 0:
                venuole.append(abs( veinDist[x][y]))
            if arteryDist[x][y] > 0:
                arteriole.append(abs(arteryDist[x][y]))

    venuole = sorted(venuole)
    arteriole = sorted(arteriole)
    lenven = len(venuole)
    if lenven%2 == 1:
        Wa = venuole[lenven//2]
        if lenven//2 == 0:
            Wb = venuole[0]
        else:
            Wb = venuole[lenven//2 - 1]
    else:
        Wa = (venuole[lenven//2 - 1] + venuole[lenven//2])// 2
        Wb = venuole[lenven//2 - 1]

    CRVE = sqrt(0.72*(Wa**2) + 0.91*(Wb**2) + 450.02)
    lenart = len(arteriole)
    if lenart%2 == 1:
        Wa = arteriole[lenart//2]
        if lenart//2 == 0:
            Wb = arteriole[0]
        else:
            Wb = arteriole[lenart//2 - 1]
    else:
        Wa = (arteriole[lenart//2 - 1] + arteriole[lenart//2])// 2
        Wb = arteriole[lenart//2 - 1]

 
    CRAE = sqrt(0.8*(Wa**2) + 1.01*(Wb**2) - 0.22*Wa*Wb-10.73)
    if len(venuole) == 0 or len(arteriole) == 0:
        predictedLabel="Il n'y a pas de vaisseaux dans l'image"
    else:
        artervenratio = CRAE/CRVE  
    predictedLabel=artervenratio
    if 0.7 <= artervenratio <=1:
        predictedLabel="Cette rétine est en bonne santé."
    else :
        predictedLabel="Cette rétine présente des anomalies."
    context={'filePathName':filePathName,'predictedLabel':predictedLabel}
    return render(request,'app/ret.html',context)
def ChangePassword(request , token):
    context = {}  
    try:
        profile_obj = Profile.objects.filter(forget_password_token = token).first()
        context = {'user_id' : profile_obj.user.id}
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('reconfirm_password')
            user_id = request.POST.get('user_id')
            if user_id is  None:
                messages.success(request, 'Aucun utilisateur trouvé avec ce Nom d&apos;utilisateur.')
                return redirect(f'/change-password/{token}/')
            if  new_password != confirm_password:
                messages.success(request, 'Les mots de passe ne correspondent pas.')
                return redirect(f'/change-password/{token}/')               
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, 'mot de passe changé avec succes')
            return redirect('login_view')     
    except Exception as e:
        print(e)
    return render(request , 'app/change-password.html' , context)
def ForgetPassword(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')      
            if not User.objects.filter(username=username).first():
                messages.success(request, "Aucun utilisateur trouvé avec ce Nom d'utilisateur.")
                return redirect('forget_password')          
            user_obj = User.objects.get(username = username)
            token = str(uuid.uuid4())
            profile_obj= Profile.objects.get(user = user_obj)
            profile_obj.forget_password_token = token
            profile_obj.save()
            send_forget_password_mail(user_obj.email , token)
            messages.success(request, 'Un email de reinitialisation est envoyé.')
            return redirect('forget_password')   
    except Exception as e:
        print(e)
    return render(request , 'app/forget-password.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None

    if my_user is not None and generateToken.check_token(my_user, token):
        my_user.is_active  = True        
        my_user.save()
        messages.success(request, "Votre compte est activé !\nVous pouvez vous connecter en remplissant le formulaire ci-dessous.")
        return redirect("login_view")
    else:
        messages.success(request, 'L\'activation a échoué, veuillez réessayer.')
        return redirect('home')
