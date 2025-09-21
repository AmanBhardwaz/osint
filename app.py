# import os
# import pytesseract
# import urllib.parse
# from PIL import Image, ImageChops
# from flask import Flask, render_template, request, redirect, url_for, send_from_directory
# from werkzeug.utils import secure_filename
# from dotenv import load_dotenv
# from google_images_search import GoogleImagesSearch
# import random

# # Load environment variables from the .env file
# load_dotenv()

# # Set the path to the Tesseract executable for OCR
# pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD_PATH')

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# # List of verified sources for credibility scoring
# VERIFIED_SOURCES = [
#     "reuters.com",
#     "apnews.com",
#     "bbc.com",
#     "nytimes.com",
#     "washingtonpost.com",
#     "thehindu.com"
# ]

# def allowed_file(filename):
#     """Checks if the file extension is allowed."""
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# def get_exif_data(image_path):
#     """Extracts EXIF metadata from an image."""
#     try:
#         image = Image.open(image_path)
#         exif_data = image._getexif()
#         if exif_data:
#             return {k: str(v) for k, v in exif_data.items()}
#     except Exception as e:
#         print(f"EXIF data not found or error: {e}")
#     return {}

# def perform_ocr(image_path):
#     """Performs Optical Character Recognition on the image."""
#     try:
#         text = pytesseract.image_to_string(Image.open(image_path))
#         return text
#     except Exception as e:
#         print(f"OCR failed: {e}")
#         return "No text found or OCR error."

# def perform_ela(image_path):
#     """Performs Error Level Analysis (ELA) on an image."""
#     try:
#         ela_path = os.path.join(app.config['UPLOAD_FOLDER'], 'ela_' + os.path.basename(image_path))
#         temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_ela.jpg')

#         original_image = Image.open(image_path).convert('RGB')
        
#         original_image.save(temp_path, 'JPEG', quality=95)
        
#         temp_image = Image.open(temp_path)
#         ela_image = ImageChops.difference(original_image, temp_image)
        
#         extrema = ela_image.getextrema()
#         max_diff = max([ex[1] for ex in extrema])
        
#         if max_diff == 0:
#             scale = 0
#         else:
#             scale = 255.0 / max_diff
        
#         ela_image = ela_image.point(lambda i: i * scale)
#         ela_image.save(ela_path)
#         os.remove(temp_path)
        
#         return os.path.basename(ela_path)
    
#     except Exception as e:
#         print(f"ELA failed: {e}")
#         return None

# def perform_reverse_search_with_api(image_path):
#     """Performs a reverse image search using Google Images Search API."""
#     try:
#         gis = GoogleImagesSearch(os.getenv('GOOGLE_API_KEY'), os.getenv('GOOGLE_CX'))
        
#         _search_params = {
#             'q': 'similar images',
#             'file_path': image_path
#         }
        
#         gis.search(search_params=_search_params)
        
#         results = []
#         for image in gis.results():
#             results.append({'title': image.title, 'url': image.url})
        
#         return results

#     except Exception as e:
#         print(f"Google Images Search API failed: {e}")
#         return []

# def calculate_credibility(search_results):
#     """Calculates a random credibility score for demo purposes."""
#     verified_count = 0
#     total_results = len(search_results)
    
#     for result in search_results:
#         try:
#             domain = urllib.parse.urlparse(result['url']).netloc
#             domain = domain.replace('www.', '')
            
#             if domain in VERIFIED_SOURCES:
#                 verified_count += 1
#         except:
#             continue

#     if total_results == 0:
#         return 0, 0
        
#     credibility_score = random.uniform(50, 100)
    
#     return credibility_score, verified_count

# def is_image_suspicious(filename, ela_image_path):
#     """
#     Checks if an image is suspicious based on ELA and filename flags.
#     For demo purposes.
#     """
#     # Check for demo flags in the filename
#     if "ai-gen" in filename.lower() or "deepfake" in filename.lower():
#         return True
    
#     # You can also add more advanced checks here based on ELA results
#     # For now, we'll keep it simple
#     return False

# def generate_takedown_request(platform_name, image_url):
#     """
#     Generates a pre-drafted takedown request email.
#     """
#     subject = f"Takedown Request: Unauthorized use of deepfake image"
    
#     body = f"""Dear {platform_name} Trust & Safety Team,

# I am writing to formally request the immediate removal of a deepfake image that has been unlawfully posted and is causing significant harm. The image is a falsified representation of me, created using AI technology.

# The URL of the infringing content is:
# {image_url}

# This image constitutes a deepfake and is a violation of your platform's policy against abusive or manipulated content. I have not consented to the creation or distribution of this image. Its continued presence is causing severe reputational damage and emotional distress.

# I kindly request that you take down this content without delay. I can provide any additional information needed to verify my identity.

# Thank you for your prompt attention to this matter.

# Sincerely,
# [Your Name]
# [Your Contact Information]
# """
#     return {"subject": subject, "body": body}


# def generate_report(exif_data, ocr_text, search_results, credibility_score, verified_count, is_suspicious, takedown_request):
#     """Generates a text report with all the findings."""
#     report_content = "--- Image Verification Report ---\n\n"
    
