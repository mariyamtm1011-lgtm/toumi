import os
import numpy as np
from django.conf import settings

def load_known_encodings():
    encodings = []
    names = []
    encoded_dir = os.path.join(settings.MEDIA_ROOT, 'encoded')

    if not os.path.exists(encoded_dir):
        return encodings, names

    for fname in os.listdir(encoded_dir):
        if fname.endswith('.npy'):
            arr = np.load(os.path.join(encoded_dir, fname))
            encodings.append(arr)
            names.append(os.path.splitext(fname)[0])

    return encodings, names
