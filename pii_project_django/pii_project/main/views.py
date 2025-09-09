from django.shortcuts import render
from django.http import FileResponse
import os
from django.conf import settings
from utils.image_pii_presidio import anonymize_image   # 👈 utils file import

# Upload aur output folders set karo (media ke andar)
UPLOAD_FOLDER = os.path.join(settings.MEDIA_ROOT, 'uploads')
OUTPUT_FOLDER = os.path.join(settings.MEDIA_ROOT, 'output')

# Agar folders na bane ho to bana do
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# Home page view (upload + process)
def index(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        filename = file.name

        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_filename = 'anonymized_' + filename
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Upload file save karo
        with open(input_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        # Anonymization call
        anonymize_image(input_path, output_path)

        # Result page dikhao
        return render(request, 'result.html', {'filename': output_filename})

    # Agar GET request hai to sirf index.html dikhao
    return render(request, 'index.html')


# Download view
def download(request, filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
