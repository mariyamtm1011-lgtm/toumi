import cv2
import numpy as np
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import AccessLog
from .face_service import load_known_encodings
import face_recognition


# ======================
# PAGE D'ACCUEIL
# ======================
def index(request):
    return render(request, "recognition/index.html")



# ======================
# PAGE : MES LOGS (USER)
# ======================
@login_required
def my_logs(request):
    logs = AccessLog.objects.filter(user=request.user).order_by('-date_time')
    return render(request, "recognition/my_logs.html", {"logs": logs})



# ======================
# PAGE : RECONNAISSANCE AVEC CAMERA
# ======================
def camera(request):

    # Charger les encodages (.npy)
    known_encodings, known_names = load_known_encodings()

    if len(known_encodings) == 0:
        return HttpResponse("Aucun visage enregistré ! Ajoutez d'abord des utilisateurs.")

    # Ouvrir la caméra
    video = cv2.VideoCapture(0)

    if not video.isOpened():
        return HttpResponse("Impossible d'accéder à la caméra.")

    recognized_name = None
    result = "denied"

    # Lire 1 image
    ret, frame = video.read()

    if not ret:
        return HttpResponse("Erreur lors de la capture !")

    # Convertir en RGB (car OpenCV utilise BGR)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Localiser les visages dans l'image
    locations = face_recognition.face_locations(rgb)

    if len(locations) > 0:
        # Encoder le visage détecté
        encoding = face_recognition.face_encodings(rgb, locations)[0]

        # Comparer avec encodages connus
        matches = face_recognition.compare_faces(known_encodings, encoding)
        distances = face_recognition.face_distance(known_encodings, encoding)

        best_match = np.argmin(distances)

        if matches[best_match]:
            recognized_name = known_names[best_match]
            result = "granted"

    # Enregistrement dans la base
    if result == "granted":
        try:
            user = User.objects.get(username=recognized_name)
        except User.DoesNotExist:
            user = None
        AccessLog.objects.create(
            user=user,
            result="granted",
            note=f"Matched {recognized_name}"
        )
    else:
        AccessLog.objects.create(
            user=None,
            result="denied",
            note="No match detected"
        )

    # Libérer caméra
    video.release()
    cv2.destroyAllWindows()

    # Retour page résultat
    return render(request, "recognition/result.html", {
        "result": result,
        "name": recognized_name
    })