#     report_content += f"Suspicious Content Detected: {'Yes' if is_suspicious else 'No'}\n\n"
    
#     report_content += "1. Image Metadata (EXIF)\n"
#     if exif_data:
#         for key, value in exif_data.items():
#             report_content += f"  - {key}: {value}\n"
#     else:
#         report_content += "  - No EXIF data found.\n"
        
#     report_content += "\n2. OCR Text\n"
#     report_content += f"  - {ocr_text}\n"
    
#     report_content += f"\n3. Credibility Score: {credibility_score:.2f}%\n"
#     report_content += f"  - Found on {verified_count} verified source(s).\n"
    
#     report_content += f"\n4. Reverse Search Results ({len(search_results)} found)\n"
#     if search_results:
#         for i, result in enumerate(search_results):
#             report_content += f"  - {i+1}. {result['title']}\n"
#             report_content += f"     URL: {result['url']}\n"
#     else:
#         report_content += "  - No reverse search results found.\n"
    
#     if is_suspicious:
#         report_content += "\n5. Takedown Request Draft\n"
#         report_content += f"  - Subject: {takedown_request['subject']}\n"
#         report_content += f"  - Body:\n{takedown_request['body']}"
        
#     return report_content

# # --- Main Flask Routes ---

# @app.route('/')
# def index():
#     """Renders the main upload page."""
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     """Handles the file upload and initiates the OSINT tasks."""
#     if 'file' not in request.files:
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         return redirect(request.url)
    
#     if file and allowed_file(file.filename):
#         try:
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
#             file.save(filepath)

#             # Perform all OSINT tasks
#             exif_data = get_exif_data(filepath)
#             ocr_text = perform_ocr(filepath)
#             reverse_search_results = perform_reverse_search_with_api(filepath)
#             ela_image = perform_ela(filepath)
            
#             credibility_score, verified_count = calculate_credibility(reverse_search_results)
            
#             is_suspicious = is_image_suspicious(filename, ela_image)
#             takedown_request = None
#             if is_suspicious:
#                 # For demo, you'll have to manually get a public URL for the takedown request.
#                 # Or, you can just use a placeholder.
#                 takedown_request = generate_takedown_request("Platform Name", "Image URL Placeholder")
            
#             report_content = generate_report(exif_data, ocr_text, reverse_search_results, credibility_score, verified_count, is_suspicious, takedown_request)
#             report_filename = secure_filename(f"report_{os.path.basename(filepath)}.txt")
#             report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
            
#             with open(report_path, 'w', encoding='utf-8') as f:
#                 f.write(report_content)
            
#             return render_template('result.html', 
#                                    exif_data=exif_data, 
#                                    ocr_text=ocr_text, 
#                                    reverse_search_results=reverse_search_results,
#                                    uploaded_image=os.path.basename(filepath),
#                                    ela_image=ela_image,
#                                    credibility_score=credibility_score,
#                                    verified_count=verified_count,
#                                    is_suspicious=is_suspicious,
#                                    takedown_request=takedown_request,
#                                    report_file=report_filename)
        
#         except Exception as e:
#             return f"An error occurred: {e}"

#     return "File type not allowed"

# @app.route('/download/<filename>')
# def download_report(filename):
#     """Route to download the verification report."""
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# if __name__ == '__main__':
#     app.run(debug=True)
import os
import pytesseract
import urllib.parse
from PIL import Image, ImageChops
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from google_images_search import GoogleImagesSearch
import random

# Load environment variables from the .env file
load_dotenv()

# Set the path to the Tesseract executable for OCR
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD_PATH')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# List of verified sources for credibility scoring
VERIFIED_SOURCES = [
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "nytimes.com",
    "washingtonpost.com",
    "thehindu.com"
]

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_exif_data(image_path):
    """Extracts EXIF metadata from an image."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            return {k: str(v) for k, v in exif_data.items()}
    except Exception as e:
        print(f"EXIF data not found or error: {e}")
    return {}

def perform_ocr(image_path):
    """Performs Optical Character Recognition on the image."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except Exception as e:
        print(f"OCR failed: {e}")
        return "No text found or OCR error."

def perform_ela(image_path):
    """Performs Error Level Analysis (ELA) on an image."""
    try:
        ela_path = os.path.join(app.config['UPLOAD_FOLDER'], 'ela_' + os.path.basename(image_path))
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_ela.jpg')

        original_image = Image.open(image_path).convert('RGB')
        
        original_image.save(temp_path, 'JPEG', quality=95)
        
        temp_image = Image.open(temp_path)
        ela_image = ImageChops.difference(original_image, temp_image)
        
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        
        if max_diff == 0:
            scale = 0
        else:
            scale = 255.0 / max_diff
        
        ela_image = ela_image.point(lambda i: i * scale)
        ela_image.save(ela_path)
        os.remove(temp_path)
        
        return os.path.basename(ela_path)
    
    except Exception as e:
        print(f"ELA failed: {e}")
        return None

def perform_reverse_search_with_api(image_path):
    """Performs a reverse image search using Google Images Search API."""
    try:
        gis = GoogleImagesSearch(os.getenv('GOOGLE_API_KEY'), os.getenv('GOOGLE_CX'))
        
        _search_params = {
            'q': 'similar images',
            'file_path': image_path
        }
        
        gis.search(search_params=_search_params)
        
        results = []
        for image in gis.results():
            results.append({'title': image.title, 'url': image.url})
        
        return results

    except Exception as e:
        print(f"Google Images Search API failed: {e}")
        return []

def calculate_credibility(search_results):
    """Calculates a random credibility score for demo purposes."""
    verified_count = 0
    total_results = len(search_results)
    
    for result in search_results:
        try:
            domain = urllib.parse.urlparse(result['url']).netloc
            domain = domain.replace('www.', '')
            
            if domain in VERIFIED_SOURCES:
                verified_count += 1
        except:
            continue

    if total_results == 0:
        return 0, 0
        
    credibility_score = random.uniform(50, 100)
    
    return credibility_score, verified_count

def is_image_suspicious(filename, ela_image_path):
    """
    Checks if an image is suspicious based on ELA and filename flags.
    For demo purposes.
    """
    if "ai-gen" in filename.lower() or "deepfake" in filename.lower():
        return True
    
    # You can also add more advanced checks here based on ELA results
    return False

def generate_takedown_request(platform_name, image_url):
    """
    Generates a pre-drafted takedown request email.
    """
    subject = f"Takedown Request: Unauthorized use of deepfake image"
    
    body = f"""Dear {platform_name} Trust & Safety Team,

I am writing to formally request the immediate removal of a deepfake image that has been unlawfully posted and is causing significant harm. The image is a falsified representation of me, created using AI technology.

The URL of the infringing content is:
{image_url}

This image constitutes a deepfake and is a violation of your platform's policy against abusive or manipulated content. I have not consented to the creation or distribution of this image. Its continued presence is causing severe reputational damage and emotional distress.

I kindly request that you take down this content without delay. I can provide any additional information needed to verify my identity.

Thank you for your prompt attention to this matter.

Sincerely,
[Your Name]
[Your Contact Information]
"""
    return {"subject": subject, "body": body}


def generate_report(exif_data, ocr_text, search_results, credibility_score, verified_count, is_suspicious, takedown_request):
    """Generates a text report with all the findings."""
    report_content = "--- Image Verification Report ---\n\n"
    
    report_content += f"Suspicious Content Detected: {'Yes' if is_suspicious else 'No'}\n\n"
    
    report_content += "1. Image Metadata (EXIF)\n"
    if exif_data:
        for key, value in exif_data.items():
            report_content += f"  - {key}: {value}\n"
    else:
        report_content += "  - No EXIF data found.\n"
        
    report_content += "\n2. OCR Text\n"
    report_content += f"  - {ocr_text}\n"
    
    report_content += f"\n3. Credibility Score: {credibility_score:.2f}%\n"
    report_content += f"  - Found on {verified_count} verified source(s).\n"
    
    report_content += f"\n4. Reverse Search Results ({len(search_results)} found)\n"
    if search_results:
        for i, result in enumerate(search_results):
            report_content += f"  - {i+1}. {result['title']}\n"
            report_content += f"     URL: {result['url']}\n"
    else:
        report_content += "  - No reverse search results found.\n"
    
    if is_suspicious:
        report_content += "\n5. Takedown Request Draft\n"
        report_content += f"  - Subject: {takedown_request['subject']}\n"
        report_content += f"  - Body:\n{takedown_request['body']}"
        
    return report_content

# --- Main Flask Routes ---

@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles the file upload and initiates the OSINT tasks."""
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)

            # Perform all OSINT tasks
            exif_data = get_exif_data(filepath)
            ocr_text = perform_ocr(filepath)
            reverse_search_results = perform_reverse_search_with_api(filepath)
            ela_image = perform_ela(filepath)
            
            credibility_score, verified_count = calculate_credibility(reverse_search_results)
            
            is_suspicious = is_image_suspicious(filename, ela_image)
            takedown_request = None
            if is_suspicious:
                takedown_request = generate_takedown_request("Platform Name", "Image URL Placeholder")
            
            report_content = generate_report(exif_data, ocr_text, reverse_search_results, credibility_score, verified_count, is_suspicious, takedown_request)
            report_filename = secure_filename(f"report_{os.path.basename(filepath)}.txt")
            report_path = os.path.join(app.config['UPLOAD_FOLDER'], report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return render_template('result.html', 
                                   exif_data=exif_data, 
                                   ocr_text=ocr_text, 
                                   reverse_search_results=reverse_search_results,
                                   uploaded_image=os.path.basename(filepath),
                                   ela_image=ela_image,
                                   credibility_score=credibility_score,
                                   verified_count=verified_count,
                                   is_suspicious=is_suspicious,
                                   takedown_request=takedown_request,
                                   report_file=report_filename)
        
        except Exception as e:
            return f"An error occurred: {e}"

    return "File type not allowed"

@app.route('/download/<filename>')
def download_report(filename):
    """Route to download the verification report."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Deployment ke liye, host aur port environment variables ka use karein
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)